import flet as ft
import json
from database.db import obtener_historial_movimientos, conectar_db
from views.Menu import vista_menu
from views.tablamovimentos import HistorialMovimientosTable
import datetime  # Import datetime
from views.custom_date_picker import open_custom_date_picker_modal  # Import the custom date picker

CONFIG_FILE = "config.json"

def cargar_configuracion():
    """Carga configuración desde un archivo JSON."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "color_fondo": "#FFFFFF",
            "color_tematica": "#FFFFFF",
            "color_letras": "#000000",
        }

def vista_historial_movimientos(page):
    print("[DEBUG] Refrescando vista_historial_movimientos con scale:", getattr(page, "global_scale", None))
    # Guarda el diálogo actual si existe
    current_dialog = getattr(page, "historial_dialog", None)

    # Limpiar la página antes de agregar la nueva vista
    page.controls.clear()
    page.update()

    config = cargar_configuracion()
    color_letras = config["color_letras"]
    color_fondo = config.get("color_fondo", "#FFFFFF")  # Default to white if not set
    color_tematica = config.get("color_tematica", "#E8E8E8")
    scale = getattr(page, "global_scale", 5.0)

    # Validar valores de escala para evitar errores de tamaño
    min_size = max(1, int(14*scale))
    min_row = max(1, int(10*scale))
    min_title = max(1, int(24*scale))
    min_spacing = max(1, int(20*scale))
    print(f"[DEBUG] scale={scale}, min_size={min_size}, min_row={min_row}, min_title={min_title}, min_spacing={min_spacing}")

    # Permitir refresco en tiempo real desde el menú
    def rebuild():
        vista_historial_movimientos(page)
    page.rebuild_vista_actual = rebuild

    menu = vista_menu(page)  # Asegúrate de que el menú también use el scale actualizado

    # Initialize filters
    filtro_tipo = ft.Dropdown(
        label="Filtrar por Tipo",
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Alta"),
            ft.dropdown.Option("Baja"),
            ft.dropdown.Option("Modificación"),
            ft.dropdown.Option("Renovación"),
        ],
        value="Todos",
        text_style=ft.TextStyle(color=color_letras, size=min_size),        
        label_style=ft.TextStyle(color=color_letras, size=min_size),
        bgcolor=color_tematica,
        border_color=color_tematica,
        width=max(50, int(200*scale)),
    )

    fecha_seleccionada = ft.Ref[ft.TextField]()

    def open_date_picker(e):
        def on_date_selected(selected_date):
            fecha_seleccionada.current.value = selected_date.strftime("%Y-%m-%d")
            filtrar_movimientos()
            page.update()

        overlay = open_custom_date_picker_modal(page, datetime.date.today(), on_date_selected)
        page.overlay.append(overlay)
        page.update()

    filtro_fecha = ft.TextField(
        ref=fecha_seleccionada,
        label="Filtrar por Fecha (YYYY-MM-DD)",
        label_style=ft.TextStyle(color=color_letras, size=min_size),
        text_style=ft.TextStyle(color=color_fondo, size=min_size),
        border_color=color_tematica,
        width=max(50, int(200*scale)),
        read_only=True,
        on_click=open_date_picker,  # Open date picker on click
    )

    # Create an instance of the table
    try:
        tabla_historial = HistorialMovimientosTable(
            page=page,
            color_letras=color_letras,
            color_tematica=color_tematica,
            color_fondo=color_fondo,
            scale=scale
        )
    except Exception as ex:
        import traceback
        print(f"[DEBUG] Error creando HistorialMovimientosTable: {ex}")
        traceback.print_exc()
        tabla_historial = None

    # Filter function
    def filtrar_movimientos(e=None):
        tipo = filtro_tipo.value
        fecha = fecha_seleccionada.current.value.strip()
        tabla_historial.filtrar_movimientos(tipo, fecha)
        page.update()

    # Update function
    def actualizar_historial(e=None):
        tabla_historial.update_data()
        fecha_seleccionada.current.value = ""  # Clear the date field
        page.update()

    # Assign events
    filtro_tipo.on_change = lambda e: filtrar_movimientos()

    vista = ft.Column(
        controls=[
            menu,
            ft.Text("📜 Historial de Movimientos", size=min_title, weight="bold", color=color_letras),
            ft.Row([filtro_tipo, filtro_fecha, ft.ElevatedButton(text="Actualizar", on_click=actualizar_historial, color="black", bgcolor=color_tematica, style=ft.ButtonStyle(text_style=ft.TextStyle(size=min_size)))], spacing=min_row),
            tabla_historial.get_widget() if tabla_historial else ft.Text("[ERROR] No se pudo crear la tabla de historial", color="red"),
            current_dialog if current_dialog else ft.Container()  # Agrega el diálogo al layout
        ],
        spacing=min_spacing
    )
    if tabla_historial:
        tabla_historial.update_data()

    if current_dialog:
        page.dialog = current_dialog
        page.update()

    # Al final de la función, para debug visual:
    print("[DEBUG] Vista historial de movimientos reconstruida correctamente.")
    return vista

if __name__ == "__main__":
    def main(page: ft.Page):
        vista_historial_movimientos(page)

    ft.app(target=main)