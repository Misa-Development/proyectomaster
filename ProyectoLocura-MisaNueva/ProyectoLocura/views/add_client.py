import flet as ft
import sqlite3
import json
from database.db import conectar_db, eliminar_cliente_por_dni
from views.Menu import vista_menu
from views.custom_date_picker import open_custom_date_picker_modal

CONFIG_FILE = "config.json"

def cargar_configuracion():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"color_fondo": "#FFFFFF", "color_tematica": "#E8E8E8", "color_letras": "#000000", "nombre_gimnasio": "Mi Gimnasio"}

def vista_add_client(page):
    configuracion = cargar_configuracion()
    page.title, page.window_maximized, page.bgcolor = "Agregar Cliente", True, configuracion["color_fondo"]

    menu = vista_menu(page)

    # Crear campos de texto con etiquetas del color correcto
    campos = ["nombre", "apellido", "dni", "edad", "email", "sexo", "enfermedades"]
    inputs = {
        campo: ft.TextField(
            label=campo.capitalize(),
            bgcolor=configuracion["color_tematica"],
            border_radius=8,
            border_color=configuracion["color_letras"],
            text_style=ft.TextStyle(color=configuracion["color_letras"]),
            label_style=ft.TextStyle(color=configuracion["color_letras"])  # Ahora el color de la etiqueta es correcto
        )
        for campo in campos
    }

    inputs["sexo"] = ft.Dropdown(
        label="Seleccione el Sexo",
        options=[
            ft.dropdown.Option(key="Male", text="Masculino"),
            ft.dropdown.Option(key="Female", text="Femenino"),
            ft.dropdown.Option(key="Other", text="Otro"),
        ],
        value="Todos",
        label_style=ft.TextStyle(color=configuracion["color_letras"])  # Color del label correcto
    )

    switch_medical = ft.Switch(label="Apta Médica", value=False, active_color=configuracion["color_letras"])

    def show_date_picker(text_field):
        def on_date_selected(selected_date):
            text_field.value = selected_date.strftime("%d/%m/%Y")
            page.overlay.remove(overlay)
            page.update()
        overlay = open_custom_date_picker_modal(page, None, on_date_selected)
        page.overlay.append(overlay)
        page.update()

    fechas = {
        key: ft.TextField(
            label=label,
            read_only=True,
            bgcolor=configuracion["color_tematica"],
            border_radius=8,
            border_color=configuracion["color_letras"],
            label_style=ft.TextStyle(color=configuracion["color_letras"])  # Color del label corregido
        )
        for key, label in {"inicio": "Inicio de Membresía", "vencimiento": "Vencimiento de Membresía"}.items()
    }

    botones_fecha = {
        key: ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e, f=fechas[key]: show_date_picker(f),
            style=ft.ButtonStyle(bgcolor=configuracion["color_tematica"], color=configuracion["color_letras"])
        )
        for key in fechas
    }

    def submit_client(e):
        client_data = {campo: inputs[campo].value.strip() for campo in inputs}
        client_data["apta_medica"], client_data["fecha_inicio"], client_data["fecha_vencimiento"] = switch_medical.value, fechas["inicio"].value, fechas["vencimiento"].value

        required_fields = ["nombre", "apellido", "dni", "email", "edad", "sexo", "fecha_inicio", "fecha_vencimiento"]
        if any(not client_data[campo] for campo in required_fields):
            mostrar_alerta("⚠️ Error", "Todos los campos son obligatorios.", "red")
            return

        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO clientes (nombre, apellido, dni, email, edad, sexo, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento)
                VALUES (:nombre, :apellido, :dni, :email, :edad, :sexo, :apta_medica, :enfermedades, :fecha_inicio, :fecha_vencimiento)''',
                client_data
            )
            conn.commit()
            conn.close()
            mostrar_alerta("✅ Éxito", f"Cliente {client_data['nombre']} {client_data['apellido']} registrado exitosamente.", "green")

            for campo in inputs.values():
                campo.value = ""
            fechas["inicio"].value, fechas["vencimiento"].value, switch_medical.value = "", "", False
            page.update()
        except sqlite3.Error as err:
            mostrar_alerta("⚠️ Error", f"Error al registrar cliente: {err}", "red")

    def cerrar_dialogo(dialog):
        dialog.open = False
        page.update()

    def mostrar_alerta(titulo, mensaje, color):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, weight="bold", color=color, size=18),
            content=ft.Text(mensaje, size=14, color=configuracion["color_letras"]),
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=configuracion["color_tematica"],
            actions=[ft.TextButton("Cerrar", on_click=lambda e: cerrar_dialogo(dialog), style=ft.ButtonStyle(color=color))]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    btn_submit = ft.ElevatedButton(
        text="Agregar Cliente",
        on_click=submit_client,
        style=ft.ButtonStyle(bgcolor=configuracion["color_tematica"], color=configuracion["color_letras"])
    )

    form = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Agregar Cliente", size=24, weight="bold", color=configuracion["color_letras"]),
                *inputs.values(), switch_medical,
                ft.Row([fechas["inicio"], botones_fecha["inicio"]], spacing=5),
                ft.Row([fechas["vencimiento"], botones_fecha["vencimiento"]], spacing=5), btn_submit
            ], spacing=15
        ),
        padding=20,
        bgcolor=configuracion["color_fondo"],
        border_radius=12
    )

    page.add(ft.Column(controls=[menu, ft.Container(content=form, alignment=ft.alignment.center)], spacing=20))
    page.update()