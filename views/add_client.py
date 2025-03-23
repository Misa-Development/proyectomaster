import flet as ft
import calendar
import datetime
import json
import sqlite3
import sqlite3
from database.db import conectar_db
from database.db import crear_tablas, insertar_clientes  # Si usas estas funciones directamente
# Ruta del archivo de configuración
CONFIG_FILE = "config.json"

# Leer configuración desde archivo
def cargar_configuracion():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        config = {
            "color_fondo": "#FFFFFF",
            "color_tematica": "#E8E8E8",
            "color_letras": "#000000",
            "tema": "Light",
            "nombre_gimnasio": "Mi Gimnasio",
            "idioma": "Español"
        }
        guardar_configuracion(config)
        return config

# Guardar configuración en archivo
def guardar_configuracion(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Modal personalizado para seleccionar fechas
def open_custom_date_picker_modal(page, initial_date, on_date_selected):
    configuracion = cargar_configuracion()

    if initial_date is None:
        initial_date = datetime.date.today()
    state = {"year": initial_date.year, "month": initial_date.month}

    modal_container = ft.Container(
        content=ft.Text(""),
        padding=10,
        bgcolor=configuracion["color_tematica"],
        border_radius=ft.BorderRadius(10, 10, 10, 10),
        width=350,
        height=400,
    )

    def build_calendar(year, month):
        month_matrix = calendar.monthcalendar(year, month)
        rows = []
        days_header = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        header_row = ft.Row(
            [ft.Text(day, weight="bold", width=40, text_align=ft.TextAlign.CENTER, color=configuracion["color_letras"])
             for day in days_header],
            alignment=ft.MainAxisAlignment.CENTER
        )
        rows.append(header_row)

        for week in month_matrix:
            btns = []
            for day in week:
                if day == 0:
                    btns.append(ft.Text(" ", width=40))
                else:
                    d = datetime.date(year, month, day)
                    btn = ft.TextButton(
                        text=str(day),
                        width=40,
                        on_click=lambda e, d=d: on_date_selected(d),
                        style=ft.ButtonStyle(bgcolor=configuracion["color_tematica"], color=configuracion["color_letras"])
                    )
                    btns.append(btn)
            rows.append(ft.Row(btns, alignment=ft.MainAxisAlignment.CENTER))
        return ft.Column(rows, spacing=2)

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
            alignment=ft.MainAxisAlignment.CENTER
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
            alignment=ft.MainAxisAlignment.CENTER
        )

        calendar_grid = build_calendar(state["year"], state["month"])

        def close_modal(e):
            if overlay in page.overlay:
                page.overlay.remove(overlay)
            page.update()
        cancel_row = ft.Row(
            [ft.TextButton("Cancelar", on_click=close_modal, style=ft.ButtonStyle(color=configuracion["color_letras"]))],
            alignment=ft.MainAxisAlignment.END
        )

        modal_container.content = ft.Column(
            [year_row, month_row, calendar_grid, cancel_row],
            spacing=10
        )
        page.update()

    rebuild_modal()

    overlay = ft.Container(
        content=modal_container,
        alignment=ft.alignment.center,
        expand=True,
        bgcolor=ft.colors.BLACK38,
    )
    return overlay

