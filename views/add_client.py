import flet as ft
import json
import sqlite3
from views.Menu import vista_menu  # Integración del menú
from views.custom_date_picker import open_custom_date_picker_modal  # Selector de fechas
from database.db import conectar_db  # Conexión con la base de datos

# Ruta del archivo de configuración
CONFIG_FILE = "config.json"

def cargar_configuracion():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "color_fondo": "#FFFFFF",
            "color_tematica": "#E8E8E8",
            "color_letras": "#000000",
            "nombre_gimnasio": "Mi Gimnasio"
        }

def vista_add_client(page):
    configuracion = cargar_configuracion()

    # Configuración general de la página
    page.title = "Agregar Cliente"
    page.window_maximized = True
    page.bgcolor = configuracion["color_fondo"]

    # Menú en la parte superior izquierda
    menu = vista_menu(page)

    # Campos del formulario
    txt_name = ft.TextField(
        label="Nombre",
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"],
        hint_style=ft.TextStyle(color=configuracion["color_letras"]),
        label_style=ft.TextStyle(color=configuracion["color_letras"]),
    )
    txt_surname = ft.TextField(
        label="Apellido",
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"],
        hint_style=ft.TextStyle(color=configuracion["color_letras"]),
        label_style=ft.TextStyle(color=configuracion["color_letras"]),
    )
    txt_dni = ft.TextField(
        label="N° Documento",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"],
        hint_style=ft.TextStyle(color=configuracion["color_letras"]),
        label_style=ft.TextStyle(color=configuracion["color_letras"]),
    )
    txt_age = ft.TextField(
        label="Edad",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"],
        hint_style=ft.TextStyle(color=configuracion["color_letras"]),
        label_style=ft.TextStyle(color=configuracion["color_letras"]),
    )
    txt_email = ft.TextField(
        label="Email",
        keyboard_type=ft.KeyboardType.EMAIL,
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"],
        hint_style=ft.TextStyle(color=configuracion["color_letras"]),
        label_style=ft.TextStyle(color=configuracion["color_letras"]),
    )
    dropdown_gender = ft.Dropdown(
        label="Seleccione el Sexo",        
        label_style=ft.TextStyle(color=configuracion["color_letras"]),
        options=[
            ft.dropdown.Option(key="Male", text="Masculino"),
            ft.dropdown.Option(key="Female", text="Femenino"),
            ft.dropdown.Option(key="Other", text="Otro"),
        ],
        value="",
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_letras"],
        hint_style=ft.TextStyle(color=configuracion["color_letras"])
    )
    txt_diseases = ft.TextField(
        label="Enfermedades",
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"],
        hint_style=ft.TextStyle(color=configuracion["color_letras"]),
        label_style=ft.TextStyle(color=configuracion["color_letras"])
    )
    switch_medical = ft.Switch(
        label="Apta Médica",
        value=False,
        active_color=configuracion["color_tematica"]
    )

    # Función para mostrar el selector de fechas
    def show_date_picker(text_field):
        def on_date_selected(selected_date):
            text_field.value = selected_date.strftime("%d/%m/%Y")
            if overlay in page.overlay:
                page.overlay.remove(overlay)
            page.update()

        overlay = open_custom_date_picker_modal(page, None, on_date_selected)
        page.overlay.append(overlay)
        page.update()

    # Campos de fechas
    txt_membership_start = ft.TextField(
        label="Inicio de Membresía",
        read_only=True,
        text_style=ft.TextStyle(color=configuracion["color_letras"]),
        border_color=configuracion["color_letras"],
        bgcolor=configuracion["color_tematica"],
        hint_style=ft.TextStyle(color=configuracion["color_letras"]),
        label_style=ft.TextStyle(color=configuracion["color_letras"])
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
        bgcolor=configuracion["color_tematica"],
        hint_style=ft.TextStyle(color=configuracion["color_letras"]),
        label_style=ft.TextStyle(color=configuracion["color_letras"])
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

    # Función para enviar datos del cliente
    def submit_client(e):
        try:
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
                "fecha_vencimiento": txt_membership_end.value,
            }
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clientes (nombre, apellido, dni, email, edad, sexo, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento)
                VALUES (:nombre, :apellido, :dni, :email, :edad, :sexo, :apta_medica, :enfermedades, :fecha_inicio, :fecha_vencimiento)
            ''', client_data)
            conn.commit()
            print("Cliente registrado exitosamente:", client_data)
        except sqlite3.Error as err:
            print(f"Error al registrar cliente: {err}")
        finally:
            if conn:
                conn.close()

        # Limpiar los campos después de enviar el formulario
        for field in [txt_name, txt_surname, txt_dni, txt_email, txt_age, txt_diseases, txt_membership_start, txt_membership_end]:
            field.value = ""
        dropdown_gender.value = ""
        switch_medical.value = False
        page.update()

    btn_submit = ft.ElevatedButton(
        text="Agregar Cliente",
        on_click=submit_client,
        style=ft.ButtonStyle(bgcolor=configuracion["color_tematica"], color=configuracion["color_letras"]),
    )

    # Formulario organizado
    form = ft.Column(
        controls=[
            ft.Text("Agregar Cliente", size=32, weight="bold", color=configuracion["color_letras"]),
            txt_name, txt_surname,
            ft.Row([txt_dni, txt_age], spacing=10),
            txt_email, dropdown_gender, txt_diseases, switch_medical,
            ft.Row([txt_membership_start, btn_pick_start], spacing=5),
            ft.Row([txt_membership_end, btn_pick_end], spacing=5),
            btn_submit,
        ],
        spacing=10,
    )

    # Layout principal
    page.add(
        ft.Column(
            controls=[
                menu,  # Menú en la parte superior
                ft.ListView(
                    expand=True,
                    controls=[form]
                )
            ],
            spacing=20
        )
    )
    page.update()