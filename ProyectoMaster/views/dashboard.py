import flet as ft
import json
import sqlite3
from views.Menu import vista_menu
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
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nombre, apellido, sexo, edad, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento 
            FROM clientes
        ''')
        clientes = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error al obtener clientes: {e}")
        clientes = []
    finally:
        if conn:
            conn.close()
    return clientes

# Vista principal del Dashboard
def vista_dashboard(page):
    # Cargar configuración
    page.scroll = "none"  # Desactivar el scroll en el dashboard
    page.clean()
    configuracion = cargar_configuracion()
    color_fondo = configuracion.get("color_fondo", "#FFFFFF")
    color_letras = configuracion.get("color_letras", "#000000")
    color_tematica = configuracion.get("color_tematica", "#FF5733")
    nombre_gimnasio = configuracion.get("nombre_gimnasio", "Mi Gimnasio")
    clientes = obtener_clientes()

    page.bgcolor = color_fondo
    page.window_maximized = True

    # Encabezado
    menu = vista_menu(page)
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(nombre_gimnasio, size=36, weight="bold", color=color_letras),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=20,
        bgcolor=color_tematica,
        border_radius=10,
    )

    # Tarjetas de métricas rápidas
    metric_cards = ft.Row(
        controls=[
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Clientes Activos", size=18, weight="bold", color=color_letras),
                            ft.Text("125", size=42, weight="bold", color=color_letras),
                            ft.Icon(ft.Icons.GROUP, size=18, color=color_letras),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.Colors.BLUE,
                    padding=17
                    ,
                    border_radius=10,
                    width=270,
                    height=150,
                    border=ft.border.all(  # Define el color del borde
                        color="#172963",
                        width=2,  # Grosor del borde
                    ),

                ),
                elevation=5,
                shadow_color=ft.Colors.BLUE,
                margin=ft.margin.all(10),
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Próximas Renovaciones", size=18, weight="bold", color=color_letras),
                            ft.Text("20", size=42, weight="bold", color=color_letras),
                            ft.Icon(ft.Icons.UPDATE, size=18, color=color_letras),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor=ft.Colors.GREEN,
                    padding=17,
                    border_radius=10,
                    width=270,
                    height=150,
                    border=ft.border.all(  # Define el color del borde
                        color="#2e6317",
                        width=2,  # Grosor del borde
                    ),
                    
                ),
                elevation=5,
                shadow_color=ft.Colors.GREEN,
                margin=ft.margin.all(10),
            ),
        ],
        spacing=25,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Panel lateral dinámico (inicia cerrado)
    cliente_panel = ft.Container(
        content=None,
        bgcolor=ft.Colors.with_opacity(0.95,color=color_fondo),
        padding=20,
        border_radius=15,
        alignment=ft.alignment.center_right,
        border=ft.border.all(2,color=color_letras,
),
        width=0,  # Inicialmente cerrado
        animate_size=True,# Transiciones suaves
        animate=ft.Animation(duration=300, curve=ft.AnimationCurve.EASE_IN_OUT),
    )

    def actualizar_lista_clientes():
        print("🔄 Actualizando lista de clientes...")
        page.clean()  # Limpia la página antes de regenerar el contenido
        vista_dashboard(page)  # Recarga la vista del dashboard

    def mostrar_detalles_cliente(cliente):
        cliente_panel.margin = 30
        cliente_panel.width = 350  # Ancho fijo
        cliente_panel.content = vista_detalles_cliente(cliente, color_letras, color_tematica, cliente_panel, actualizar_lista_clientes)
        cliente_panel.update()
    # Tabla de clientes
    tabla_clientes = vista_tabla_clientes(page, mostrar_detalles_cliente, color_letras, color_tematica)

    # Filtros de búsqueda
    filtros = vista_filtros(
        page,
        color_letras,
        open_custom_date_picker_modal,
        tabla_clientes,
        clientes,
        mostrar_detalles_cliente,
    )



    # Layout principal
    layout = ft.Row(
        controls=[
            ft.Container(  # Contenido principal
                content=ft.Column(
                    controls=[
                        menu,
                        header,
                        metric_cards,
                        filtros,
                        tabla_clientes,
                    ],
                    expand=True,  # Ajusta al espacio disponible
                ),
                expand=True,  # Este contenedor es flexible
            ),
            cliente_panel,  # Panel lateral dinámico
        ],
        spacing=0,
        expand=True,
    )

    # Añadir layout a la página
    page.add(layout)
    page.update()