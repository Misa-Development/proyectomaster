import flet as ft
import sqlite3
import json
from database.db import conectar_db
from views.Menu import vista_menu
from views.custom_date_picker import open_custom_date_picker_modal

CONFIG_FILE = "config.json"

def cargar_configuracion():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"color_fondo": "#FFFFFF", "color_tematica": "#E8E8E8", "color_letras": "#000000", "nombre_gimnasio": "Mi Gimnasio"}

def estilo_texto(config, label, read_only=False, on_submit=None):
    return ft.TextField(
        label=label, 
        read_only=read_only, 
        bgcolor=config["color_tematica"], 
        border_radius=8, 
        border_color=config["color_letras"], 
        text_style=ft.TextStyle(color=config["color_letras"]), 
        label_style=ft.TextStyle(color=config["color_letras"]), 
        on_submit=on_submit  # Detecta Enter/Intro
    )

def vista_add_client(page):
    config = cargar_configuracion()
    page.title, page.window_maximized, page.bgcolor = "Agregar Cliente", True, config["color_fondo"]

    menu = vista_menu(page)

    def confirmar_registro(e):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Confirmar registro?", weight="bold", color="blue", size=18),
            content=ft.Text("¿Deseas agregar este cliente a la base de datos?", size=14, color=config["color_letras"]),
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=config["color_tematica"],
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(dialog, page), style=ft.ButtonStyle(color="red")),
                ft.TextButton("Confirmar", on_click=submit_client, style=ft.ButtonStyle(color="green"))
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    inputs = {campo: estilo_texto(config, campo.capitalize(), on_submit=confirmar_registro) for campo in ["nombre", "apellido", "dni", "edad", "email", "enfermedades"]}

    inputs["sexo"] = ft.Dropdown(
        label="Seleccione el Sexo",
        options=[ft.dropdown.Option(key=k, text=v) for k, v in [("Male", "Masculino"), ("Female", "Femenino"), ("Other", "Otro")]],
        value="Todos",
        label_style=ft.TextStyle(color=config["color_letras"])
    )

    switch_medical = ft.Switch(
            label="Apta Médica",
            value=False,
            active_color=config["color_letras"],
            label_style=ft.TextStyle(color=config["color_letras"])  # Color de la etiqueta
        )

    fechas = {key: estilo_texto(config, label, True) for key, label in {"inicio": "Inicio de Membresía", "vencimiento": "Vencimiento de Membresía"}.items()}

    def show_date_picker(text_field):
        def on_date_selected(date):
            text_field.value = date.strftime("%d/%m/%Y")
            page.overlay.clear()
            page.update()

        page.overlay.append(open_custom_date_picker_modal(page, None, on_date_selected))
        page.update()

    botones_fecha = {key: ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda e, f=fechas[key]: show_date_picker(f),
                                        style=ft.ButtonStyle(bgcolor=config["color_tematica"], color=config["color_letras"])) for key in fechas}

    def submit_client(e):
        client_data = {k: v.value.strip() for k, v in inputs.items()}
        client_data.update({"apta_medica": switch_medical.value, "fecha_inicio": fechas["inicio"].value, "fecha_vencimiento": fechas["vencimiento"].value})

        if any(not client_data[campo] for campo in ["nombre", "apellido", "dni", "email", "edad", "sexo", "fecha_inicio", "fecha_vencimiento"]):
            mostrar_alerta(page, "⚠️ Error", "Todos los campos son obligatorios.", "red")
            return
        
        try:
            conn = conectar_db()
            conn.cursor().execute('''INSERT INTO clientes (nombre, apellido, dni, email, edad, sexo, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento)
                                    VALUES (:nombre, :apellido, :dni, :email, :edad, :sexo, :apta_medica, :enfermedades, :fecha_inicio, :fecha_vencimiento)''', client_data)
            conn.commit(), conn.close()
            mostrar_alerta(page, "✅ Éxito", f"Cliente {client_data['nombre']} {client_data['apellido']} registrado exitosamente.", "green")
            
            for campo in inputs.values(): campo.value = ""
            fechas["inicio"].value, fechas["vencimiento"].value, switch_medical.value = "", "", False
            page.update()
        except sqlite3.Error as err:
            mostrar_alerta(page, "⚠️ Error", f"Error al registrar cliente: {err}", "red")

    def mostrar_alerta(page, titulo, mensaje, color):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, weight="bold", color=color, size=18),
            content=ft.Text(mensaje, size=14, color=config["color_letras"]),
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=config["color_tematica"],
            actions=[ft.TextButton("Cerrar", on_click=lambda e: cerrar_dialogo(dialog, page), style=ft.ButtonStyle(color=color))]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def cerrar_dialogo(dialog, page):
        dialog.open = False
        page.update()

    btn_submit = ft.ElevatedButton(text="Agregar Cliente", on_click=confirmar_registro,
                                   style=ft.ButtonStyle(bgcolor=config["color_tematica"], color=config["color_letras"]))

    form = ft.Container(
        content=ft.Column(controls=[
            ft.Text("Agregar Cliente", size=24, weight="bold", color=config["color_letras"]),
            *inputs.values(), switch_medical,
            ft.Row([fechas["inicio"], botones_fecha["inicio"]], spacing=5),
            ft.Row([fechas["vencimiento"], botones_fecha["vencimiento"]], spacing=5),
            btn_submit
        ], spacing=15),
        padding=20, bgcolor=config["color_fondo"], border_radius=12
    )

    scroll_container = ft.Container(
        content=ft.Column(controls=[menu, form], spacing=20, scroll="adaptive"),
        expand=True
    )

    page.add(scroll_container)
    page.update()