import flet as ft
import asyncio  # Para manejar la pausa entre opacidad y cambio de ruta

def vista_menu(page):
    async def navegar_con_efecto(ruta):
        """
        Simula una transición al cambiar la ruta con un efecto de desvanecimiento usando asyncio.
        """
        # Reduce la opacidad para el efecto de transición
        if len(page.views) > 0:
            page.views[-1].opacity = 0
            page.update()
        
        # Espera 200 ms antes de cambiar de vista
        await asyncio.sleep(0.2)

        # Cambia la ruta
        page.go(ruta)

        # Restaura la opacidad al 100% para la nueva vista
        if len(page.views) > 0:
            page.views[-1].opacity = 1
            page.update()

    # Define las opciones del menú con la navegación con efecto
    menu_items = [
        ft.PopupMenuItem(text="Dashboard", on_click=lambda e: asyncio.run(navegar_con_efecto("/"))),
        ft.PopupMenuItem(text="Agregar Clientes", on_click=lambda e: asyncio.run(navegar_con_efecto("/add_client"))),
        ft.PopupMenuItem(text="Configuraciones", on_click=lambda e: asyncio.run(navegar_con_efecto("/configuraciones"))),
        ft.PopupMenuItem(text="Historial de Pagos", on_click=lambda e: asyncio.run(navegar_con_efecto("/historial_pagos"))),
        ft.PopupMenuItem(text="Stock", on_click=lambda e: asyncio.run(navegar_con_efecto("/Stock"))),
    ]

    # Crea el menú desplegable
    menu = ft.PopupMenuButton(icon=ft.Icons.MENU, items=menu_items)

    # Contenedor para posicionar el menú en la esquina superior izquierda
    return ft.Container(
        content=menu,
        padding=ft.padding.all(1),
        alignment=ft.alignment.top_left,
    )