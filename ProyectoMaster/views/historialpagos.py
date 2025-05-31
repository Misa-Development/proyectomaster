import flet as ft
import json
import sys
import os
from views.custom_date_picker import open_custom_date_picker_modal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Asegurar acceso al módulo 'database'
from database.db import insertar_ingreso
from views.Menu import vista_menu
from views.filtrosingresos import filtros_ingresos  # Importar los filtros
from views.tablasingresos import tabla_ingresos  # Importar la tabla de ingresos

# Ruta del archivo de configuración
CONFIG_FILE = "config.json"

def cargar_configuracion():
    """
    Cargar configuración desde un archivo JSON. Retorna un diccionario con valores por defecto si no se encuentra el archivo.
    """
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "color_fondo": "#FFFFFF",
            "color_tematica": "#E8E8E8",
            "color_letras": "#000000",
            "nombre_gimnasio": "Mi Gimnasio"
        }


def vista_historial_pagos(page: ft.Page):
    """
    Vista principal para gestionar el historial de pagos e ingresos.
    """
    # Cargar configuración desde el archivo JSON
    config = cargar_configuracion()
    color_letras = config["color_letras"]

    # Configuración general de la página
    page.title = "Historial de Pagos y Gestión de Ingresos"
    page.scroll = "auto"  # Habilitar scroll en la página
    page.theme_mode = ft.ThemeMode.LIGHT

    # Agregar el menú superior
    menu = vista_menu(page)

    # Inputs para agregar un ingreso
    input_articulo = ft.TextField(
        label="Artículo",
        width=200,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        label_style=ft.TextStyle(color=color_letras),
    )
    input_fecha = ft.TextField(
        label="Fecha (DD/MM/AAAA)",
        width=150,
        read_only=True,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        label_style=ft.TextStyle(color=color_letras),
    )  # Campo de fecha solo lectura
    input_monto = ft.TextField(
        label="Monto",
        width=150,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        label_style=ft.TextStyle(color=color_letras),
    )
    input_cliente = ft.TextField(
        label="Cliente",
        width=200,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        label_style=ft.TextStyle(color=color_letras),
    )
    input_metodo_pago = ft.TextField(
        label="Método de Pago",
        width=150,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        label_style=ft.TextStyle(color=color_letras),
    )  # Nuevo campo para el método de pago

    # Tabla y filtros
    tabla = tabla_ingresos()
    filtros = filtros_ingresos(page, tabla, color_letras)

    # Función para abrir el selector de fecha
    def abrir_selector_fecha(e):
        def on_date_selected(selected_date):
            # Actualizar el campo de fecha con la fecha seleccionada
            input_fecha.value = selected_date.strftime("%Y-%m-%d")
            page.overlay.clear()
            page.update()

        # Agregar el modal del selector de fecha
        modal = open_custom_date_picker_modal(page, initial_date=None, on_date_selected=on_date_selected)
        page.overlay.append(modal)
        page.update()

    # Añadir acción para abrir el modal al hacer clic en el campo de fecha
    input_fecha.on_focus = abrir_selector_fecha

    def agregar_ingreso(e):
        articulo = input_articulo.value
        monto = input_monto.value
        cliente = input_cliente.value
        fecha = input_fecha.value
        metodo_pago = input_metodo_pago.value or "Efectivo"  # Valor por defecto si está vacío

        if not all([articulo, monto, cliente, fecha, metodo_pago]):
            page.snack_bar = ft.SnackBar(content=ft.Text("Por favor, completa todos los campos antes de agregar el ingreso."))
            page.snack_bar.open = True
            return

        try:
            insertar_ingreso(articulo, float(monto), fecha, cliente, metodo_pago)
            input_articulo.value = ""
            input_fecha.value = ""
            input_monto.value = ""
            input_cliente.value = ""
            input_metodo_pago.value = ""
            page.snack_bar = ft.SnackBar(content=ft.Text("Ingreso agregado exitosamente."))
            page.snack_bar.open = True
            tabla.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(articulo, color=color_letras)),
                ft.DataCell(ft.Text(f"${float(monto):.2f}", color=color_letras)),
                ft.DataCell(ft.Text(fecha, color=color_letras)),
                ft.DataCell(ft.Text(cliente, color=color_letras)),
                ft.DataCell(ft.Text(metodo_pago, color=color_letras)),  # Nueva celda dinámica para la columna
            ]))
            page.update()
        except ValueError:
            page.snack_bar = ft.SnackBar(content=ft.Text("El monto debe ser un número válido."))
            page.snack_bar.open = True

    boton_agregar_ingreso = ft.ElevatedButton(
        text="Agregar ingreso",
        on_click=agregar_ingreso,
        bgcolor=ft.Colors.BLUE,  # Fondo azul
        color=ft.Colors.WHITE,   # Texto blanco
    )

    # Sección de filtros y formulario
    layout_filtros_prompts = ft.Column(
        controls=[
            ft.Text("Gestión de Historial e Ingresos", size=28, weight="bold", color=color_letras),
            ft.Row([filtros], spacing=10),
            ft.Text("Insertar Ingreso", size=20, weight="bold", color=color_letras),
            ft.Row([input_articulo, input_fecha, input_monto, input_cliente, input_metodo_pago, boton_agregar_ingreso], spacing=10),
        ],
        spacing=20,
    )

    # Layout principal de la vista
    contenido = ft.Column(
        controls=[
            menu,  # Menú superior integrado
            layout_filtros_prompts,
            tabla,
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
    )

    # Agregar contenido a la página
    page.add(contenido)

if __name__ == "__main__":
    ft.app(target=vista_historial_pagos)