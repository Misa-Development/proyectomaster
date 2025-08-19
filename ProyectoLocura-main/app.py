import flet as ft
try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version
print("Flet version:", version("flet"))
from views.Ingresos import vista_historial_pagos
from views.add_client import vista_add_client
from views.dashboard import vista_dashboard
from views.configuraciones import vista_configuraciones
from views.Stock import vista_stock
from views.historial_movimientos import vista_historial_movimientos
from database.db import crear_tablas

# Crea las tablas de la base de datos al iniciar la aplicación
crear_tablas()


def main(page: ft.Page):
    # Título de la ventana
    page.title = "Gestión de Gimnasio"
    # Pantalla completa al iniciar
    page.window.full_screen = True
    # Maximiza la ventana al iniciar (opcional, pero no necesario si es full screen)
    page.window_maximized = True

    # Función para cambiar vistas según la ruta
    def cambiar_vista(route, *args, **kwargs):
        # Optimización: solo limpiar y actualizar si realmente cambia la vista
        if hasattr(page, "_last_route") and page._last_route == route:
            return
        page._last_route = route
        # Limpiar controles previos para evitar controles huérfanos
        if hasattr(page, "controls"):
            page.controls.clear()
        vistas = {
            "/": lambda p: vista_dashboard(p, *args, **kwargs),
            "/add_client": lambda p: vista_add_client(p, cambiar_vista=cambiar_vista, *args, **kwargs),
            "/configuraciones": lambda p: vista_configuraciones(p, *args, **kwargs),
            "/historial_movimientos": lambda p: vista_historial_movimientos(p, *args, **kwargs),
            "/historial_pagos": lambda p: vista_historial_pagos(p, *args, **kwargs),
            "/Stock": lambda p: vista_stock(p, cambiar_vista=cambiar_vista, *args, **kwargs),
        }
        control = vistas.get(route, lambda p: ft.Text("Página no encontrada", size=24, weight="bold"))(page)
        page.controls.append(control if control is not None else ft.Text("Error al cargar la vista", size=24, weight="bold", color="red"))
        page.update()

    # Manejo de cambios de ruta
    # Asigna la función cambiar_vista al evento on_route_change de la página
    page.on_route_change = lambda e: cambiar_vista(page.route)

    # Callback global para zoom/rebuild desde el menú
    page.rebuild_vista_actual = lambda: cambiar_vista(page.route)

    # Ruta inicial
    # Establece la vista inicial como el Dashboard
    page.go("/")

    def toggle_fullscreen(e):
        page.window.full_screen = not page.window.full_screen
        page.update()

    page.on_keyboard_event = lambda e: toggle_fullscreen(e) if e.key == "F11" else None


# Inicializa la aplicación
# Llama a la función ft.app y le pasa la función main como target
if __name__ == "__main__":
    ft.app(target=main)