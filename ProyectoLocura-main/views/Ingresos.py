import flet as ft
import json
from views.Menu import vista_menu
from views.ingresosfiltros import filtros_ingresos
from views.ingresostablas import tabla_ingresos
from views.ingresopago import panel_ingreso_pago

CONFIG_FILE = "config.json"

def cargar_configuracion():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "color_fondo": "#CF3434",
            "color_tematica": "#E8E8E8",
            "color_letras": "#000000",
            "nombre_gimnasio": "Mi Gimnasio"
        }

def vista_historial_pagos(page: ft.Page):
    config = cargar_configuracion()
    color_fondo = config["color_fondo"]
    color_letras = config["color_letras"]
    color_tematica = config["color_tematica"]
    
    page.title = "Historial de Pagos y Gestión de Ingresos"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT

    menu = vista_menu(page)
    tabla = tabla_ingresos()
    filtros = filtros_ingresos(page, tabla, color_letras, color_tematica)

    # Estado para mostrar/ocultar el panel
    panel_visible = False

    def set_panel_visible(valor):
        nonlocal panel_visible
        panel_visible = valor
        panel_control.offset = ft.Offset(0, 0) if panel_visible else ft.Offset(1, 0)
        page.update()

    def abrir_panel(e):
        set_panel_visible(True)

    def cerrar_panel(e):
        set_panel_visible(False)

    def get_boton_panel():
        return ft.ElevatedButton(
            text="Cerrar ingreso" if panel_visible else "Insertar ingreso",
            icon=ft.Icons.CLOSE if panel_visible else ft.Icons.ADD,
            on_click=cerrar_panel if panel_visible else abrir_panel,
            style=ft.ButtonStyle(
                bgcolor="red" if panel_visible else color_tematica,
                color="white" if panel_visible else "black"
            )
        )

    # Panel lateral inicializado con offset fuera de pantalla
    panel_control = panel_ingreso_pago(page, tabla, color_letras, color_fondo, color_tematica, panel_visible, set_panel_visible)

    contenido = ft.Column(
        controls=[
            menu,
            filtros,
            ft.Row(
                [
                    ft.Container(expand=6),
                    get_boton_panel(),
                    ft.Container(expand=1),
                ]
            ),
            ft.Row(
                controls=[
                    tabla,
                    ft.Container(
                        content=ft.VerticalDivider(width=1, thickness=2, color=color_tematica),
                        height=500  # Ajusta este valor según la altura de tu tabla
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Divider(height=1, thickness=2, color=color_tematica),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
    )

    stack = ft.Stack(
        controls=[
            contenido,
            panel_control
        ]
    )
    return stack