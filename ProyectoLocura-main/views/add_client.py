import flet as ft
import sqlite3, json, os, shutil, threading
from database.db import conectar_db
from views.Menu import vista_menu
from views.custom_date_picker import open_custom_date_picker_modal
from datetime import datetime
from dateutil.relativedelta import relativedelta  # <-- NUEVO

CONFIG_FILE = "config.json"
IMAGE_DIR = "database/images/"

def cargar_configuracion():
    try: return json.load(open(CONFIG_FILE))
    except FileNotFoundError: return {"color_fondo": "#FFFFFF", "color_tematica": "#E8E8E8", "color_letras": "#000000", "nombre_gimnasio": "Mi Gimnasio"}

def estilo_texto(config, label, read_only=False):
    return ft.TextField(label=label, read_only=read_only, bgcolor=config["color_fondo"], border_radius=8, border_color=config["color_tematica"], 
                        text_style=ft.TextStyle(color=config["color_letras"]), label_style=ft.TextStyle(color=config["color_letras"]))

def vista_add_client(page, cambiar_vista=None):
    import re
    # Estados de error para mostrar advertencias
    errores = {"nombre": "", "apellido": "", "dni": "", "email": ""}

    config = cargar_configuracion()
    page.title, page.window_maximized, page.bgcolor = "Agregar Cliente", True, config["color_fondo"]
    inputs = {}
    inputs["nombre"] = estilo_texto(config, "Nombre")
    inputs["apellido"] = estilo_texto(config, "Apellido")
    inputs["dni"] = estilo_texto(config, "Dni")
    inputs["email"] = estilo_texto(config, "Email")
    inputs["enfermedades"] = estilo_texto(config, "Enfermedades")

    # Campos con navegación por Enter
    def validar_nombre(e):
        valor = e.control.value
        if not valor.isalpha():
            errores["nombre"] = "Solo se permiten letras."
        else:
            errores["nombre"] = ""
        page.update()
    def validar_apellido(e):
        valor = e.control.value
        if not valor.isalpha():
            errores["apellido"] = "Solo se permiten letras."
        else:
            errores["apellido"] = ""
        page.update()
    def validar_dni(e):
        valor = e.control.value
        if not valor.isdigit() or not (7 <= len(valor) <= 10):
            errores["dni"] = "Solo números (7-10 dígitos)."
        else:
            errores["dni"] = ""
        page.update()
    def validar_email(e):
        valor = e.control.value
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", valor):
            errores["email"] = "Formato de email inválido."
        else:
            errores["email"] = ""
        page.update()

    def label_color(error):
        return "red" if error else config["color_letras"]

    def recreate_fields():
        # recrea los campos con el color correcto
        inputs["nombre"].label_style = ft.TextStyle(color=label_color(errores["nombre"]))
        inputs["apellido"].label_style = ft.TextStyle(color=label_color(errores["apellido"]))
        inputs["dni"].label_style = ft.TextStyle(color=label_color(errores["dni"]))
        inputs["email"].label_style = ft.TextStyle(color=label_color(errores["email"]))
        inputs["fecha_nacimiento_dia"].label_style = ft.TextStyle(color=label_color(errores["fecha_nacimiento_dia"]))
        inputs["fecha_nacimiento_mes"].label_style = ft.TextStyle(color=label_color(errores["fecha_nacimiento_mes"]))
        inputs["fecha_nacimiento_anio"].label_style = ft.TextStyle(color=label_color(errores["fecha_nacimiento_anio"]))

    def validar_nombre(e):
        valor = e.control.value
        if not valor.isalpha():
            errores["nombre"] = "Solo se permiten letras."
        else:
            errores["nombre"] = ""
        recreate_fields()
        page.update()
    def validar_apellido(e):
        valor = e.control.value
        if not valor.isalpha():
            errores["apellido"] = "Solo se permiten letras."
        else:
            errores["apellido"] = ""
        recreate_fields()
        page.update()
    def validar_dni(e):
        valor = e.control.value
        if not valor.isdigit() or not (7 <= len(valor) <= 10):
            errores["dni"] = "Solo números (7-10 dígitos)."
        else:
            errores["dni"] = ""
        recreate_fields()
        page.update()
    def validar_email(e):
        valor = e.control.value
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", valor):
            errores["email"] = "Formato de email inválido."
        else:
            errores["email"] = ""
        recreate_fields()
        page.update()
    def validar_fecha_nacimiento_dia(e):
        valor = e.control.value
        if not valor.isdigit() or not (1 <= int(valor) <= 31):
            errores["fecha_nacimiento_dia"] = "Día inválido."
        else:
            errores["fecha_nacimiento_dia"] = ""
        recreate_fields()
        page.update()
    def validar_fecha_nacimiento_mes(e):
        valor = e.control.value
        if not valor.isdigit() or not (1 <= int(valor) <= 12):
            errores["fecha_nacimiento_mes"] = "Mes inválido."
        else:
            errores["fecha_nacimiento_mes"] = ""
        recreate_fields()
        page.update()
    def validar_fecha_nacimiento_anio(e):
        valor = e.control.value
        if not valor.isdigit() or not (1900 <= int(valor) <= datetime.now().year):
            errores["fecha_nacimiento_anio"] = "Año inválido."
        else:
            errores["fecha_nacimiento_anio"] = ""
        recreate_fields()
        page.update()

    errores["fecha_nacimiento_dia"] = ""
    errores["fecha_nacimiento_mes"] = ""
    errores["fecha_nacimiento_anio"] = ""

    # Inicialización de los campos (solo una vez)
    inputs["nombre"] = ft.TextField(
        label="Nombre", bgcolor=config["color_fondo"], border_radius=8, border_color=config["color_tematica"],
        text_style=ft.TextStyle(color=config["color_letras"]),
        label_style=ft.TextStyle(color=label_color(errores["nombre"])),
        on_submit=lambda e: inputs["apellido"].focus(),
        on_change=validar_nombre,
        error_text=errores["nombre"] if errores["nombre"] else None
    )
    inputs["apellido"] = ft.TextField(
        label="Apellido", bgcolor=config["color_fondo"], border_radius=8, border_color=config["color_tematica"],
        text_style=ft.TextStyle(color=config["color_letras"]),
        label_style=ft.TextStyle(color=label_color(errores["apellido"])),
        on_submit=lambda e: inputs["dni"].focus(),
        on_change=validar_apellido,
        error_text=errores["apellido"] if errores["apellido"] else None
    )
    inputs["dni"] = ft.TextField(
        label="Dni", bgcolor=config["color_fondo"], border_radius=8, border_color=config["color_tematica"],
        text_style=ft.TextStyle(color=config["color_letras"]),
        label_style=ft.TextStyle(color=label_color(errores["dni"])),
        on_submit=lambda e: inputs["email"].focus(),
        on_change=validar_dni,
        error_text=errores["dni"] if errores["dni"] else None
    )
    inputs["email"] = ft.TextField(
        label="Email", bgcolor=config["color_fondo"], border_radius=8, border_color=config["color_tematica"],
        text_style=ft.TextStyle(color=config["color_letras"]),
        label_style=ft.TextStyle(color=label_color(errores["email"])),
        on_submit=lambda e: inputs["fecha_nacimiento_dia"].focus(),
        on_change=validar_email,
        error_text=errores["email"] if errores["email"] else None
    )
    inputs["fecha_nacimiento_dia"] = ft.TextField(
        label="Día", width=60, max_length=2, bgcolor=config["color_fondo"], border_radius=8, border_color=config["color_tematica"],
        text_style=ft.TextStyle(color=config["color_letras"]),
        label_style=ft.TextStyle(color=label_color(errores["fecha_nacimiento_dia"])),
        on_submit=lambda e: inputs["fecha_nacimiento_mes"].focus(),
        on_change=validar_fecha_nacimiento_dia,
        error_text=errores["fecha_nacimiento_dia"] if errores["fecha_nacimiento_dia"] else None
    )
    inputs["fecha_nacimiento_mes"] = ft.TextField(
        label="Mes", width=60, max_length=2, bgcolor=config["color_fondo"], border_radius=8, border_color=config["color_tematica"],
        text_style=ft.TextStyle(color=config["color_letras"]),
        label_style=ft.TextStyle(color=label_color(errores["fecha_nacimiento_mes"])),
        on_submit=lambda e: inputs["fecha_nacimiento_anio"].focus(),
        on_change=validar_fecha_nacimiento_mes,
        error_text=errores["fecha_nacimiento_mes"] if errores["fecha_nacimiento_mes"] else None
    )
    inputs["fecha_nacimiento_anio"] = ft.TextField(
        label="Año", width=80, max_length=4, bgcolor=config["color_fondo"], border_radius=8, border_color=config["color_tematica"],
        text_style=ft.TextStyle(color=config["color_letras"]),
        label_style=ft.TextStyle(color=label_color(errores["fecha_nacimiento_anio"])),
        on_submit=lambda e: inputs["enfermedades"].focus(),
        on_change=validar_fecha_nacimiento_anio,
        error_text=errores["fecha_nacimiento_anio"] if errores["fecha_nacimiento_anio"] else None
    )
    inputs["enfermedades"] = ft.TextField(
        label="Enfermedades", bgcolor=config["color_fondo"], border_radius=8, border_color=config["color_tematica"],
        text_style=ft.TextStyle(color=config["color_letras"]), label_style=ft.TextStyle(color=config["color_letras"])
    )
    inputs["sexo"] = ft.Dropdown(
        label="Sexo",
        border_color=config["color_tematica"],
        options=[
            ft.dropdown.Option(key="Male", text="Masculino"),
            ft.dropdown.Option(key="Female", text="Femenino"),
            ft.dropdown.Option(key="Other", text="Otro")
        ],
        value=None,
        label_style=ft.TextStyle(color=config["color_letras"]),
        text_style=ft.TextStyle(color=config["color_letras"])
    )
    switch_medical = ft.Switch(label="Apta Médica", value=False, active_color=config["color_tematica"], label_style=ft.TextStyle(color=config["color_letras"]))

    fechas = {key: estilo_texto(config, label, True) for key, label in {"inicio": "Inicio de Membresía", "vencimiento": "Vencimiento de Membresía"}.items()}

    # Inicializar 'menu' antes de usarlo en el layout
    menu = vista_menu(page)

    # --- NUEVO: Función para poner la fecha de hoy ---
    def set_fecha_hoy(e):
        hoy = datetime.now().strftime("%d/%m/%Y")
        fechas["inicio"].value = hoy
        auto_rellenar_vencimiento()
        page.update()

    # --- NUEVO: Auto-rellenar vencimiento cuando se completa inicio ---
    def auto_rellenar_vencimiento(*args):
        try:
            fecha_inicio = datetime.strptime(fechas["inicio"].value, "%d/%m/%Y")
            fecha_vencimiento = fecha_inicio + relativedelta(months=1)
            fechas["vencimiento"].value = fecha_vencimiento.strftime("%d/%m/%Y")
            page.update()
        except Exception:
            pass

    # --- NUEVO: Modificadores de mes para vencimiento ---
    def modificar_mes_vencimiento(delta):
        try:
            fecha_vencimiento = datetime.strptime(fechas["vencimiento"].value, "%d/%m/%Y")
            nueva_fecha = fecha_vencimiento + relativedelta(months=delta)
            fechas["vencimiento"].value = nueva_fecha.strftime("%d/%m/%Y")
            page.update()
        except Exception:
            pass

    def show_date_picker(text_field):
        def on_date_selected(date):
            text_field.value = date.strftime("%d/%m/%Y")
            if text_field is fechas["inicio"]:
                auto_rellenar_vencimiento()
            # Solo elimina el modal de fecha, no limpia todos los overlays
            for overlay in page.overlay[:]:
                if isinstance(overlay, ft.Container) and getattr(overlay, "width", None) == 350 and getattr(overlay, "bgcolor", None) == config["color_tematica"]:
                    page.overlay.remove(overlay)
            page.update()

        page.overlay.append(open_custom_date_picker_modal(page, None, on_date_selected))
        page.update()

    botones_fecha = {
        "inicio": ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda e, f=fechas["inicio"]: show_date_picker(f), style=ft.ButtonStyle(bgcolor=config["color_tematica"], color="black")),
        "vencimiento": ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda e, f=fechas["vencimiento"]: show_date_picker(f), style=ft.ButtonStyle(bgcolor=config["color_tematica"], color="black"))
    }

    # --- NUEVO: Botón "Hoy" para inicio ---
    boton_hoy = ft.TextButton("Hoy", on_click=set_fecha_hoy, style=ft.ButtonStyle(bgcolor=config["color_tematica"], color="black"))

    # --- NUEVO: Botones + y - para vencimiento ---
    boton_menos = ft.IconButton(icon=ft.Icons.REMOVE, on_click=lambda e: modificar_mes_vencimiento(-1), style=ft.ButtonStyle(bgcolor=config["color_tematica"], color="black"))
    boton_mas = ft.IconButton(icon=ft.Icons.ADD, on_click=lambda e: modificar_mes_vencimiento(1), style=ft.ButtonStyle(bgcolor=config["color_tematica"], color="black"))

    # --- NUEVO: Detectar cambio manual en inicio para auto-rellenar vencimiento ---
    fechas["inicio"].on_change = lambda e: auto_rellenar_vencimiento()

    file_picker = ft.FilePicker(on_result=lambda e: guardar_imagen(e.files))
    page.add(file_picker)

    def guardar_imagen(files):
        if files and (file := files[0]).path.endswith((".jpg", ".png")):
            dni = inputs["dni"].value.strip()
            if dni: shutil.move(file.path, os.path.join(IMAGE_DIR, f"{dni}.png"))
            else: mostrar_alerta(page, "⚠️ Error", "DNI no especificado.", "red")
        else: mostrar_alerta(page, "⚠️ Error", "Formato de imagen no válido.", "red")

    def confirmar_registro(e):
        dialog = ft.AlertDialog(
            modal=True, title=ft.Text("Confirmar Registro", size=18, weight="bold", color="blue"),
            content=ft.Text("¿Deseas agregar este cliente a la base de datos?", size=14, color=config["color_letras"]),
            shape=ft.RoundedRectangleBorder(radius=10), bgcolor=config["color_tematica"],
            actions=[ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(dialog, page), style=ft.ButtonStyle(color="red")),
                     ft.TextButton("Confirmar", on_click=lambda e: submit_client(), style=ft.ButtonStyle(color="green"))]
        )
        page.overlay.append(dialog), setattr(dialog, "open", True), page.update()

    def mostrar_alerta(page, titulo, mensaje, color, on_close=None):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, weight="bold", color=color, size=18),
            content=ft.Text(mensaje, size=14, color=config["color_letras"]),
            shape=ft.RoundedRectangleBorder(radius=10),
            bgcolor=config["color_tematica"],
            actions=[]
        )
        def cerrar_y_reiniciar_dialogo(e=None):
            print('cerrar_y_reiniciar_dialogo ejecutado')
            dialog.open = False
            page.update()
            if on_close is True:
                page.clean()
                page.add(vista_add_client(page))
                page.update()
        dialog.actions.append(
            ft.TextButton("Cerrar", on_click=cerrar_y_reiniciar_dialogo, style=ft.ButtonStyle(color=color))
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def cerrar_dialogo(dialog, page):
        dialog.open = False
        page.update()

    def submit_client():
        client_data = {k: (v.value.strip() if hasattr(v, 'value') and v.value is not None else "") for k, v in inputs.items()}
        # Si el campo enfermedades tiene el texto por defecto, guardar vacío
        if client_data.get("enfermedades", "") in ("Sin enfermedades registradas", "No especificado"):
            client_data["enfermedades"] = ""
        # Combinar fecha de nacimiento
        dia = client_data.get("fecha_nacimiento_dia", "")
        mes = client_data.get("fecha_nacimiento_mes", "")
        anio = client_data.get("fecha_nacimiento_anio", "")
        client_data["fecha_nacimiento"] = f"{anio}-{mes.zfill(2)}-{dia.zfill(2)}" if dia and mes and anio else ""
        client_data.update({
            "apta_medica": switch_medical.value,
            "fecha_inicio": fechas["inicio"].value,
            "fecha_vencimiento": fechas["vencimiento"].value,
            "foto": f"{IMAGE_DIR}{client_data['dni']}.png",
            "estado": 1  # 🔹 Estado por defecto como "Activo"
        })
        # Validar campos obligatorios
        campos_obligatorios = ["nombre", "apellido", "dni", "email", "fecha_nacimiento", "sexo", "fecha_inicio", "fecha_vencimiento"]
        # Validar errores de campos y mostrar cuáles son
        # Forzar validación para mostrar error_text en la ventana
        class DummyEvent:
            def __init__(self, control):
                self.control = control
        validar_nombre(DummyEvent(inputs["nombre"]))
        validar_apellido(DummyEvent(inputs["apellido"]))
        validar_dni(DummyEvent(inputs["dni"]))
        validar_email(DummyEvent(inputs["email"]))
        validar_fecha_nacimiento_dia(DummyEvent(inputs["fecha_nacimiento_dia"]))
        validar_fecha_nacimiento_mes(DummyEvent(inputs["fecha_nacimiento_mes"]))
        validar_fecha_nacimiento_anio(DummyEvent(inputs["fecha_nacimiento_anio"]))
        campos_con_error = [campo.replace("fecha_nacimiento_", "").capitalize() if campo.startswith("fecha_nacimiento_") else campo.capitalize() for campo in ["nombre", "apellido", "dni", "email", "fecha_nacimiento_dia", "fecha_nacimiento_mes", "fecha_nacimiento_anio"] if errores.get(campo)]
        campos_incompletos = [campo.replace("_", " ").capitalize() for campo in campos_obligatorios if not client_data.get(campo)]
        mensaje_error = ""
        if campos_con_error:
            mensaje_error += "Corrige los siguientes campos: " + ", ".join(campos_con_error) + ". "
        if campos_incompletos:
            mensaje_error += "Completa los siguientes campos: " + ", ".join(campos_incompletos) + "."
        if mensaje_error:
            page.update()
            mostrar_alerta(page, "⚠️ Error", mensaje_error.strip(), "red")
            return
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO clientes (nombre, apellido, dni, email, fecha_nacimiento, sexo, apta_medica, enfermedades, 
                                               fecha_inicio, fecha_vencimiento, foto, estado)
                         VALUES (:nombre, :apellido, :dni, :email, :fecha_nacimiento, :sexo, :apta_medica, :enfermedades, 
                                 :fecha_inicio, :fecha_vencimiento, :foto, :estado)''', client_data)
            conn.commit()
            # Registrar movimiento en la tabla de historial
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''INSERT INTO historial_movimientos (tipo, nombre, apellido, dni, fecha)
                                VALUES (?, ?, ?, ?, ?)''', ("Alta", client_data['nombre'], client_data['apellido'], client_data['dni'], now))
            conn.commit()
            conn.close()
            # Limpiar los campos
            for campo in inputs.values():
                campo.value = ""
            fechas["inicio"].value = fechas["vencimiento"].value = ""
            switch_medical.value = False
            page.update()
            mostrar_alerta(page, "✅ Éxito", f"Cliente {client_data['nombre']} {client_data['apellido']} registrado exitosamente.", "green", on_close=True)
        except sqlite3.Error as err:
            mostrar_alerta(page, "⚠️ Error", f"Error al registrar cliente: {err}", "red")

    form = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Agregar Cliente", size=24, weight="bold", color=config["color_letras"]),
                inputs["nombre"],
                inputs["apellido"],
                inputs["dni"],
                inputs["email"],
                ft.Row([
                    ft.Text("Fecha de Nacimiento", size=14, color=config["color_letras"], width=150),
                    inputs["fecha_nacimiento_dia"],
                    inputs["fecha_nacimiento_mes"],
                    inputs["fecha_nacimiento_anio"]
                ], spacing=5, alignment="start"),
                inputs["sexo"],
                inputs["enfermedades"],
                switch_medical,
                ft.ElevatedButton("Adjuntar Foto", on_click=lambda e: file_picker.pick_files(allow_multiple=False), style=ft.ButtonStyle(bgcolor=config["color_tematica"], color="black")),
                # Fila de inicio con botón "Hoy"
                ft.Row([fechas["inicio"], botones_fecha["inicio"], boton_hoy], spacing=5),
                # Fila de vencimiento con + y -
                ft.Row([fechas["vencimiento"], botones_fecha["vencimiento"], boton_menos, boton_mas], spacing=5),
                ft.ElevatedButton("Agregar Cliente", on_click=confirmar_registro, style=ft.ButtonStyle(bgcolor=config["color_tematica"], color="black"))
            ],
            spacing=15
        ),
        padding=20, bgcolor=config["color_fondo"], border_radius=12
    )

    main_content = ft.Container(content=ft.Column(controls=[menu, form], spacing=20, scroll="adaptive"), expand=True)
    return main_content