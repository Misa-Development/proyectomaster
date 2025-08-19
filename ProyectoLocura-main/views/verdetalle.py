# Función optimizada para actualizar la página de forma segura
def actualizar_pagina_seguro(page, intentos=3):
    """Actualiza la página de forma segura con reintentos automáticos y verificaciones adicionales"""
    if page is None:
        print("[DEBUG] Page es None, no se puede actualizar")
        return False
        
    for intento in range(intentos):
        try:
            # Verificar que la página sigue siendo válida
            if not hasattr(page, 'update'):
                print(f"[DEBUG] Page no tiene método update (intento {intento + 1})")
                return False
                
            # Intentar la actualización
            page.update()
            print(f"[DEBUG] Página actualizada exitosamente (intento {intento + 1})")
            return True
            
        except Exception as ex:
            print(f"[DEBUG] Error actualizando página (intento {intento + 1}): {ex}")
            
            # En el último intento, intentar estrategias alternativas
            if intento == intentos - 1:
                print(f"[DEBUG] Se agotaron los intentos de actualización")
                
                # Estrategia alternativa: Verificar si hay overlay problemáticos
                try:
                    if hasattr(page, 'overlay') and len(page.overlay) > 10:
                        print(f"[DEBUG] Demasiados overlays ({len(page.overlay)}), limpiando...")
                        # Mantener solo los últimos 5 overlays
                        page.overlay = page.overlay[-5:]
                        page.update()
                        print("[DEBUG] Overlays limpiados y página actualizada")
                        return True
                except Exception as ex_alt:
                    print(f"[DEBUG] Estrategia alternativa falló: {ex_alt}")
                
                return False
            
            # Esperar un poco antes del siguiente intento
            import time
            time.sleep(0.1 * (intento + 1))  # Aumentar tiempo de espera progresivamente
            
    return False

# Función simple para mostrar alertas en este módulo
def mostrar_alerta(page, titulo, mensaje, color, on_close=None):
    def cleanup(e=None):
        try:
            print("[DEBUG] Cerrando alerta...")
            if dialog in page.overlay:
                page.overlay.remove(dialog)
                print("[DEBUG] Alerta removida del overlay")
            dialog.open = False
            
            # Actualización inmediata para cerrar sin delay
            try:
                page.update()
                print("[DEBUG] Alerta cerrada exitosamente sin delay")
            except Exception as update_ex:
                print(f"[DEBUG] Error actualizando tras cerrar alerta: {update_ex}")
            
            if on_close:
                on_close(e)
        except Exception as ex:
            print(f"[DEBUG] Error en cleanup de alerta: {ex}")
    
    config = cargar_configuracion()
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(titulo, weight="bold", color=config["color_letras"], size=18),
        content=ft.Text(mensaje, size=14, color=config["color_letras"]),
        bgcolor=config["color_fondo"],
        shape=ft.RoundedRectangleBorder(radius=10),
        actions=[
            ft.TextButton(
                "Cerrar",
                on_click=cleanup,
                style=ft.ButtonStyle(color=config["color_tematica"])
            )
        ]
        # Eliminado on_dismiss para evitar dobles llamadas
    )
    
    try:
        page.overlay.append(dialog)
        dialog.open = True
        # Usar actualización simple en lugar de la función compleja
        page.update()
        print("[DEBUG] Alerta mostrada exitosamente")
    except Exception as ex:
        print(f"[DEBUG] Error mostrando alerta: {ex}")
import flet as ft
import json
import os
import sqlite3
from database.db import conectar_db, eliminar_cliente_por_dni
from views.vistaedicion import *
from views.tablacliente import actualizar_lista_clientes
from datetime import datetime  

# Inicializar caché de configuración global
_config_cache = None

CONFIG_FILE = "config.json"
IMAGE_DIR = "database/images/"

# 🔹 Función para invalidar el cache de configuración
def invalidar_cache_configuracion():
    """Invalida el cache de configuración para forzar la recarga"""
    global _config_cache
    _config_cache = None
    print("[DEBUG] Cache de configuración invalidado")

# 🔹 Cargar configuración
def cargar_configuracion():
    global _config_cache
    # SIEMPRE recargar desde archivo para obtener cambios en tiempo real
    try:
        with open(CONFIG_FILE, "r") as f:
            _config_cache = json.load(f)
        print("[DEBUG] Configuración recargada desde archivo")
    except FileNotFoundError:
        _config_cache = {
            "color_fondo": "#FFFFFF",
            "color_tematica": "#E8E8E8",
            "color_letras": "#000000",
            "nombre_gimnasio": "Mi Gimnasio"
        }
        print("[DEBUG] Usando configuración por defecto")
    # Validar color_tematica
    color = _config_cache.get("color_tematica", "#E8E8E8")
    if not isinstance(color, str) or not color.startswith("#") or len(color) not in (7, 9):
        print(f"[DEBUG] color_tematica inválido en config: {color}, usando #E8E8E8")
        _config_cache["color_tematica"] = "#E8E8E8"
    return _config_cache

