import flet as ft
import os
from database.db import conectar_db
import json
import sqlite3

CONFIG_FILE = "config.json"
IMAGE_DIR = "database/images/"
temp_image_path = None  # Variable global para almacenar la imagen seleccionada

# 🔹 Cargar configuración
_config_cache = None

def invalidar_cache_configuracion():
    """Invalida el cache de configuración para forzar la recarga"""
    global _config_cache
    _config_cache = None
    print("[DEBUG] Cache de configuración invalidado en vistaedicion")

def cargar_configuracion():
    global _config_cache
    # SIEMPRE recargar desde archivo para obtener cambios en tiempo real
    try:
        with open(CONFIG_FILE, "r") as f:
            _config_cache = json.load(f)
        print("[DEBUG] Configuración recargada desde archivo en vistaedicion")
    except FileNotFoundError:
        _config_cache = {"color_fondo": "#FFFFFF", "color_tematica": "#E8E8E8", "color_letras": "#000000", "nombre_gimnasio": "Mi Gimnasio"}
        print("[DEBUG] Usando configuración por defecto en vistaedicion")
    return _config_cache

# 🔹 Estilo de texto optimizado
def estilo_texto(config, label, valor="", read_only=False, scale=0.85):
    return ft.TextField(
        label=label,
        value=str(valor),
        read_only=read_only,
        bgcolor=config["color_fondo"],  # Fondo igual al color de fondo general
        border_radius=8,
        border_color=config["color_letras"],
        text_style=ft.TextStyle(color=config["color_letras"], size=16*scale),
        label_style=ft.TextStyle(color=config["color_letras"], size=14*scale),
        height=38*scale,
        content_padding=ft.padding.symmetric(vertical=6*scale, horizontal=8*scale)
    )

# 🔹 Obtener DNI con validación mejorada
def obtener_dni(cliente):
    if isinstance(cliente, sqlite3.Row):  # ✅ Convierte Row a diccionario si es necesario
        cliente = dict(cliente)
    
    dni = cliente.get("dni")
    
    if not dni:  # ✅ Si el DNI está vacío, intenta obtenerlo de la base de datos
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT dni FROM clientes WHERE nombre=? AND apellido=?", (cliente.get("nombre"), cliente.get("apellido")))
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else None  # ✅ Devuelve None si no se encuentra

    return dni

