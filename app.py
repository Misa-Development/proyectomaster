import flet as ft
from views.historialpagos import vista_historial_pagos
from views.dashboard import vista_dashboard
from views.configuraciones import vista_configuraciones

def main(page):
    page.title = "Gestión de Gimnasio"

    def cambiar_vista(route):
        page.controls.clear()
        if route == "/":
            vista_dashboard(page)  # Carga el Dashboard
        elif route == "/configuraciones":
            vista_configuraciones(page)  # Carga Configuraciones
        elif route == "/historial_pagos":
            vista_historial_pagos(page)  # Carga Historial de Pagos
        else:
            page.add(ft.Text("Página no encontrada", size=24, weight="bold"))
        page.update()

    page.on_route_change = lambda e: cambiar_vista(page.route)
    page.go("/")  # Establecer ruta predeterminada

ft.app(target=main)