def obtener_dni(cliente):
    if isinstance(cliente, sqlite3.Row):
        cliente = dict(cliente)  # Convertir `Row` a diccionario

    dni = cliente.get("dni")
    if not dni:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT dni FROM clientes WHERE nombre=? AND apellido=?", (cliente.get("nombre"), cliente.get("apellido")))
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else None

    return dni

# 🔹 Obtener imagen del cliente
def obtener_imagen_cliente(cliente):
    if isinstance(cliente, sqlite3.Row):
        cliente = dict(cliente)
    dni = obtener_dni(cliente)
    if not dni:
        return os.path.join(IMAGE_DIR, "default.png")
    foto_path = cliente.get("foto")
    if foto_path and os.path.exists(foto_path):
        return foto_path
    ruta_por_dni = os.path.join(IMAGE_DIR, f"{dni}.png")
    if os.path.exists(ruta_por_dni):
        return ruta_por_dni
    return os.path.join(IMAGE_DIR, "default.png")

def cerrar_dialogo(dialog, page):
    """Cierra un diálogo de forma segura con múltiples fallbacks"""
    try:
        if dialog is None:
            print("[DEBUG] Dialog es None, no hay nada que cerrar")
            return
            
        print(f"[DEBUG] Intentando cerrar diálogo: {type(dialog)}")
        
        # Paso 1: Cerrar el diálogo
        if hasattr(dialog, 'open'):
            dialog.open = False
            print("[DEBUG] Dialog.open = False ejecutado")
        
        # Paso 2: Remover del overlay si está ahí
        if hasattr(page, 'overlay') and dialog in page.overlay:
            page.overlay.remove(dialog)
            print("[DEBUG] Dialog removido del overlay")
        
        # Paso 3: Actualizar página de forma segura
        if actualizar_pagina_seguro(page):
            print("[DEBUG] Página actualizada exitosamente")
        else:
            print("[DEBUG] Falló actualización de página, pero diálogo cerrado")
            
    except Exception as ex:
        print(f"[DEBUG] Error cerrando diálogo: {ex}")
        # Fallback 1: Intentar solo cerrar sin actualizar
        try:
            if dialog and hasattr(dialog, 'open'):
                dialog.open = False
                print("[DEBUG] Fallback 1: Solo cerrar diálogo ejecutado")
        except Exception as ex2:
            print(f"[DEBUG] Fallback 1 falló: {ex2}")
        
        # Fallback 2: Intentar actualizar página sin tocar el diálogo
        try:
            page.update()
            print("[DEBUG] Fallback 2: Actualización directa ejecutada")
        except Exception as ex3:
            print(f"[DEBUG] Fallback 2 falló: {ex3}")
            print("[DEBUG] Todos los fallbacks fallaron, pero la app debería continuar")

# 🔹 Vista detalles del cliente
# Ahora usa el modal global y page, no cliente_panel

