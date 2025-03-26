import flet as ft
from views.historialpagos import vista_historial_pagos
from views.add_client import vista_add_client
from views.dashboard import vista_dashboard
from views.configuraciones import vista_configuraciones
from database.db import crear_tablas

crear_tablas()
def main(page: ft.Page):
    page.title = "Gestión de Gimnasio"
    page.window_maximized = True

    # Función para cambiar vistas según la ruta
    def cambiar_vista(route):
        page.controls.clear()  # Limpia los controles existentes
        vistas = {
            "/": vista_dashboard,
            "/add_client": vista_add_client,
            "/configuraciones": vista_configuraciones,
            "/historial_pagos": vista_historial_pagos,
        }
        if route in vistas:
            vistas[route](page)  # Carga la vista correspondiente
        else:
            page.add(ft.Text("Página no encontrada", size=24, weight="bold"))
        page.update()  # Actualiza la página para reflejar los cambios

    # Manejo de cambios de ruta
    page.on_route_change = lambda e: cambiar_vista(page.route)

    # Ruta inicial
    page.go("/")  # Establece la vista inicial como el Dashboard

# Inicializa la aplicación
ft.app(target=main)