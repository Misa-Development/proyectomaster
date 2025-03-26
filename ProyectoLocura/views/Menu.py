import flet as ft

def vista_menu(page):
    # Define las opciones del menú
    menu_items = [
        ft.PopupMenuItem(text="Dashboard", on_click=lambda e: page.go("/")),
        ft.PopupMenuItem(text="Agregar Clientes", on_click=lambda e: page.go("/add_client")),
        ft.PopupMenuItem(text="Configuraciones", on_click=lambda e: page.go("/configuraciones")),
        ft.PopupMenuItem(text="Historial de Pagos", on_click=lambda e: page.go("/historial_pagos")),
    ]

    # Crea el menú desplegable
    menu = ft.PopupMenuButton(icon=ft.icons.MENU, items=menu_items)

    # Contenedor para posicionar el menú en la esquina superior izquierda
    return ft.Container(
        content=menu,
        padding=ft.padding.all(1),
        alignment=ft.alignment.top_left,
    )