# 🔹 Vista de edición optimizada
def vista_edicion(cliente, page, color_letras, color_tematica, cerrar_panel_detalles=None, cambiar_vista=None):
    global temp_image_path
    config = cargar_configuracion()
    scale = 0.85  # Escala reducida para todos los campos y textos

    dni_actualizado = obtener_dni(cliente)
    if not dni_actualizado:
        return ft.Text("⚠️ Error: Cliente sin DNI válido.", color="red", size=18)

    print(f"[DEBUG] Abriendo vista_edicion para cliente: {cliente.get('nombre')} {cliente.get('apellido')} (DNI: {dni_actualizado})")
    print(f"[DEBUG] cerrar_panel_detalles: {cerrar_panel_detalles}, cambiar_vista: {cambiar_vista}")

    import re
    errores = {"nombre": "", "apellido": "", "dni": "", "email": "", "fecha_nacimiento_dia": "", "fecha_nacimiento_mes": "", "fecha_nacimiento_anio": "", "fecha_inicio_dia": "", "fecha_inicio_mes": "", "fecha_inicio_anio": "", "fecha_vencimiento_dia": "", "fecha_vencimiento_mes": "", "fecha_vencimiento_anio": ""}
    def validar_fecha_inicio_dia(e):
        valor = e.control.value
        if not valor.isdigit() or not (1 <= int(valor) <= 31):
            errores["fecha_inicio_dia"] = "Día inválido."
        else:
            errores["fecha_inicio_dia"] = ""
        fecha_inicio_dia.label_style = ft.TextStyle(color=label_color(errores["fecha_inicio_dia"]))
        fecha_inicio_dia.error_text = errores["fecha_inicio_dia"] if errores["fecha_inicio_dia"] else None
        page.update()
    def validar_fecha_inicio_mes(e):
        valor = e.control.value
        if not valor.isdigit() or not (1 <= int(valor) <= 12):
            errores["fecha_inicio_mes"] = "Mes inválido."
        else:
            errores["fecha_inicio_mes"] = ""
        fecha_inicio_mes.label_style = ft.TextStyle(color=label_color(errores["fecha_inicio_mes"]))
        fecha_inicio_mes.error_text = errores["fecha_inicio_mes"] if errores["fecha_inicio_mes"] else None
        page.update()
    def validar_fecha_inicio_anio(e):
        valor = e.control.value
        from datetime import datetime
        if not valor.isdigit() or not (1900 <= int(valor) <= datetime.now().year):
            errores["fecha_inicio_anio"] = "Año inválido."
        else:
            errores["fecha_inicio_anio"] = ""
        fecha_inicio_anio.label_style = ft.TextStyle(color=label_color(errores["fecha_inicio_anio"]))
        fecha_inicio_anio.error_text = errores["fecha_inicio_anio"] if errores["fecha_inicio_anio"] else None
        page.update()
    def validar_fecha_vencimiento_dia(e):
        valor = e.control.value
        if not valor.isdigit() or not (1 <= int(valor) <= 31):
            errores["fecha_vencimiento_dia"] = "Día inválido."
        else:
            errores["fecha_vencimiento_dia"] = ""
        fecha_vencimiento_dia.label_style = ft.TextStyle(color=label_color(errores["fecha_vencimiento_dia"]))
        fecha_vencimiento_dia.error_text = errores["fecha_vencimiento_dia"] if errores["fecha_vencimiento_dia"] else None
        page.update()
    def validar_fecha_vencimiento_mes(e):
        valor = e.control.value
        if not valor.isdigit() or not (1 <= int(valor) <= 12):
            errores["fecha_vencimiento_mes"] = "Mes inválido."
        else:
            errores["fecha_vencimiento_mes"] = ""
        fecha_vencimiento_mes.label_style = ft.TextStyle(color=label_color(errores["fecha_vencimiento_mes"]))
        fecha_vencimiento_mes.error_text = errores["fecha_vencimiento_mes"] if errores["fecha_vencimiento_mes"] else None
        page.update()
    def validar_fecha_vencimiento_anio(e):
        valor = e.control.value
        from datetime import datetime
        if not valor.isdigit() or not (1900 <= int(valor) <= datetime.now().year):
            errores["fecha_vencimiento_anio"] = "Año inválido."
        else:
            errores["fecha_vencimiento_anio"] = ""
        fecha_vencimiento_anio.label_style = ft.TextStyle(color=label_color(errores["fecha_vencimiento_anio"]))
        fecha_vencimiento_anio.error_text = errores["fecha_vencimiento_anio"] if errores["fecha_vencimiento_anio"] else None
        page.update()
    def label_color(error):
        return "red" if error else color_letras

    # Inicialización de los campos con datos del cliente
    def validar_nombre(e):
        valor = e.control.value
        if not valor.isalpha():
            errores["nombre"] = "Solo se permiten letras."
        else:
            errores["nombre"] = ""
        nombre.label_style = ft.TextStyle(color=label_color(errores["nombre"]))
        nombre.error_text = errores["nombre"] if errores["nombre"] else None
        page.update()
    def validar_apellido(e):
        valor = e.control.value
        if not valor.isalpha():
            errores["apellido"] = "Solo se permiten letras."
        else:
            errores["apellido"] = ""
        apellido.label_style = ft.TextStyle(color=label_color(errores["apellido"]))
        apellido.error_text = errores["apellido"] if errores["apellido"] else None
        page.update()
    def validar_email(e):
        valor = e.control.value
        import re
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", valor):
            errores["email"] = "Formato de email inválido."
        else:
            errores["email"] = ""
        email.label_style = ft.TextStyle(color=label_color(errores["email"]))
        email.error_text = errores["email"] if errores["email"] else None
        page.update()
    def validar_fecha_nacimiento_dia(e):
        valor = e.control.value
        if not valor.isdigit() or not (1 <= int(valor) <= 31):
            errores["fecha_nacimiento_dia"] = "Día inválido."
        else:
            errores["fecha_nacimiento_dia"] = ""
        fecha_nacimiento_dia.label_style = ft.TextStyle(color=label_color(errores["fecha_nacimiento_dia"]))
        fecha_nacimiento_dia.error_text = errores["fecha_nacimiento_dia"] if errores["fecha_nacimiento_dia"] else None
        page.update()
    def validar_fecha_nacimiento_mes(e):
        valor = e.control.value
        if not valor.isdigit() or not (1 <= int(valor) <= 12):
            errores["fecha_nacimiento_mes"] = "Mes inválido."
        else:
            errores["fecha_nacimiento_mes"] = ""
        fecha_nacimiento_mes.label_style = ft.TextStyle(color=label_color(errores["fecha_nacimiento_mes"]))
        fecha_nacimiento_mes.error_text = errores["fecha_nacimiento_mes"] if errores["fecha_nacimiento_mes"] else None
        page.update()
    def validar_fecha_nacimiento_anio(e):
        valor = e.control.value
        from datetime import datetime
        if not valor.isdigit() or not (1900 <= int(valor) <= datetime.now().year):
            errores["fecha_nacimiento_anio"] = "Año inválido."
        else:
            errores["fecha_nacimiento_anio"] = ""
        fecha_nacimiento_anio.label_style = ft.TextStyle(color=label_color(errores["fecha_nacimiento_anio"]))
        fecha_nacimiento_anio.error_text = errores["fecha_nacimiento_anio"] if errores["fecha_nacimiento_anio"] else None
        page.update()

    nombre = ft.TextField(label="Nombre", value=cliente.get("nombre", ""), width=260, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["nombre"])), error_text=errores["nombre"],
        on_change=validar_nombre)
    apellido = ft.TextField(label="Apellido", value=cliente.get("apellido", ""), width=260, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["apellido"])), error_text=errores["apellido"],
        on_change=validar_apellido)
    dni = ft.TextField(label="Dni", value=str(cliente.get("dni", "")), width=260, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["dni"])), error_text=errores["dni"], read_only=True)
    email = ft.TextField(label="Email", value=cliente.get("email", ""), width=260, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["email"])), error_text=errores["email"],
        on_change=validar_email)
    enfermedades = ft.TextField(label="Enfermedades", value=cliente.get("enfermedades", ""), width=260, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=color_letras))
    # Fecha de nacimiento separada
    fecha_nacimiento = cliente.get("fecha_nacimiento", "")
    dia, mes, anio = "", "", ""
    if fecha_nacimiento:
        try:
            if "-" in fecha_nacimiento:
                partes = fecha_nacimiento.split("-")
                anio, mes, dia = partes[0], partes[1], partes[2]
            elif "/" in fecha_nacimiento:
                partes = fecha_nacimiento.split("/")
                dia, mes, anio = partes[0], partes[1], partes[2]
        except Exception:
            pass
    fecha_nacimiento_dia = ft.TextField(label="Día", value=dia, width=60, max_length=2, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["fecha_nacimiento_dia"])), error_text=errores["fecha_nacimiento_dia"],
        on_change=validar_fecha_nacimiento_dia)
    fecha_nacimiento_mes = ft.TextField(label="Mes", value=mes, width=60, max_length=2, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["fecha_nacimiento_mes"])), error_text=errores["fecha_nacimiento_mes"],
        on_change=validar_fecha_nacimiento_mes)
    fecha_nacimiento_anio = ft.TextField(label="Año", value=anio, width=80, max_length=4, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["fecha_nacimiento_anio"])), error_text=errores["fecha_nacimiento_anio"],
        on_change=validar_fecha_nacimiento_anio)
    # Dropdown sexo
    sexo = ft.Dropdown(
        label="Sexo",
        border_color=color_tematica,
        options=[
            ft.dropdown.Option(key="Male", text="Masculino"),
            ft.dropdown.Option(key="Female", text="Femenino"),
            ft.dropdown.Option(key="Other", text="Otro")
        ],
        value=cliente.get("sexo", None),
        label_style=ft.TextStyle(color=color_letras),
        text_style=ft.TextStyle(color=color_letras)
    )
    switch_medical = ft.Switch(label="Apta Médica", value=bool(cliente.get("apta_medica", False)), active_color=color_tematica, label_style=ft.TextStyle(color=color_letras))
    # Fechas inicio y vencimiento separadas
    fecha_inicio_val = cliente.get("fecha_inicio", "")
    ini_dia, ini_mes, ini_anio = "", "", ""
    if fecha_inicio_val:
        try:
            if "-" in fecha_inicio_val:
                partes = fecha_inicio_val.split("-")
                ini_anio, ini_mes, ini_dia = partes[0], partes[1], partes[2]
            elif "/" in fecha_inicio_val:
                partes = fecha_inicio_val.split("/")
                ini_dia, ini_mes, ini_anio = partes[0], partes[1], partes[2]
        except Exception:
            pass
    fecha_inicio_dia = ft.TextField(label="Día", value=ini_dia, width=60, max_length=2, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["fecha_inicio_dia"])), error_text=errores["fecha_inicio_dia"],
        on_change=validar_fecha_inicio_dia)
    fecha_inicio_mes = ft.TextField(label="Mes", value=ini_mes, width=60, max_length=2, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["fecha_inicio_mes"])), error_text=errores["fecha_inicio_mes"],
        on_change=validar_fecha_inicio_mes)
    fecha_inicio_anio = ft.TextField(label="Año", value=ini_anio, width=80, max_length=4, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["fecha_inicio_anio"])), error_text=errores["fecha_inicio_anio"],
        on_change=validar_fecha_inicio_anio)

    fecha_vencimiento_val = cliente.get("fecha_vencimiento", "")
    ven_dia, ven_mes, ven_anio = "", "", ""
    if fecha_vencimiento_val:
        try:
            if "-" in fecha_vencimiento_val:
                partes = fecha_vencimiento_val.split("-")
                ven_anio, ven_mes, ven_dia = partes[0], partes[1], partes[2]
            elif "/" in fecha_vencimiento_val:
                partes = fecha_vencimiento_val.split("/")
                ven_dia, ven_mes, ven_anio = partes[0], partes[1], partes[2]
        except Exception:
            pass
    fecha_vencimiento_dia = ft.TextField(label="Día", value=ven_dia, width=60, max_length=2, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["fecha_vencimiento_dia"])), error_text=errores["fecha_vencimiento_dia"],
        on_change=validar_fecha_vencimiento_dia)
    fecha_vencimiento_mes = ft.TextField(label="Mes", value=ven_mes, width=60, max_length=2, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["fecha_vencimiento_mes"])), error_text=errores["fecha_vencimiento_mes"],
        on_change=validar_fecha_vencimiento_mes)
    fecha_vencimiento_anio = ft.TextField(label="Año", value=ven_anio, width=80, max_length=4, bgcolor=config["color_fondo"], border_radius=8, border_color=color_tematica,
        text_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=label_color(errores["fecha_vencimiento_anio"])), error_text=errores["fecha_vencimiento_anio"],
        on_change=validar_fecha_vencimiento_anio)
    # Imagen
    imagen_cliente = ft.Image(src=f"{IMAGE_DIR}{dni_actualizado}.png" if os.path.exists(f"{IMAGE_DIR}{dni_actualizado}.png") else f"{IMAGE_DIR}default.png", width=150, height=150)
    btn_cambiar_foto = ft.ElevatedButton(text="🖼️ Cambiar Foto", on_click=lambda e: seleccionar_foto_cliente(page, imagen_cliente), style=ft.ButtonStyle(bgcolor=color_tematica, color=color_letras))
    btn_guardar_cambios = ft.ElevatedButton(
        text="💾 Guardar Cambios",
        on_click=lambda e: guardar_cambios(
            cliente, dni, [
                nombre, apellido, sexo,
                fecha_nacimiento_dia, fecha_nacimiento_mes, fecha_nacimiento_anio,
                email, enfermedades,
                fecha_inicio_dia, fecha_inicio_mes, fecha_inicio_anio,
                fecha_vencimiento_dia, fecha_vencimiento_mes, fecha_vencimiento_anio
            ], switch_medical, imagen_cliente, color_letras, color_tematica, page, cambiar_vista, cerrar_panel_detalles
        ),
        style=ft.ButtonStyle(bgcolor=color_tematica, color=color_letras)
    )
    btn_cancelar = ft.ElevatedButton(
        text="❌ Cancelar",
        on_click=(lambda e: cerrar_panel_edicion(page)),
        style=ft.ButtonStyle(bgcolor=color_tematica, color="red")
    )
    panel_edicion = ft.Container(
        width=500*scale,
        padding=ft.padding.only(top=5, left=16*scale, right=16*scale, bottom=16*scale),
        bgcolor=config["color_fondo"],
        border_radius=10,
        border=ft.border.all(3, color_tematica),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=10),
        content=ft.Column([
            ft.Text(f"Editar Cliente: {cliente['nombre']} {cliente['apellido']}", size=22*scale, weight="bold", color=color_letras),
            imagen_cliente,
            nombre,
            apellido,
            dni,
            email,
            ft.Row([
                ft.Text("Fecha de Nacimiento", size=14, color=color_letras, width=150),
                fecha_nacimiento_dia,
                fecha_nacimiento_mes,
                fecha_nacimiento_anio
            ], spacing=5, alignment="start"),
            sexo,
            enfermedades,
            switch_medical,
            btn_cambiar_foto,
            ft.Row([
                ft.Text("Inicio de Membresía", size=14, color=color_letras, width=150),
                fecha_inicio_dia,
                fecha_inicio_mes,
                fecha_inicio_anio
            ], spacing=5, alignment="start"),
            ft.Row([
                ft.Text("Vencimiento de Membresía", size=14, color=color_letras, width=150),
                fecha_vencimiento_dia,
                fecha_vencimiento_mes,
                fecha_vencimiento_anio
            ], spacing=5, alignment="start"),
            ft.Row([btn_guardar_cambios, btn_cancelar], alignment=ft.MainAxisAlignment.END, spacing=10*scale)
        ], spacing=16*scale, scroll="always"),
        expand=False,
        height=page.window.height if hasattr(page.window, 'height') else 700*scale
    )
    panel_edicion.is_edicion_panel = True
    return panel_edicion