# Vista agregar cliente
def vista_add_client(page):
    configuracion = cargar_configuracion()

    page.title = "Agregar Cliente"
    page.window_maximized = True
    page.bgcolor = configuracion["color_fondo"]

    def regresar_dashboard(e):
        page.clean()
        from views.dashboard import vista_dashboard
        vista_dashboard(page)
        page.update()

    btn_volver = ft.IconButton(
        icon=ft.icons.ARROW_BACK,
        tooltip="Volver al Dashboard",
        on_click=regresar_dashboard,
        style=ft.ButtonStyle(bgcolor=configuracion["color_tematica"], color=configuracion["color_letras"])
    )

    txt_name = ft.TextField(
        label="Nombre",
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"]
    )
    txt_surname = ft.TextField(
        label="Apellido",
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"]
    )
    txt_dni = ft.TextField(
        label="N° Documento",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"]
    )
    txt_age = ft.TextField(
        label="Edad",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"]
    )
    txt_email = ft.TextField(
        label="Email",
        keyboard_type=ft.KeyboardType.EMAIL,
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"]
    )
    dropdown_gender = ft.Dropdown(
        label="Seleccione el Sexo",
        options=[
            ft.dropdown.Option(key="Male", text="Masculino"),
            ft.dropdown.Option(key="Female", text="Femenino"),
            ft.dropdown.Option(key="Other", text="Otro"),
        ],
        value="",
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"]
    )
    txt_diseases = ft.TextField(
        label="Enfermedades",
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"]
    )
    switch_medical = ft.Switch(
    label="Apta Médica",
    value=False,
    active_color=configuracion["color_tematica"]
    )

    def show_date_picker(text_field):
        def on_date_selected(selected_date):
            text_field.value = selected_date.strftime("%d/%m/%Y")
            if overlay in page.overlay:
                page.overlay.remove(overlay)
            page.update()

        overlay = open_custom_date_picker_modal(page, None, on_date_selected)
        page.overlay.append(overlay)
        page.update()

    txt_membership_start = ft.TextField(
        label="Inicio de Membresía",
        read_only=True,
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"]
    )
    btn_pick_start = ft.IconButton(
        icon=ft.icons.CALENDAR_MONTH,
        tooltip="Seleccionar Fecha",
        on_click=lambda e: show_date_picker(txt_membership_start),
        style=ft.ButtonStyle(
            bgcolor=configuracion["color_tematica"],
            color=configuracion["color_letras"]
        )
    )
    txt_membership_end = ft.TextField(
        label="Vencimiento de Membresía",
        read_only=True,
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"]
    )
    btn_pick_end = ft.IconButton(
        icon=ft.icons.CALENDAR_MONTH,
        tooltip="Seleccionar Fecha",
        on_click=lambda e: show_date_picker(txt_membership_end),
        style=ft.ButtonStyle(
            bgcolor=configuracion["color_tematica"],
            color=configuracion["color_letras"]
        )
    )

    def submit_client(e):
        # Inicializar conexión
        conn = None

        try:
            # Recolectar los datos del formulario
            client_data = {
                "nombre": txt_name.value,
                "apellido": txt_surname.value,
                "dni": txt_dni.value,
                "email": txt_email.value,
                "edad": int(txt_age.value) if txt_age.value.isdigit() else 0,
                "sexo": dropdown_gender.value,
                "apta_medica": switch_medical.value,
                "enfermedades": txt_diseases.value,
                "fecha_inicio": txt_membership_start.value,
                "fecha_vencimiento": txt_membership_end.value
            }

            # Conexión a la base de datos e inserción de datos
            conn = conectar_db()  # Usar tu función de conexión
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clientes (nombre, apellido, dni, email, edad, sexo, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento)
                VALUES (:nombre, :apellido, :dni, :email, :edad, :sexo, :apta_medica, :enfermedades, :fecha_inicio, :fecha_vencimiento)
            ''', client_data)
            conn.commit()

            print("Cliente registrado exitosamente:", client_data)
        except sqlite3.Error as e:
            print(f"Error al registrar el cliente: {e}")
        finally:
            # Cerrar la conexión en cualquier caso
            if conn:
                conn.close()

        # Limpiar los campos del formulario después del registro
        txt_name.value = ""
        txt_surname.value = ""
        txt_dni.value = ""
        txt_email.value = ""
        txt_age.value = ""
        dropdown_gender.value = ""
        switch_medical.value = False
        txt_diseases.value = ""
        txt_membership_start.value = ""
        txt_membership_end.value = ""
        page.update()
    btn_submit = ft.ElevatedButton(
        text="Agregar Cliente",
        on_click=submit_client,
        style=ft.ButtonStyle(
            bgcolor=configuracion["color_tematica"],
            color=configuracion["color_letras"]
        )
    )

    membership_start_row = ft.Row([txt_membership_start, btn_pick_start], spacing=5)
    membership_end_row = ft.Row([txt_membership_end, btn_pick_end], spacing=5)

    form = ft.Column(
        [
            ft.Text("Agregar Cliente", size=32, weight="bold", color=configuracion["color_letras"]),
            txt_name,
            txt_surname,
            ft.Row([txt_dni, txt_age], spacing=10),
            txt_email,
            dropdown_gender,
            txt_diseases,
            switch_medical,
            membership_start_row,
            membership_end_row,
            btn_submit,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    container = ft.Container(
        content=form,
        alignment=ft.alignment.center,
        padding=20,
        bgcolor=configuracion["color_fondo"],
        border_radius=ft.BorderRadius(10, 10, 10, 10),
        width=500,
        height=800,
    )

    scrollable_layout = ft.ListView(
        expand=True,
        spacing=10,
        controls=[
            ft.Row([btn_volver], alignment=ft.MainAxisAlignment.START),
            container
        ]
    )

    page.add(scrollable_layout)
    page.update()

if __name__ == "__main__":
    ft.app(target=vista_add_client)