def vista_detalles_cliente(cliente, color_letras, color_tematica, page, cerrar_panel_detalles, mostrar_detalles_cliente, pos_x=None, pos_y=None):
    # Recargar configuración en tiempo real para obtener colores actualizados
    config_actual = cargar_configuracion()
    color_letras = config_actual["color_letras"]
    color_tematica = config_actual["color_tematica"]
    print(f"[DEBUG] Colores recargados en tiempo real - Letras: {color_letras}, Temática: {color_tematica}")
    
    # Recargar datos del cliente desde la base de datos usando el DNI antes de mostrar el detalle
    if isinstance(cliente, sqlite3.Row):
        cliente = dict(cliente)
    dni_cliente = obtener_dni(cliente)
    
    # SIEMPRE recargar datos completos desde la base de datos para asegurar que tenemos toda la información
    if dni_cliente:
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes WHERE dni=?", (dni_cliente,))
            row = cursor.fetchone()
            if row:
                cliente = dict(row)  # Usar datos completos de la BD
                print(f"[DEBUG] Datos completos cargados - Email: {cliente.get('email', 'NO ENCONTRADO')}, Nombre: {cliente.get('nombre')}")
            else:
                print(f"[DEBUG] No se encontró cliente con DNI: {dni_cliente}")
            conn.close()
        except Exception as ex:
            print(f"[DEBUG] Error cargando datos completos del cliente: {ex}")
    
    # Marcar el panel como abierto para este cliente
    page._detalle_abierto_dni = dni_cliente

    print(f"[DEBUG] color_tematica usado en detalle: {color_tematica}")
    def vista_estatica(cliente, page):
        def mostrar_popup_renovacion(e=None):
            # Deshabilitar botones mientras se procesa para evitar doble click
            if hasattr(page, "_popup_renovando") and page._popup_renovando:
                return
            page._popup_renovando = True
            meses = [1]  # lista mutable para el contador
            def actualizar_label():
                label_meses.value = str(meses[0])
                try:
                    label_meses.update()
                except Exception as ex:
                    print(f"[DEBUG] Error actualizando label: {ex}")
            def sumar():
                meses[0] += 1
                actualizar_label()
            def restar():
                if meses[0] > 1:
                    meses[0] -= 1
                    actualizar_label()
            already_closed = {'value': False}
            import threading
            def abrir_desplegable():
                # Espera 0.005 segundos y abre el desplegable del último cliente seleccionado
                from views.dashboard import vista_dashboard
                if hasattr(page, 'abrir_ultimo_cliente'):
                    page.abrir_ultimo_cliente()

            def cerrar_y_cerrar_panel(e=None):
                if already_closed['value']:
                    return
                already_closed['value'] = True
                try:
                    print("[DEBUG] Navegando al dashboard tras renovación...")
                    from views.dashboard import vista_dashboard
                    page.clean()
                    page.add(vista_dashboard(page))
                    
                    # Usar actualización simple
                    try:
                        page.update()
                        print("[DEBUG] Dashboard actualizado exitosamente")
                    except Exception as update_ex:
                        print(f"[DEBUG] Error actualizando dashboard: {update_ex}")
                    
                    if cerrar_panel_detalles:
                        cerrar_panel_detalles()
                except Exception as ex:
                    print(f"[DEBUG] Error navegando al dashboard: {ex}")
                    # Fallback: solo cerrar el panel
                    if cerrar_panel_detalles:
                        cerrar_panel_detalles()
            label_meses = ft.Text(str(meses[0]), size=22, weight="bold", color=color_letras)
            popup_renovacion = None
            def cancelar(ev=None):
                nonlocal popup_renovacion
                print("[DEBUG] Cancelando renovación (versión mejorada)...")
                
                # Paso 1: Cambiar flags
                page._popup_renovando = False
                
                # Paso 2: Cerrar el popup
                try:
                    popup_renovacion.open = False
                    print("[DEBUG] Popup cerrado")
                except Exception as ex:
                    print(f"[DEBUG] Error cerrando popup: {ex}")
                
                # Paso 3: Actualización mínima e inmediata para eliminar el delay
                try:
                    page.update()
                    print("[DEBUG] Actualización inmediata exitosa")
                except Exception as update_ex:
                    print(f"[DEBUG] Actualización falló pero popup cerrado: {update_ex}")
                
                print("[DEBUG] Cancelación completada sin delay")
            def completar(ev=None):
                nonlocal popup_renovacion
                try:
                    fecha_venc = cliente.get("fecha_vencimiento", "")
                    if not fecha_venc:
                        raise Exception("Fecha de vencimiento no disponible")
                    try:
                        if "/" in fecha_venc:
                            dt = datetime.strptime(fecha_venc, "%d/%m/%Y")
                        else:
                            dt = datetime.strptime(fecha_venc, "%Y-%m-%d")
                    except Exception:
                        mostrar_alerta(page, "Error", "Formato de fecha de vencimiento inválido", "red")
                        page._popup_renovando = False
                        return
                    from dateutil.relativedelta import relativedelta
                    nueva_fecha = dt + relativedelta(months=meses[0])
                    nueva_fecha_str = nueva_fecha.strftime("%d/%m/%Y") if "/" in fecha_venc else nueva_fecha.strftime("%Y-%m-%d")
                    conn = conectar_db()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE clientes SET fecha_vencimiento=? WHERE dni=?", (nueva_fecha_str, cliente["dni"]))
                    # Registrar movimiento de renovación con nota
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    notas = f"Se renovó {meses[0]} {'mes' if meses[0] == 1 else 'meses'}"
                    try:
                        cursor.execute('''INSERT INTO historial_movimientos (tipo, nombre, apellido, dni, fecha, notas) VALUES (?, ?, ?, ?, ?, ?)''',
                            ("Renovación", cliente.get("nombre", "No especificado"), cliente.get("apellido", "No especificado"), cliente.get("dni", "No especificado"), now, notas))
                    except Exception:
                        cursor.execute('''INSERT INTO historial_movimientos (tipo, nombre, apellido, dni, fecha) VALUES (?, ?, ?, ?, ?)''',
                            ("Renovación", cliente.get("nombre", "No especificado"), cliente.get("apellido", "No especificado"), cliente.get("dni", "No especificado"), now))
                    conn.commit()
                    conn.close()
                    cliente["fecha_vencimiento"] = nueva_fecha_str
                    
                    # Cerrar popup de forma segura
                    try:
                        popup_renovacion.open = False
                        if popup_renovacion in page.overlay:
                            page.overlay.remove(popup_renovacion)
                    except Exception:
                        pass
                    
                    page._popup_renovando = False
                    
                    # Actualizar página de forma simple y segura
                    try:
                        page.update()
                        print("[DEBUG] Página actualizada tras renovación")
                    except Exception as update_ex:
                        print(f"[DEBUG] Error actualizando tras renovación: {update_ex}")
                        # No es crítico si falla la actualización
                    
                    mostrar_alerta(
                        page,
                        "Renovación exitosa",
                        f"Nueva fecha de vencimiento: {nueva_fecha_str}",
                        "green",
                        on_close=cerrar_y_cerrar_panel
                    )
                except Exception as ex:
                    page._popup_renovando = False
                    mostrar_alerta(page, "Error", f"No se pudo renovar: {ex}", "red")
            popup_renovacion = ft.AlertDialog(
                modal=True,
                title=ft.Text("Renovación de Membresía", size=18, weight="bold", color=color_letras),
                content=ft.Container(
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.REMOVE, on_click=lambda e: restar(), icon_color=color_tematica),
                        label_meses,
                        ft.IconButton(icon=ft.Icons.ADD, on_click=lambda e: sumar(), icon_color=color_tematica),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    bgcolor=cargar_configuracion()["color_fondo"],
                    border=ft.border.all(3, color_tematica),
                    border_radius=10,
                    padding=16
                ),
                bgcolor=cargar_configuracion()["color_fondo"],
                shape=ft.RoundedRectangleBorder(radius=10),
                actions=[
                    ft.TextButton("Completar", on_click=completar, style=ft.ButtonStyle(color=color_tematica)),
                    ft.TextButton("Cancelar", on_click=cancelar, style=ft.ButtonStyle(color=ft.Colors.RED)),
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            try:
                page.overlay.append(popup_renovacion)
                popup_renovacion.open = True
                # Usar actualización simple en lugar de la función compleja
                page.update()
                print("[DEBUG] Popup renovación mostrado exitosamente")
            except Exception as ex:
                print(f"[DEBUG] Error mostrando popup renovación: {ex}")
                page._popup_renovando = False
                # Fallback: intentar mostrar sin overlay
                try:
                    popup_renovacion.open = True
                    page.update()
                    print("[DEBUG] Popup mostrado sin overlay")
                except Exception as ex2:
                    print(f"[DEBUG] Fallback popup también falló: {ex2}")
                    page._popup_renovando = False
        print(f"🔍 DNI en vista_estatica: {dni_cliente}")

        def mostrar_imagen_grande(e=None):
            # Optimización: usar directamente la ruta de la imagen sin recálculo ni render extra
            src_img = obtener_imagen_cliente(cliente)
            zoom_state = {'zoom': 1.0}
            imagen_zoom = ft.Image(
                src=src_img,
                width=600,
                height=600,
                fit=ft.ImageFit.CONTAIN,
                error_content=ft.Text("Imagen no disponible", color="red")
            )
            def zoom_in(ev=None):
                zoom_state['zoom'] = min(zoom_state['zoom'] + 0.1, 3.0)
                imagen_zoom.width = 600 * zoom_state['zoom']
                imagen_zoom.height = 600 * zoom_state['zoom']
                try:
                    imagen_zoom.update()
                except Exception as ex:
                    print(f"[DEBUG] Error zoom in: {ex}")
                    
            def zoom_out(ev=None):
                zoom_state['zoom'] = max(zoom_state['zoom'] - 0.1, 0.5)
                imagen_zoom.width = 600 * zoom_state['zoom']
                imagen_zoom.height = 600 * zoom_state['zoom']
                try:
                    imagen_zoom.update()
                except Exception as ex:
                    print(f"[DEBUG] Error zoom out: {ex}")
            
            def cerrar_imagen_seguro(ev=None):
                """Función específica para cerrar imagen de forma segura - versión minimalista"""
                try:
                    print("[DEBUG] Cerrando imagen ampliada (modo seguro)...")
                    
                    # Paso 1: Solo cerrar el diálogo sin tocar overlay ni actualizar
                    dialogo_imagen.open = False
                    print("[DEBUG] Dialog.open = False ejecutado")
                    
                    # Paso 2: Intentar actualización mínima usando try-catch individual
                    try:
                        page.update()
                        print("[DEBUG] Actualización simple exitosa")
                    except Exception as update_ex:
                        print(f"[DEBUG] Actualización simple falló: {update_ex}")
                        # No hacer nada más, solo cerrar
                    
                    print("[DEBUG] Imagen cerrada en modo seguro")
                    
                except Exception as ex:
                    print(f"[DEBUG] Error en modo seguro: {ex}")
                    # Último recurso: solo intentar cerrar dialog
                    try:
                        dialogo_imagen.open = False
                        print("[DEBUG] Último recurso ejecutado")
                    except:
                        print("[DEBUG] Último recurso también falló")
                        pass
            
            dialogo_imagen = ft.AlertDialog(
                modal=True,
                bgcolor=cargar_configuracion()["color_fondo"],
                shape=ft.RoundedRectangleBorder(radius=10),
                content=ft.Container(
                    imagen_zoom,
                    alignment=ft.alignment.center,
                    padding=0,
                    bgcolor=cargar_configuracion()["color_fondo"]
                ),
                actions=[
                    ft.IconButton(icon=ft.Icons.REMOVE, tooltip="Zoom -", on_click=zoom_out, icon_color=color_tematica),
                    ft.IconButton(icon=ft.Icons.ADD, tooltip="Zoom +", on_click=zoom_in, icon_color=color_tematica),
                    ft.TextButton("Cerrar", on_click=cerrar_imagen_seguro, style=ft.ButtonStyle(color=color_tematica))
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER
                # Removido on_dismiss para evitar problemas de doble llamada
            )
            try:
                page.overlay.append(dialogo_imagen)
                dialogo_imagen.open = True
                # Usar actualización simple en lugar de la función compleja
                page.update()
                print("[DEBUG] Imagen grande mostrada exitosamente")
            except Exception as ex:
                print(f"[DEBUG] Error mostrando imagen grande: {ex}")
                # Fallback: intentar sin overlay
                try:
                    dialogo_imagen.open = True
                    page.update()
                    print("[DEBUG] Imagen mostrada sin overlay")
                except Exception as ex2:
                    print(f"[DEBUG] Fallback también falló: {ex2}")

        imagen_cliente = ft.GestureDetector(
            content=ft.Image(
                src=obtener_imagen_cliente(cliente),
                width=150,
                height=150,
                fit=ft.ImageFit.CONTAIN,
                border_radius=ft.border_radius.all(10),
                error_content=ft.Text("Imagen no disponible", color="red")
            ),
            on_tap=mostrar_imagen_grande
        )

        def cerrar_panel():
            cerrar_panel_detalles()
            # Refuerzo: si el menú desapareció del overlay, lo reinsertamos al inicio SOLO si existe una instancia previa
            try:
                # Buscar el menú lateral real por el atributo is_menu_panel
                menu = None
                for ctrl in page.overlay:
                    if getattr(ctrl, 'is_menu_panel', False):
                        menu = ctrl
                        break
                # Si no está en overlay pero sí en controls, lo reinsertamos
                if not menu:
                    for ctrl in page.controls:
                        if getattr(ctrl, 'is_menu_panel', False):
                            menu = ctrl
                            break
                    if menu:
                        page.overlay.insert(0, menu)
                        # Usar actualización simple
                        page.update()
                        print("[DEBUG] Menú reinsertado tras cerrar detalle")
            except Exception as ex:
                print(f"[DEBUG] Error asegurando menú en overlay tras cerrar detalle: {ex}")

        detalle_container = ft.Container(
            width=420,
            padding=24,
            bgcolor=cargar_configuracion()["color_fondo"],
            border_radius=16,
            border=ft.border.all(3, color_tematica),
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=16,
                color="#88888844",
                offset=ft.Offset(0, 4),
            ),
            left=pos_x if pos_x is not None else None,
            top=pos_y if pos_y is not None else None,
            alignment=ft.alignment.top_left if (pos_x is not None and pos_y is not None) else None,
            margin=ft.margin.only(top=15),
            content=ft.Column([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=color_tematica,
                        tooltip="Cerrar",
                        on_click=lambda e: cerrar_panel(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                    ),
                    ft.Container(
                        imagen_cliente,
                        width=90,
                        height=90,
                        border_radius=12,
                        bgcolor="#F5F5F5",
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(left=12, right=8)
                    ),
                    ft.Column([
                        ft.Text(f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}", size=22, weight="bold", color=color_tematica),
                        ft.Text(f"DNI: {dni_cliente if dni_cliente else 'No especificado'}", size=15, color=color_letras),
                        ft.Text(f"Actividad: {cliente.get('estado', 'No especificado')}", size=14, color=color_letras),
                    ], spacing=2, alignment=ft.alignment.top_left),
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                ft.Divider(height=18, color=color_tematica),
                ft.Text("Datos personales", size=16, weight="bold", color=color_tematica),
                ft.Row([
                    ft.Text("Sexo:", size=14, color=color_tematica, weight="bold"),
                    ft.Text(cliente.get("sexo", "No especificado"), size=14, color=color_letras),
                    ft.Text("Edad:", size=14, color=color_tematica, weight="bold"),
                    ft.Text(
                        str(
                            (lambda fn: (datetime.now().year - fn.year - ((datetime.now().month, datetime.now().day) < (fn.month, fn.day))) if fn else "No especificado")(
                                datetime.strptime(cliente.get("fecha_nacimiento", ""), "%Y-%m-%d") if cliente.get("fecha_nacimiento") else None
                            )
                        ),
                        size=14, color=color_letras
                    ),
                ], spacing=16),
                ft.Row([
                    ft.Text("Email:", size=14, color=color_tematica, weight="bold"),
                    ft.Text(cliente.get("email", "No especificado"), size=14, color=color_letras),
                ], spacing=16),
                ft.Row([
                ft.Text(f"Inicio:", size=14, color=color_tematica, weight="bold"),
                ft.Text(
                    datetime.strptime(cliente.get("fecha_inicio", "01/01/1970"), "%Y-%m-%d").strftime("%d/%m/%Y")
                    if cliente.get("fecha_inicio") and "-" in cliente.get("fecha_inicio") else cliente.get("fecha_inicio", "No especificado"),
                    size=14, color=color_letras),
                ft.Text("Vencimiento:", size=14, color=color_tematica, weight="bold"),
                ft.Text(
                    datetime.strptime(cliente.get("fecha_vencimiento", "01/01/1970"), "%Y-%m-%d").strftime("%d/%m/%Y")
                    if cliente.get("fecha_vencimiento") and "-" in cliente.get("fecha_vencimiento") else cliente.get("fecha_vencimiento", "No especificado"),
                    size=14, color=color_letras),
                ], spacing=16),
                ft.Row([
                    ft.Text("Apta Médica:", size=14, color=color_tematica, weight="bold"),
                    ft.Text("Sí" if cliente.get("apta_medica") else "No", size=14, color=color_letras),
                ], spacing=16),
                ft.Text("Enfermedades: ", size=14, color=color_tematica, weight="bold"),
                ft.Text(
                    cliente["enfermedades"] if cliente.get("enfermedades") not in (None, "", "No especificado") else "Sin enfermedades registradas",
                    size=14, color=color_letras
                ),
                ft.Divider(height=18, color=color_tematica),
                ft.Row([
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Container(
                            ft.Icon(ft.Icons.AUTORENEW, color="white", size=18),
                            width=24, height=24,
                            bgcolor="black",
                            border_radius=12,
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(right=4)
                        ),
                        ft.Text("Renovación", color=color_letras, size=14, weight="bold")
                    ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                    on_click=mostrar_popup_renovacion,
                    style=ft.ButtonStyle(
                        bgcolor=color_tematica,
                        color=color_letras,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(vertical=6, horizontal=8)
                    ),
                ),
                    ft.ElevatedButton(
                        text="✏️ Editar Cliente",
                        on_click=lambda e: editar_cliente(cliente, page, color_letras, color_tematica, cerrar_panel_detalles),
                        style=ft.ButtonStyle(bgcolor=color_tematica, color=color_letras, shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                    ft.ElevatedButton(
                        text="🗑️ Eliminar Cliente",
                        on_click=lambda e: confirmar_eliminacion(cliente, page),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.RED, color="white", shape=ft.RoundedRectangleBorder(radius=8)),
                    )
                ], alignment=ft.MainAxisAlignment.END, spacing=12)
            ], spacing=18, scroll="always"),
            expand=False,
        )
        return detalle_container

    def editar_cliente(cliente, page, color_letras, color_tematica, cerrar_panel):
        from views.vistaedicion import vista_edicion
        print(f"[DEBUG] Llamando editar_cliente para: {cliente.get('nombre')} {cliente.get('apellido')}")
        print(f"[DEBUG] cerrar_panel: {cerrar_panel}, page.cliente_panel_modal: {getattr(page, 'cliente_panel_modal', None)}")
        print(f"[DEBUG] color_tematica usado en edición: {color_tematica}")
        
        # IMPORTANTE: Recargar TODOS los datos del cliente desde la base de datos antes de editar
        dni_cliente = obtener_dni(cliente)
        if dni_cliente:
            try:
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clientes WHERE dni=?", (dni_cliente,))
                row = cursor.fetchone()
                if row:
                    cliente = dict(row)  # Usar todos los datos frescos de la BD
                    print(f"[DEBUG] Datos recargados para edición - Email: {cliente.get('email', 'NO ENCONTRADO')}")
                else:
                    print(f"[DEBUG] No se encontró cliente con DNI: {dni_cliente}")
                conn.close()
            except Exception as ex:
                print(f"[DEBUG] Error recargando datos del cliente: {ex}")
        
        # Función personalizada para navegar al dashboard después de editar
        def callback_edicion():
            try:
                # Cerrar el panel de detalles primero
                if cerrar_panel:
                    cerrar_panel()
                # Navegar al dashboard
                from views.dashboard import vista_dashboard
                page.clean()
                page.add(vista_dashboard(page))
                # Usar actualización simple
                page.update()
                print("[DEBUG] Dashboard actualizado tras edición")
            except Exception as ex:
                print(f"[DEBUG] Error en callback_edicion: {ex}")
        
        # Eliminar cualquier panel de edición o detalle previo del overlay
        try:
            for ctrl in list(page.overlay):
                if getattr(ctrl, 'is_edicion_panel', False) or (hasattr(ctrl, 'content') and isinstance(ctrl.content, ft.Column) and any(isinstance(c, ft.Text) and 'DNI:' in c.value for c in ctrl.content.controls)):
                    page.overlay.remove(ctrl)
        except Exception as ex:
            print(f"[DEBUG] Error limpiando overlays: {ex}")
        
        # Agregar el panel de edición como overlay lateral
        try:
            panel_edicion = vista_edicion(cliente, page, color_letras, color_tematica, cerrar_panel, callback_edicion)
            page.overlay.append(panel_edicion)
            # Usar actualización simple
            page.update()
            print("[DEBUG] Panel de edición mostrado")
        except Exception as ex:
            print(f"[DEBUG] Error mostrando panel de edición: {ex}")
            # Fallback: mostrar alerta de error
            mostrar_alerta(page, "Error", "No se pudo abrir el panel de edición", "red")

    def eliminar_cliente(cliente, cerrar_panel, page, motivo=None):
        dni_cliente = obtener_dni(cliente)
        conn = None
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if motivo:
                cursor.execute('''INSERT INTO historial_movimientos (tipo, nombre, apellido, dni, fecha, notas)
                                    VALUES (?, ?, ?, ?, ?, ?)''', ("Baja", cliente['nombre'], cliente['apellido'], dni_cliente, now, motivo))
            else:
                cursor.execute('''INSERT INTO historial_movimientos (tipo, nombre, apellido, dni, fecha)
                                    VALUES (?, ?, ?, ?, ?)''', ("Baja", cliente['nombre'], cliente['apellido'], dni_cliente, now))
            conn.commit()
            
            if eliminar_cliente_por_dni(dni_cliente):
                # Cerrar panel primero
                if cerrar_panel:
                    cerrar_panel()
                # Refresca la vista completa
                try:
                    from views.dashboard import vista_dashboard
                    page.clean()
                    page.add(vista_dashboard(page))
                    # Usar actualización simple
                    page.update()
                    print("[DEBUG] Dashboard refrescado tras eliminación")
                except Exception as ex:
                    print(f"[DEBUG] Error refrescando dashboard después de eliminar: {ex}")
                    
        except sqlite3.Error as e:
            print(f"Error al registrar la baja del cliente: {e}")
            raise  # Re-lanzar para que se maneje en eliminar_cliente_confirmado
        except Exception as e:
            print(f"Error general eliminando cliente: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def eliminar_cliente_confirmado(cliente, dialog, page, motivo):
        try:
            # Cerrar el diálogo primero
            dialog.open = False
            if dialog in page.overlay:
                page.overlay.remove(dialog)
            # Usar actualización simple
            page.update()
            print("[DEBUG] Diálogo de eliminación cerrado")
        except Exception as ex:
            print(f"[DEBUG] Error cerrando diálogo: {ex}")
        
        def cerrar_panel_wrapper():
            try:
                cerrar_panel_detalles()
            except Exception as ex:
                print(f"[DEBUG] Error cerrando panel: {ex}")
        
        try:
            eliminar_cliente(cliente, cerrar_panel_wrapper, page, motivo)
            
            def cerrar_exito(ev=None):
                try:
                    from views.dashboard import vista_dashboard
                    page.clean()
                    page.add(vista_dashboard(page))
                    # Usar actualización simple
                    page.update()
                    print("[DEBUG] Dashboard refrescado tras éxito")
                except Exception as ex:
                    print(f"[DEBUG] Error refrescando dashboard: {ex}")
            
            mostrar_alerta(
                page,
                "Eliminación exitosa",
                f"Cliente '{cliente.get('nombre', '')} {cliente.get('apellido', '')}' eliminado con éxito.",
                "green",
                on_close=cerrar_exito
            )
        except Exception as ex:
            print(f"[DEBUG] Error eliminando cliente: {ex}")
            mostrar_alerta(page, "Error", f"No se pudo eliminar el cliente: {ex}", "red")

    def confirmar_eliminacion(cliente, page):
        config = cargar_configuracion()
        motivo_text = ft.TextField(
            label="Motivo de la eliminación (obligatorio)",
            multiline=True,
            min_lines=3,
            max_lines=5,
            height=120,
            width=350,
            bgcolor=config["color_fondo"],
            border_color=color_tematica,
            border_radius=8,
            text_style=ft.TextStyle(color=color_letras),
            label_style=ft.TextStyle(color=color_letras),
            text_align=ft.TextAlign.CENTER,
            autofocus=True
        )
        
        def on_eliminar_click(e):
            motivo = motivo_text.value.strip()
            if not motivo:
                motivo_text.error_text = "Este campo es obligatorio."
                try:
                    motivo_text.update()
                except Exception as ex:
                    print(f"[DEBUG] Error actualizando campo motivo: {ex}")
                    pass  # Evitar errores de actualización
                return
            eliminar_cliente_confirmado(cliente, dialog, page, motivo)
        
        def on_cancelar_click(e):
            print("[DEBUG] Cancelando eliminación (versión ultra-minimalista)...")
            
            # Solo cerrar el diálogo, NO tocar overlay
            try:
                dialog.open = False
                print("[DEBUG] Diálogo de eliminación cerrado")
            except Exception as ex:
                print(f"[DEBUG] Error cerrando diálogo: {ex}")
            
            # Actualización mínima e inmediata
            try:
                page.update()
                print("[DEBUG] Actualización inmediata exitosa")
            except Exception as update_ex:
                print(f"[DEBUG] Actualización falló pero diálogo cerrado: {update_ex}")
            
            print("[DEBUG] Cancelación de eliminación completada sin delay")
        
        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=config["color_fondo"],
            shape=ft.RoundedRectangleBorder(radius=12),
            content=ft.Container(
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.WARNING, color="red"),
                        ft.Text("Confirmación de Eliminación", weight="bold", color=color_letras, size=18)
                    ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=8, color=color_tematica),
                    ft.Text(f"⚠️ ¿Estás seguro de que deseas eliminar a {cliente['nombre']} {cliente['apellido']}?", color=color_letras, size=15, text_align=ft.TextAlign.CENTER),
                    ft.Row([
                        ft.Container(motivo_text, alignment=ft.alignment.center)
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=config["color_fondo"],
                border=ft.border.all(3, color_tematica),
                border_radius=12,
                padding=10,
                alignment=ft.alignment.center,
                height=240
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=on_cancelar_click, style=ft.ButtonStyle(color=color_tematica)),
                ft.TextButton("Eliminar", on_click=on_eliminar_click, style=ft.ButtonStyle(color=ft.Colors.RED))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        try:
            page.overlay.append(dialog)
            dialog.open = True
            # Usar actualización simple
            page.update()
            print("[DEBUG] Diálogo de confirmación mostrado")
        except Exception as ex:
            print(f"[DEBUG] Error mostrando diálogo de confirmación: {ex}")
            # Fallback: mostrar alerta simple
            mostrar_alerta(page, "Error", "No se pudo mostrar el diálogo de confirmación", "red")

    return vista_estatica(cliente, page)

# 🔹 Función utilitaria para mostrar el panel de detalles directamente
def mostrar_panel_detalles_cliente(cliente, page, cerrar_panel_detalles, mostrar_detalles_cliente, pos_x=None, pos_y=None):
    # Recargar configuración en tiempo real
    config = cargar_configuracion()
    print(f"[DEBUG] Colores actualizados para panel - Fondo: {config['color_fondo']}, Temática: {config['color_tematica']}, Letras: {config['color_letras']}")
    
    panel = vista_detalles_cliente(
        cliente,
        config["color_letras"],
        config["color_tematica"],
        page,
        cerrar_panel_detalles,
        mostrar_detalles_cliente,
        pos_x,
        pos_y
    )
    try:
        page.overlay.append(panel)
        # Usar actualización simple
        page.update()
        print("[DEBUG] Panel de detalles mostrado exitosamente con colores actualizados")
    except Exception as ex:
        print(f"[DEBUG] Error mostrando panel de detalles: {ex}")