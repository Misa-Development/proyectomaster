import flet as ft
from views.dashboard import vista_dashboard
from views.configuraciones import vista_configuraciones
from database.db import crear_tablas, insertar_clientes

def main(page):
    # Inicializa la base de datos antes de cualquier interacción
    crear_tablas()
    insertar_clientes()

    page.title = "Gestor de Gimnasio"
    page.icon = "https://img.icons8.com/ios/452/dumbbell.png"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    
    # Función para manejar la navegación
    def cambiar_vista(route):
        page.controls.clear()
        if route == "/configuraciones":
            vista_configuraciones(page)
        else:  # Default to dashboard
            vista_dashboard(page)
        page.update()

    # Configura las rutas de las vistas
    page.on_route_change = lambda e: cambiar_vista(page.route)
    cambiar_vista(page.route)

ft.app(target=main)