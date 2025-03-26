import flet as ft
import calendar
import datetime
import json

CONFIG_FILE = "config.json"

# Función para cargar y guardar configuración
def cargar_configuracion():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        config = {
            "color_fondo": "#FFFFFF",
            "color_tematica": "#E8E8E8",
            "color_letras": "#000000",
            "nombre_gimnasio": "Mi Gimnasio",
        }
        guardar_configuracion(config)
        return config

def guardar_configuracion(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Modal para seleccionar fechas
def open_custom_date_picker_modal(page, initial_date, on_date_selected):
    configuracion = cargar_configuracion()

    if initial_date is None:
        initial_date = datetime.date.today()
    state = {"year": initial_date.year, "month": initial_date.month}

    # Función para construir el calendario dinámico
    def build_calendar(year, month):
        month_matrix = calendar.monthcalendar(year, month)
        rows = []
        days_header = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        header_row = ft.Row(
            [ft.Text(day, weight="bold", width=40, text_align=ft.TextAlign.CENTER, color=configuracion["color_letras"]) for day in days_header],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        rows.append(header_row)

        for week in month_matrix:
            btns = []
            for day in week:
                if day == 0:  # Día vacío
                    btns.append(ft.Text(" ", width=40))
                else:
                    d = datetime.date(year, month, day)
                    btn = ft.TextButton(
                        text=str(day),
                        width=40,
                        on_click=lambda e, d=d: on_date_selected(d),
                        style=ft.ButtonStyle(bgcolor=configuracion["color_tematica"], color=configuracion["color_letras"]),
                    )
                    btns.append(btn)
            rows.append(ft.Row(btns, alignment=ft.MainAxisAlignment.CENTER))
        return ft.Column(rows, spacing=2)

    # Función para reconstruir el modal con el calendario actualizado
    def rebuild_modal():
        def prev_year(e):
            state["year"] -= 1
            rebuild_modal()
        def next_year(e):
            state["year"] += 1
            rebuild_modal()
        year_row = ft.Row(
            [
                ft.IconButton(icon=ft.icons.ARROW_LEFT, tooltip="Año anterior", on_click=prev_year),
                ft.Text(str(state["year"]), size=18, weight="bold", color=configuracion["color_letras"]),
                ft.IconButton(icon=ft.icons.ARROW_RIGHT, tooltip="Año siguiente", on_click=next_year),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        def prev_month(e):
            if state["month"] == 1:
                state["month"] = 12
                state["year"] -= 1
            else:
                state["month"] -= 1
            rebuild_modal()
        def next_month(e):
            if state["month"] == 12:
                state["month"] = 1
                state["year"] += 1
            else:
                state["month"] += 1
            rebuild_modal()
        month_row = ft.Row(
            [
                ft.IconButton(icon=ft.icons.ARROW_LEFT, tooltip="Mes anterior", on_click=prev_month),
                ft.Text(calendar.month_name[state["month"]], size=18, weight="bold", color=configuracion["color_letras"]),
                ft.IconButton(icon=ft.icons.ARROW_RIGHT, tooltip="Mes siguiente", on_click=next_month),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        calendar_grid = build_calendar(state["year"], state["month"])

        def close_modal(e):
            if overlay in page.overlay:
                page.overlay.remove(overlay)
            page.update()
        cancel_row = ft.Row(
            [ft.TextButton("Cancelar", on_click=close_modal, style=ft.ButtonStyle(color=configuracion["color_letras"]))],
            alignment=ft.MainAxisAlignment.END,
        )

        modal_container.content = ft.Column(
            [year_row, month_row, calendar_grid, cancel_row],
            spacing=10,
        )
        page.update()

    # Configuración inicial del contenedor del modal
    modal_container = ft.Container(
        content=ft.Text(""),
        padding=10,
        bgcolor=configuracion["color_tematica"],
        border_radius=ft.BorderRadius(10, 10, 10, 10),
        width=350,
        height=400,
    )

    rebuild_modal()

    # Overlay para mostrar el modal
    overlay = ft.Container(
        content=modal_container,
        alignment=ft.alignment.center,
        expand=True,
        bgcolor=ft.colors.BLACK38,
    )
    return overlay