# 🔹 Selección de foto
def seleccionar_foto_cliente(page, imagen_cliente):
    global temp_image_path
    file_picker = ft.FilePicker(on_result=lambda e: actualizar_foto_cliente(e.files, imagen_cliente))
    page.overlay.append(file_picker)
    page.update()
    file_picker.pick_files(allow_multiple=False)

# 🔹 Actualización de la foto del cliente
def actualizar_foto_cliente(files, imagen_cliente):
    global temp_image_path
    if files and files[0].path.endswith((".jpg", ".png")):
        temp_image_path = files[0].path
        imagen_cliente.src = temp_image_path
        imagen_cliente.update()

# 🔹 Cancelar edición
def cancelar_edicion(page):
    # Cierra el modal global si existe
    if hasattr(page, "cliente_panel_modal"):
        page.cliente_panel_modal.open = False
    # Elimina cualquier AlertDialog abierto del overlay sin reasignar la lista
    to_remove = [ctrl for ctrl in page.overlay if isinstance(ctrl, ft.AlertDialog)]
    for ctrl in to_remove:
        page.overlay.remove(ctrl)
    page.update()

# 🔹 Cancelar solo edición (no cerrar detalle)
def cerrar_panel_edicion(page):
    # Elimina solo el panel de edición del overlay
    to_remove = [ctrl for ctrl in page.overlay if getattr(ctrl, 'is_edicion_panel', False)]
    for ctrl in to_remove:
        page.overlay.remove(ctrl)
    page.update()

