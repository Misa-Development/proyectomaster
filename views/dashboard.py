import flet as ft
import json
import sqlite3
from views.Menu import vista_menu
from views.add_client import vista_add_client
from views.tablacliente import vista_tabla_clientes
from views.verdetalle import vista_detalles_cliente
from views.filtros import vista_filtros, open_custom_date_picker_modal
from database.db import conectar_db

# Función para cargar configuración desde config.json
def cargar_configuracion():
    with open("config.json", "r") as config_file:
        return json.load(config_file)

# Función para obtener la lista de clientes desde la base de datos
def obtener_clientes():
    try:
        conn = conectar_db()
        conn.row_factory = sqlite3.Row  # Convertir resultados a objetos tipo Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nombre, apellido, sexo, edad, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento 
            FROM clientes
        ''')
        # Convertir cada fila a un diccionario explícitamente
        clientes = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error al obtener clientes: {e}")
        clientes = []  # Retornar lista vacía en caso de error
    finally:
        if conn:
            conn.close()
    return clientes
def vista_dashboard(page):
    # Cargar configuración del archivo JSON
    configuracion = cargar_configuracion()

    # Configuración de colores y tema
    color_fondo = configuracion.get("color_fondo", "#FFFFFF")
    color_letras = configuracion.get("color_letras", "#000000")
    color_tematica = configuracion.get("color_tematica", "#FF5733")
    nombre_gimnasio = configuracion.get("nombre_gimnasio", "Mi Gimnasio")

    # Obtener la lista de clientes
    clientes = obtener_clientes()

    # Aplicar fondo y maximizar ventana
    page.bgcolor = color_fondo
    page.window_maximized = True

    # Crear el encabezado con el nombre del gimnasio
    menu = vista_menu(page)
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(nombre_gimnasio, size=36, weight="bold", color=color_letras),
                ft.IconButton(icon=ft.icons.SETTINGS, tooltip="Configuraciones", icon_color=color_tematica),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=20,
        bgcolor=color_tematica,
        border_radius=10,
    )

    # Tarjetas con métricas rápidas
    metric_cards = ft.Row(
        controls=[
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Clientes Activos", size=18, weight="bold", color=color_letras),
                            ft.Text("125", size=42, weight="bold", color=color_tematica),
                            ft.Icon(ft.icons.GROUP, size=28, color=color_tematica),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.colors.BLUE,
                    padding=5,
                    border_radius=20,
                    width=270,
                    height=150,
                ),
                elevation=5,
                margin=ft.margin.all(10),
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Próximas Renovaciones", size=18, weight="bold", color=color_letras),
                            ft.Text("20", size=42, weight="bold", color=color_tematica),
                            ft.Icon(ft.icons.UPDATE, size=28, color=color_tematica),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.colors.GREEN,
                    padding=5,
                    border_radius=20,
                    width=270,
                    height=150,
                ),
                elevation=5,
                margin=ft.margin.all(10),
            ),
        ],
        spacing=25,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Panel lateral para detalles del cliente
    cliente_panel = ft.Container(
        content=None,  # Inicialmente vacío
        bgcolor=ft.colors.with_opacity(0.95, ft.colors.BLACK),
        padding=20,
        border_radius=15,
        alignment=ft.alignment.center_left,
        border=ft.border.all(2, ft.colors.WHITE),
        width=0,  # Empieza invisible
        animate_size=True,
    )

    # Función para mostrar detalles de un cliente
    def mostrar_detalles_cliente(cliente):
        print(f"Mostrando detalles para: {cliente}")  # Log de depuración
        cliente_panel.content = vista_detalles_cliente(cliente, color_letras, color_tematica, cliente_panel)
        cliente_panel.width = 350  # Ajustar tamaño del panel
        cliente_panel.update()
        print("Panel actualizado y visible")

    # Crear la tabla de clientes
    tabla_clientes = vista_tabla_clientes(page, mostrar_detalles_cliente, color_letras, color_tematica)

    # Crear los filtros utilizando los clientes
    filtros = vista_filtros(
        page,
        color_letras,
        open_custom_date_picker_modal,
        tabla_clientes,
        clientes,  # Se pasa la lista de clientes aquí
    )

    # Función para ir a la vista de agregar clientes
    def ir_a_agregar_cliente(e):
        page.clean()  # Limpia la vista actual
        vista_add_client(page)

    # Botón para agregar clientes
    btn_agregar_cliente = ft.ElevatedButton(
        text="Agregar Cliente",
        icon=ft.icons.PERSON_ADD,
        style=ft.ButtonStyle(bgcolor=color_tematica, color=ft.colors.WHITE),
        on_click=ir_a_agregar_cliente,
    )

    # Layout principal
    layout = ft.Column(
        controls=[
            menu,
            header,
            metric_cards,
            filtros,
            btn_agregar_cliente,
            tabla_clientes,
            cliente_panel,
        ],
        spacing=20,
        scroll="auto",
    )

    page.add(layout)
    page.update()