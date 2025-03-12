# views/Menu.py
import flet as ft

def vista_menu(page):
    # Define las opciones del menú
    menu_items = [
        ft.PopupMenuItem(text="Dashboard", on_click=lambda e: page.go("/")),
        ft.PopupMenuItem(text="Configuraciones", on_click=lambda e: page.go("/configuraciones")),
    ]

    # Crea el menú desplegable
    menu = ft.PopupMenuButton(
        icon=ft.icons.MENU,
        items=menu_items
    )

    # Contenedor para posicionar el menú en la esquina superior izquierda
    contenedor_menu = ft.Container(
        content=menu,
        padding=ft.padding.all(10),
        alignment=ft.alignment.top_left
    )

    return contenedor_menu
