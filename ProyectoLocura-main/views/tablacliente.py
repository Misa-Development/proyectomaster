import flet as ft
import sqlite3
import sys
import os
import functools

# Agregar el directorio database al path
sys.path.append(os.path.join(os.path.dirname(__file__), '../database'))
from database.db import conectar_db
from database.db import obtener_clientes
from datetime import datetime, date

def vista_tabla_clientes(page, mostrar_detalles_cliente, color_letras="#000000", color_tematica="#E8E8E8", scale=1.0, clientes_filtrados=None, tabla_listview=None, rol=None, devolver_funcion_limpiar=False):
    # --- PAGINACIÓN ---
    PAGE_SIZE = 50
    # Estado de paginación (guardar en page.data para persistencia entre actualizaciones)
    if not hasattr(page, 'data') or not isinstance(page.data, dict):
        page.data = {}
    # Guardar los clientes filtrados en page.data solo si se pasan explícitamente (aplicar filtro)
    if clientes_filtrados is not None:
        page.data['clientes_filtrados'] = clientes_filtrados
        # Solo reiniciar paginación si se está aplicando un filtro nuevo (flag debe ser seteado desde la función de filtros)
        if page.data.get('aplicando_filtro', False):
            page.data['clientes_page'] = 0
            # El flag se limpia aquí, pero nunca se setea en la paginación
            page.data['aplicando_filtro'] = False
    # Usar los clientes filtrados guardados si existen
    if 'clientes_filtrados' in page.data and page.data['clientes_filtrados'] is not None:
        clientes_filtrados = page.data['clientes_filtrados']
    if 'clientes_page' not in page.data:
        page.data['clientes_page'] = 0
    current_page = page.data['clientes_page']
    """
    Genera la tabla de clientes consultando desde la base de datos o usando una lista filtrada.
    El parámetro scale permite que la tabla reaccione al zoom global.
    """
    # Determinar si el tema es oscuro para hover
    is_dark = False
    try:
        from views.Menu import cargar_configuracion
        config = cargar_configuracion()
        color_fondo = config.get("color_fondo", "#FFFFFF")
        if color_fondo.startswith("#"):
            r = int(color_fondo[1:3], 16)
            g = int(color_fondo[3:5], 16)
            b = int(color_fondo[5:7], 16)
            luminancia = (r*0.299 + g*0.587 + b*0.114)
            is_dark = luminancia < 128
    except Exception:
        color_fondo = "#FFFFFF"
        pass
    hover_bg = "#F5F5F5" if is_dark else "#222222"
    hover_fg = color_letras if not is_dark else color_tematica
    normal_bg = color_fondo

    # Elimino hover y referencias a filas activas
    filas_containers = []  # Lista para guardar referencias a todas las filas

    # Elimina la función poner_todas_filas_fondo_menos para evitar recorrer todas las filas en cada hover

    def make_on_click(cliente_dict):
        def on_click(e, c=cliente_dict):
            pos_x = page.window.width - 500 if hasattr(page.window, 'width') else 900
            pos_y = getattr(e, 'page_y', None)
            try:
                from views.verdetalle import vista_detalles_cliente
                overlays_to_remove = [ctrl for ctrl in page.overlay if not getattr(ctrl, 'is_menu_panel', False)]
                for ctrl in overlays_to_remove:
                    page.overlay.remove(ctrl)
                def cerrar_panel_detalle():
                    page.overlay[:] = [ctrl for ctrl in page.overlay if getattr(ctrl, 'is_menu_panel', False)]
                    page.update()
                detalle = vista_detalles_cliente(
                    c, color_letras, color_tematica, page,
                    cerrar_panel_detalle,
                    mostrar_detalles_cliente,
                    pos_x=pos_x, pos_y=pos_y
                )
                detalle.width = 500
                detalle.border = ft.border.all(3, color_tematica)
                page.overlay.append(detalle)
                page.update()
            except Exception as ex:
                print(f"[DEBUG] Error mostrando detalle cliente: {ex}")
        return on_click

    def normalizar_fecha(fecha):
        try:
            if '-' in fecha:
                dt = datetime.strptime(fecha, "%Y-%m-%d")
                return dt.strftime("%d/%m/%Y")
            elif len(fecha.split('/')) == 3:
                partes = fecha.split('/')
                anio = partes[2]
                if len(anio) == 2:
                    anio = '20' + anio
                dt = datetime.strptime(f"{partes[0]}/{partes[1]}/{anio}", "%d/%m/%Y")
                return dt.strftime("%d/%m/%Y")
        except Exception:
            return fecha
        return fecha
    def get_rows():
        rows = []
        filas_containers.clear()  # Limpiar referencias viejas antes de crear nuevas filas
        # Permitir filtrado externo
        if clientes_filtrados is not None:
            clientes = clientes_filtrados
        else:
            try:
                conn = conectar_db()
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT dni, nombre, apellido, sexo, fecha_nacimiento, fecha_inicio, fecha_vencimiento, apta_medica, estado
                    FROM clientes
                    ORDER BY fecha_inicio DESC, rowid DESC
                ''')
                clientes = [dict(row) for row in cursor.fetchall()]
            except sqlite3.Error as e:
                print(f"Error al obtener clientes: {e}")
                return [ft.Container(content=ft.Text("Error al cargar datos", color=ft.colors.RED, size=18))]
            finally:
                if 'conn' in locals() and conn:
                    conn.close()
        from datetime import datetime, date
        # ...resto de get_rows sin cambios...
        # Paginación personalizada: en cada página se omiten los primeros PAGE_SIZE * page.data['clientes_page'] clientes
        start_idx = page.data.get('clientes_page', 0) * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        clientes_pagina = clientes[start_idx:end_idx]
        for cliente in clientes_pagina:
            estado_val = cliente.get("estado")
            if estado_val == 1 or estado_val == "1":
                estado_str = "Activo"
            elif estado_val == 0 or estado_val == "0":
                estado_str = "Inactivo"
            else:
                estado_str = cliente.get("estado", "")
            dni_txt = ft.Text(str(cliente.get("dni", "")), color=color_letras, size=14, expand=True, font_family="Segoe UI")
            nombre_txt = ft.Text(cliente["nombre"], color=color_letras, size=14, expand=True, font_family="Segoe UI")
            apellido_txt = ft.Text(cliente["apellido"], color=color_letras, size=14, expand=True, font_family="Segoe UI")
            sexo_txt = ft.Text(cliente["sexo"], color=color_letras, size=14, expand=True, font_family="Segoe UI")
            fecha_nacimiento_str = cliente.get("fecha_nacimiento", "")
            edad = ""
            fecha_nac_fmt = fecha_nacimiento_str
            if fecha_nacimiento_str:
                try:
                    if '-' in fecha_nacimiento_str:
                        fecha_nac = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
                        fecha_nac_fmt = fecha_nacimiento_str
                    elif len(fecha_nacimiento_str.split('/')) == 3:
                        partes = fecha_nacimiento_str.split('/')
                        anio = partes[2]
                        if len(anio) == 2:
                            anio = '20' + anio
                        fecha_nac = datetime.strptime(f"{partes[0]}/{partes[1]}/{anio}", "%d/%m/%Y").date()
                        fecha_nac_fmt = f"{partes[0]}/{partes[1]}/{anio}"
                    else:
                        raise ValueError("Formato de fecha desconocido")
                    today = date.today()
                    edad = today.year - fecha_nac.year - ((today.month, today.day) < (fecha_nac.month, fecha_nac.day))
                except Exception:
                    edad = "-"
            edad_txt = ft.Text(str(edad), color=color_letras, size=14, expand=True, font_family="Segoe UI")
            fecha_nac_txt = ft.Text(fecha_nac_fmt, color=color_letras, size=14, expand=True, font_family="Segoe UI")
            inicio_txt = ft.Text(normalizar_fecha(cliente["fecha_inicio"]), color=color_letras, size=14, expand=True, font_family="Segoe UI")
            venc_txt = ft.Text(normalizar_fecha(cliente["fecha_vencimiento"]), color=color_letras, size=14, expand=True, font_family="Segoe UI")
            apta_txt = ft.Text("Sí" if cliente["apta_medica"] else "No", color=color_letras, size=14, expand=True, font_family="Segoe UI")
            # Mostrar valor real de 'actividad' si existe, si no dejar vacío
            actividad_val = cliente.get("actividad", "")
            # Si el valor de actividad es una fecha o está vacío, mostrar estado en vez de la fecha
            import re
            fecha_regex = r"^\d{4}-\d{2}-\d{2}$|^\d{2}/\d{2}/\d{4}$"
            if not actividad_val or re.match(fecha_regex, str(actividad_val)) or actividad_val.lower() in ["", "none", "null"]:
                estado_val = cliente.get("estado")
                if estado_val == 1 or estado_val == "1":
                    actividad_val = "Activo"
                elif estado_val == 0 or estado_val == "0":
                    actividad_val = "Inactivo"
                else:
                    actividad_val = str(estado_val)
            actividad_txt = ft.Text(str(actividad_val), color=color_letras, size=14, expand=True, font_family="Segoe UI")
            def fila_on_click(e, c=cliente):
                make_on_click(dict(c))(e)
            row_container = ft.Container(
                content=make_row_container(
                    dni_txt,
                    nombre_txt,
                    apellido_txt,
                    sexo_txt,
                    edad_txt,
                    inicio_txt,
                    venc_txt,
                    actividad_txt  # Actividad como última columna
                ),
                bgcolor=normal_bg,
                border_radius=3,
                padding=ft.padding.symmetric(vertical=1, horizontal=3),
                height=28,
                on_click=fila_on_click,
            )
            filas_containers.append(row_container)
            rows.append(row_container)
        return rows, clientes

    # Elimino funciones de hover y limpieza relacionadas

    headers = ft.Container(
        content=ft.Row([
            ft.Container(ft.Text("Inicio", weight="bold", color=color_letras, size=16, font_family="Segoe UI"), border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),
            ft.Container(ft.Text("Vencimiento", weight="bold", color=color_letras, size=16, font_family="Segoe UI"), border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),
            ft.Container(ft.Text("DNI", weight="bold", color=color_letras, size=16, font_family="Segoe UI"), border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),
            ft.Container(ft.Text("Nombre", weight="bold", color=color_letras, size=16, font_family="Segoe UI"), border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),
            ft.Container(ft.Text("Apellido", weight="bold", color=color_letras, size=16, font_family="Segoe UI"), border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),
            ft.Container(ft.Text("Sexo", weight="bold", color=color_letras, size=16, font_family="Segoe UI"), border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),
            ft.Container(ft.Text("Edad", weight="bold", color=color_letras, size=16, font_family="Segoe UI"), border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),
            ft.Container(ft.Text("Actividad", weight="bold", color=color_letras, size=16, font_family="Segoe UI"), expand=True, alignment=ft.alignment.center),  # Sin borde derecho
        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=normal_bg,
        padding=3,
        border_radius=3,
        border=ft.border.all(1, color_tematica),
        margin=ft.margin.only(bottom=2),
    )
    def make_row_container(*controls):
        return ft.Row([
            ft.Container(controls[5], border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),  # Inicio
            ft.Container(controls[6], border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),  # Vencimiento           
            ft.Container(controls[0], border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),  # DNI
            ft.Container(controls[1], border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),  # Nombre
            ft.Container(controls[2], border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),  # Apellido
            ft.Container(controls[3], border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),  # Sexo
            ft.Container(controls[4], border=ft.border.only(right=ft.BorderSide(1, color_tematica)), expand=True, alignment=ft.alignment.center),  # Edad
            ft.Container(controls[7], expand=True, alignment=ft.alignment.center),  # Actividad sin borde derecho
        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    rows, clientes = get_rows()
    if tabla_listview is not None:
        # Si es un Container, obtener el ListView real
        if isinstance(tabla_listview, ft.Container) and hasattr(tabla_listview, 'listview'):
            listview = tabla_listview.listview
        else:
            listview = tabla_listview
        listview.controls.clear()
        listview.controls.extend(rows)  # Solo las filas, sin headers
        # Verificar que el listview es válido antes de actualizar
        is_valid = (
            listview is not None and
            hasattr(listview, '__page') and listview.__page is not None and
            hasattr(listview, '_Control__uid') and listview._Control__uid is not None and
            (listview in getattr(page, 'controls', []) or any(hasattr(c, 'listview') and c.listview is listview for c in getattr(page, 'controls', [])))
        )
        if is_valid:
            listview.update()
        return {
            'header': headers,
            'tabla': tabla_listview
        }
    else:
        # Definir función de paginación antes de los controles
        def cambiar_pagina(delta):
            # Usar los clientes filtrados guardados si existen
            clientes_filtrados_local = page.data.get('clientes_filtrados', None)
            # Usar la lista filtrada para mostrar las filas y calcular el total
            if clientes_filtrados_local is not None:
                total_clientes = len(clientes_filtrados_local)
                # Mostrar solo los clientes filtrados en la página actual
                def get_rows_filtrados():
                    rows = []
                    start_idx = page.data.get('clientes_page', 0) * PAGE_SIZE
                    end_idx = start_idx + PAGE_SIZE
                    clientes_pagina = clientes_filtrados_local[start_idx:end_idx]
                    for cliente in clientes_pagina:
                        # ...igual que en get_rows original...
                        estado_val = cliente.get("estado")
                        if estado_val == 1 or estado_val == "1":
                            estado_str = "Activo"
                        elif estado_val == 0 or estado_val == "0":
                            estado_str = "Inactivo"
                        else:
                            estado_str = cliente.get("estado", "")
                        dni_txt = ft.Text(str(cliente.get("dni", "")), color=color_letras, size=14, expand=True, font_family="Segoe UI")
                        nombre_txt = ft.Text(cliente["nombre"], color=color_letras, size=14, expand=True, font_family="Segoe UI")
                        apellido_txt = ft.Text(cliente["apellido"], color=color_letras, size=14, expand=True, font_family="Segoe UI")
                        sexo_txt = ft.Text(cliente["sexo"], color=color_letras, size=14, expand=True, font_family="Segoe UI")
                        fecha_nacimiento_str = cliente.get("fecha_nacimiento", "")
                        edad = ""
                        fecha_nac_fmt = fecha_nacimiento_str
                        if fecha_nacimiento_str:
                            try:
                                if '-' in fecha_nacimiento_str:
                                    from datetime import datetime, date
                                    fecha_nac = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
                                    fecha_nac_fmt = fecha_nacimiento_str
                                elif len(fecha_nacimiento_str.split('/')) == 3:
                                    partes = fecha_nacimiento_str.split('/')
                                    anio = partes[2]
                                    if len(anio) == 2:
                                        anio = '20' + anio
                                    from datetime import datetime, date
                                    fecha_nac = datetime.strptime(f"{partes[0]}/{partes[1]}/{anio}", "%d/%m/%Y").date()
                                    fecha_nac_fmt = f"{partes[0]}/{partes[1]}/{anio}"
                                else:
                                    raise ValueError("Formato de fecha desconocido")
                                today = date.today()
                                edad = today.year - fecha_nac.year - ((today.month, today.day) < (fecha_nac.month, fecha_nac.day))
                            except Exception:
                                edad = "-"
                        edad_txt = ft.Text(str(edad), color=color_letras, size=14, expand=True, font_family="Segoe UI")
                        fecha_nac_txt = ft.Text(fecha_nac_fmt, color=color_letras, size=14, expand=True, font_family="Segoe UI")
                        inicio_txt = ft.Text(cliente.get("fecha_inicio", ""), color=color_letras, size=14, expand=True, font_family="Segoe UI")
                        venc_txt = ft.Text(cliente.get("fecha_vencimiento", ""), color=color_letras, size=14, expand=True, font_family="Segoe UI")
                        apta_txt = ft.Text("Sí" if cliente.get("apta_medica", False) else "No", color=color_letras, size=14, expand=True, font_family="Segoe UI")
                        actividad_val = cliente.get("actividad", "")
                        import re
                        fecha_regex = r"^\d{4}-\d{2}-\d{2}$|^\d{2}/\d{2}/\d{4}$"
                        if not actividad_val or re.match(fecha_regex, str(actividad_val)) or str(actividad_val).lower() in ["", "none", "null"]:
                            estado_val = cliente.get("estado")
                            if estado_val == 1 or estado_val == "1":
                                actividad_val = "Activo"
                            elif estado_val == 0 or estado_val == "0":
                                actividad_val = "Inactivo"
                            else:
                                actividad_val = str(estado_val)
                        actividad_txt = ft.Text(str(actividad_val), color=color_letras, size=14, expand=True, font_family="Segoe UI")
                        def fila_on_click(e, c=cliente):
                            make_on_click(dict(c))(e)
                        row_container = ft.Container(
                            content=make_row_container(
                                dni_txt,
                                nombre_txt,
                                apellido_txt,
                                sexo_txt,
                                edad_txt,
                                inicio_txt,
                                venc_txt,
                                actividad_txt
                            ),
                            bgcolor=normal_bg,
                            border_radius=3,
                            padding=ft.padding.symmetric(vertical=1, horizontal=3),
                            height=28,
                            on_click=fila_on_click,
                        )
                        rows.append(row_container)
                    return rows
                total_pages = max(1, (total_clientes + PAGE_SIZE - 1) // PAGE_SIZE)
                current_page_actual = page.data.get('clientes_page', 0)
                page.data['clientes_page'] = max(0, min(current_page_actual + delta, total_pages - 1))
                print(f"[DEBUG] Cambiando a página: {page.data['clientes_page']+1} de {total_pages}")
                rows = get_rows_filtrados()
                tabla_con_scroll.controls.clear()
                tabla_con_scroll.controls.extend(rows)
                paginacion_row.controls[0].value = f"Página {page.data['clientes_page']+1} de {total_pages}"
                paginacion_row.controls[1].disabled = page.data['clientes_page'] == 0
                paginacion_row.controls[2].disabled = page.data['clientes_page'] >= total_pages - 1
                tabla_con_scroll.update()
                paginacion_row.update()
                return
            # Si no hay filtro, usar la lógica original
            try:
                conn = conectar_db()
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM clientes')
                total_clientes = cursor.fetchone()[0]
            except Exception:
                total_clientes = 0
            finally:
                if 'conn' in locals() and conn:
                    conn.close()
            total_pages = max(1, (total_clientes + PAGE_SIZE - 1) // PAGE_SIZE)
            current_page_actual = page.data.get('clientes_page', 0)
            page.data['clientes_page'] = max(0, min(current_page_actual + delta, total_pages - 1))
            print(f"[DEBUG] Cambiando a página: {page.data['clientes_page']+1} de {total_pages}")
            rows, _ = get_rows()
            tabla_con_scroll.controls.clear()
            tabla_con_scroll.controls.extend(rows)
            paginacion_row.controls[0].value = f"Página {page.data['clientes_page']+1} de {total_pages}"
            paginacion_row.controls[1].disabled = page.data['clientes_page'] == 0
            paginacion_row.controls[2].disabled = page.data['clientes_page'] >= total_pages - 1
            tabla_con_scroll.update()
            paginacion_row.update()

        tabla_con_scroll = ft.ListView(
            controls=rows,  # Solo las filas, sin headers
            auto_scroll=False,
            spacing=1
        )
        # --- Controles de paginación ---
        total_clientes = len(clientes)
        total_pages = max(1, (total_clientes + PAGE_SIZE - 1) // PAGE_SIZE)
        paginacion_row = ft.Row([
            ft.Text(f"Página {current_page + 1} de {total_pages}", size=14, color=color_tematica),
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Anterior",
                disabled=current_page == 0,
                icon_color=color_tematica,
                on_click=lambda e: cambiar_pagina(-1)
            ),
            ft.IconButton(
                icon=ft.Icons.ARROW_FORWARD,
                tooltip="Siguiente",
                disabled=current_page >= total_pages - 1,
                icon_color=color_tematica,
                on_click=lambda e: cambiar_pagina(1)
            )
        ], alignment=ft.MainAxisAlignment.CENTER)

        tabla_container = ft.Container(
            content=ft.Column([
                headers,  # Header fijo arriba
                tabla_con_scroll,  # ListView sin expand
                paginacion_row
            ])
        )
        tabla_wrapper = ft.Container(
            content=tabla_container
        )
        tabla_wrapper.listview = tabla_con_scroll
        return {
            'header': headers,
            'tabla': tabla_wrapper
        }

def actualizar_lista_clientes(page, mostrar_detalles_cliente):
    """Función para actualizar la lista de clientes en la vista principal."""
    # print("🔄 Actualizando lista de clientes...")
    page.clean()
    from views.dashboard import vista_dashboard  # Import here to avoid circular dependency
    vista_dashboard(page)  # Call vista_dashboard to redraw the entire dashboard
    page.update()