def registrar_movimiento(tipo, cliente):
    conn = conectar_db()
    if conn is None:
        print("❌ Error: No se pudo conectar a la base de datos.")
        return

    cursor = conn.cursor()
    query = """INSERT INTO historial_movimientos (tipo, nombre, apellido, dni, fecha) VALUES (?, ?, ?, ?, datetime('now'))"""
    cursor.execute(query, (tipo, cliente.get("nombre", "No especificado"), cliente.get("apellido", "No especificado"), cliente.get("dni", "No especificado")))

    conn.commit()
    conn.close()
    print(f"📌 Movimiento registrado: {tipo} - {cliente['nombre']} {cliente['apellido']}")



def guardar_cambios(cliente, edit_dni, fields, switch_medical, imagen_cliente, color_letras, color_tematica, page, cambiar_vista=None, cerrar_panel_detalles=None):
    import os, shutil, sqlite3
    import flet as ft
    from views.verdetalle import vista_detalles_cliente
    from views.dashboard import vista_dashboard  # Importamos vista_dashboard
    global temp_image_path

    nuevo_dni = edit_dni.value.strip() or cliente.get("dni")
    if not nuevo_dni:
        print("⚠️ Error: DNI nuevo inválido, verifique la entrada.")
        return
    # Validar campos obligatorios (fecha_nacimiento ahora es obligatoria)
    campos_obligatorios = [fields[0], fields[1], fields[2], fields[3], fields[5], fields[6], edit_dni]
    for campo in campos_obligatorios:
        if not campo.value.strip():
            print(f"❌ Error: El campo obligatorio '{campo.label}' está vacío.")
            return

    # Validar que no haya errores en los campos
    # Busca error_text en todos los campos relevantes
    campos_validacion = [fields[0], fields[1], fields[6], fields[3], fields[4], fields[5], fields[8], fields[9], fields[10], fields[11], fields[12], fields[13]]
    for campo in campos_validacion:
        if getattr(campo, "error_text", None):
            print(f"❌ Error de validación en '{campo.label}': {campo.error_text}")
            return

    # Armar fecha de nacimiento desde los campos separados
    dia = fields[3].value.strip()
    mes = fields[4].value.strip()
    anio = fields[5].value.strip()
    fecha_nacimiento_norm = ""
    if dia and mes and anio:
        try:
            fecha_nacimiento_norm = f"{anio}-{mes.zfill(2)}-{dia.zfill(2)}"
        except Exception:
            fecha_nacimiento_norm = ""
    # Armar fecha de inicio y vencimiento desde los campos separados
    ini_dia = fields[8].value.strip()
    ini_mes = fields[9].value.strip()
    ini_anio = fields[10].value.strip()
    fecha_inicio_norm = ""
    if ini_dia and ini_mes and ini_anio:
        try:
            fecha_inicio_norm = f"{ini_anio}-{ini_mes.zfill(2)}-{ini_dia.zfill(2)}"
        except Exception:
            fecha_inicio_norm = ""
    ven_dia = fields[11].value.strip()
    ven_mes = fields[12].value.strip()
    ven_anio = fields[13].value.strip()
    fecha_vencimiento_norm = ""
    if ven_dia and ven_mes and ven_anio:
        try:
            fecha_vencimiento_norm = f"{ven_anio}-{ven_mes.zfill(2)}-{ven_dia.zfill(2)}"
        except Exception:
            fecha_vencimiento_norm = ""
    # La edad no se guarda en la base de datos, se calcula dinámicamente en la app
    # Corregir el valor de enfermedades: si es el texto por defecto, guardar vacío
    enfermedades_valor = fields[7].value.strip()
    if enfermedades_valor == "Sin enfermedades registradas":
        enfermedades_valor = ""

    def confirmar_guardado(e):
        print(f"[DEBUG] Botón de confirmación presionado: {e.control.text}")
        # Cerrar y eliminar el diálogo ANTES de cualquier otra acción
        if dialogo_confirmacion.open:
            dialogo_confirmacion.open = False
            page.update()
        try:
            if dialogo_confirmacion in page.overlay:
                page.overlay.remove(dialogo_confirmacion)
        except Exception as ex:
            print(f"[DEBUG] Error al eliminar el diálogo: {ex}")
        if e.control.text == "Sí":
            print("[DEBUG] Confirmado: se procederá a guardar los cambios en la base de datos.")
            conn = conectar_db()
            if conn is None:
                print("❌ Error: No se pudo conectar a la base de datos.")
                return

            cursor = conn.cursor()

            try:
                cursor.execute("SELECT * FROM clientes WHERE dni=?", (nuevo_dni,))
                cliente_existente = cursor.fetchone()


                if cliente_existente:
                    print("[DEBUG] Cliente encontrado, actualizando datos...")
                    # Detectar cambios y armar nota
                    campos = ["nombre", "apellido", "sexo", "fecha_nacimiento", "email", "enfermedades", "apta_medica", "fecha_inicio", "fecha_vencimiento"]
                    valores_nuevos = [
                        fields[0].value.strip(),  # nombre
                        fields[1].value.strip(),  # apellido
                        fields[2].value.strip(),  # sexo
                        fecha_nacimiento_norm,    # fecha_nacimiento
                        fields[6].value.strip(),  # email
                        enfermedades_valor,       # enfermedades
                        int(switch_medical.value),# apta_medica
                        fecha_inicio_norm,        # fecha_inicio
                        fecha_vencimiento_norm    # fecha_vencimiento
                    ]
                    # Mapear la fila a un diccionario por nombre de columna
                    colnames = [desc[0] for desc in cursor.description]
                    cliente_dict = dict(zip(colnames, cliente_existente))
                    valores_anteriores = [
                        int(cliente_dict[campo]) if campo == "apta_medica" else str(cliente_dict.get(campo, ""))
                        for campo in campos
                    ]
                    notas_mod = []
                    for i, campo in enumerate(campos):
                        old = valores_anteriores[i]
                        new = valores_nuevos[i]
                        if str(old) != str(new):
                            notas_mod.append(f"{campo}({old}) = {new}")
                    nota_final = "\n".join(notas_mod) if notas_mod else "Modificación sin cambios detectados"

                    cursor.execute("""UPDATE clientes SET nombre=?, apellido=?, sexo=?, fecha_nacimiento=?, email=?, enfermedades=?, apta_medica=?, fecha_inicio=?, fecha_vencimiento=?, dni=? WHERE dni=?""",
                        (fields[0].value.strip(), fields[1].value.strip(), fields[2].value.strip(), fecha_nacimiento_norm, fields[6].value.strip(), enfermedades_valor,
                         int(switch_medical.value), fecha_inicio_norm, fecha_vencimiento_norm, nuevo_dni, cliente.get("dni")))
                    conn.commit()
                    print(f"[DEBUG] UPDATE rowcount: {cursor.rowcount}")
                    if cursor.rowcount > 0:
                        print(f"✅ Cliente con DNI {nuevo_dni} actualizado correctamente.")
                    else:
                        print(f"⚠️ No se actualizó ningún cliente. Verifica el DNI original y el nuevo.")

                    # Registrar movimiento de modificación con nota detallada
                    from datetime import datetime
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        cursor.execute('''INSERT INTO historial_movimientos (tipo, nombre, apellido, dni, fecha, notas) VALUES (?, ?, ?, ?, ?, ?)''',
                            ("Modificación", fields[0].value.strip(), fields[1].value.strip(), nuevo_dni, now, nota_final))
                    except Exception:
                        cursor.execute('''INSERT INTO historial_movimientos (tipo, nombre, apellido, dni, fecha) VALUES (?, ?, ?, ?, ?)''',
                            ("Modificación", fields[0].value.strip(), fields[1].value.strip(), nuevo_dni, now))
                    conn.commit()

                else:
                    print(f"⚠️ Error: No se encontró cliente con DNI {nuevo_dni} en la base de datos.")
                    return

                # Guardar la imagen si se ha cambiado
                if temp_image_path and os.path.exists(temp_image_path):
                    print(f"[DEBUG] Imagen temporal detectada: {temp_image_path}")
                    destino_imagen = os.path.join("database/images", f"{nuevo_dni}.png")
                    shutil.copy(temp_image_path, destino_imagen)
                    cursor.execute("UPDATE clientes SET foto=? WHERE dni=?", (destino_imagen, nuevo_dni))
                    conn.commit()
                    imagen_cliente.src = destino_imagen + "?updated=" + str(os.path.getmtime(destino_imagen))
                    imagen_cliente.update()
                    print(f"[DEBUG] Imagen actualizada en {destino_imagen}")

                # Cerrar el modal global después de guardar (antes de navegar)
                try:
                    if hasattr(page, "cliente_panel_modal"):
                        print("[DEBUG] Cerrando modal de edición de cliente.")
                        page.cliente_panel_modal.open = False
                        page.update()
                    # Cerrar panel de detalle si existe
                    if cerrar_panel_detalles:
                        print("[DEBUG] Cerrando panel de detalle de cliente.")
                        cerrar_panel_detalles()
                    # Eliminar cualquier AlertDialog abierto
                    to_remove = [ctrl for ctrl in page.overlay if isinstance(ctrl, ft.AlertDialog)]
                    for ctrl in to_remove:
                        page.overlay.remove(ctrl)
                    page.update()
                    # --- Refrescar dashboard y tabla como en ver detalle (imitando eliminar_cliente) ---
                    from views.dashboard import vista_dashboard
                    page.clean()
                    page.add(vista_dashboard(page))
                    page.update()
                except Exception as ex:
                    print(f"[DEBUG] No se pudo refrescar/cerrar tras editar: {ex}")
                # ---
                # 🔄 Navegación centralizada tras guardar
                if cambiar_vista:
                    print("🔄 Navegando al dashboard usando cambiar_vista...")
                    cambiar_vista("/")  # Redirige a la ruta principal/dashboard
                else:
                    print("⚠️ cambiar_vista no proporcionado, no se puede navegar al dashboard automáticamente.")

            except Exception as ex:
                print(f"❌ Error al actualizar cliente: {ex}")

            finally:
                conn.close()

            # Cerrar el modal global después de guardar
            if hasattr(page, "cliente_panel_modal"):
                print("[DEBUG] Cerrando modal de edición de cliente.")
                page.cliente_panel_modal.open = False
                page.update()
        else:
            print("[DEBUG] Cancelado: no se guardaron los cambios.")

    def cerrar_dialogo_confirmacion(e=None):
        print("[DEBUG] Diálogo de confirmación cerrado sin guardar.")
        if dialogo_confirmacion.open:
            dialogo_confirmacion.open = False
            page.update()
        try:
            if dialogo_confirmacion in page.overlay:
                page.overlay.remove(dialogo_confirmacion)
        except Exception as ex:
            print(f"[DEBUG] Error al eliminar el diálogo: {ex}")

    dialogo_confirmacion = ft.AlertDialog(
        title=ft.Text("Confirmar cambios"),
        content=ft.Text("¿Estás seguro de que deseas guardar los cambios?"),
        actions=[
            ft.TextButton("Sí", on_click=confirmar_guardado),
            ft.TextButton("No", on_click=cerrar_dialogo_confirmacion),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    print("[DEBUG] Mostrando diálogo de confirmación de guardado.")
    if dialogo_confirmacion not in page.overlay:
        page.overlay.append(dialogo_confirmacion)
    dialogo_confirmacion.open = True
    page.update()
