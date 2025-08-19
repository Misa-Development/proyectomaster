import flet as ft
import json
import sqlite3
import datetime
from views.Menu import vista_menu
from views.tablacliente import vista_tabla_clientes
from views.verdetalle import vista_detalles_cliente
from views.filtros import vista_filtros
from database.db import conectar_db
from views.leyendas import vista_leyendas

from views.Menu import cargar_configuracion

def actualizar_estados_clientes():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT id, fecha_vencimiento FROM clientes")
        clientes = cursor.fetchall()
        for cliente_id, fecha_vencimiento in clientes:
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    fecha_vencimiento_obj = datetime.datetime.strptime(fecha_vencimiento, fmt)
                    fecha_vencimiento_formateada = fecha_vencimiento_obj.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            else:
                continue  # Si ningún formato funcionó, salta este cliente
            if fecha_vencimiento_formateada > fecha_actual:
                estado = 1
            elif fecha_vencimiento_formateada < fecha_actual:
                estado = 0
            else:
                cursor.execute("SELECT estado FROM clientes WHERE id = ?", (cliente_id,))
                estado = cursor.fetchone()[0]
            cursor.execute("UPDATE clientes SET estado = ? WHERE id = ?", (estado, cliente_id))
        conn.commit()
    except Exception:
        pass
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def obtener_clientes():
    try:
        conn = conectar_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            'SELECT nombre, apellido, sexo, edad, apta_medica, enfermedades, fecha_inicio, fecha_vencimiento FROM clientes'
        )
        clientes = [dict(row) for row in cursor.fetchall()]
    except Exception:
        clientes = []
    finally:
        if 'conn' in locals() and conn:
            conn.close()
    return clientes

def vista_dashboard(page):
    try:
        page.global_scale = getattr(page, "global_scale", 1.0)
        page.title = "Dashboard"
        page.scroll = "none"
        # Limpiar controles previos para evitar controles huérfanos
        if hasattr(page, "controls"):
            page.controls.clear()

        config = cargar_configuracion()
        color_fondo = config.get("color_fondo", "#FFFFFF")
        color_letras = config.get("color_letras", "#000000")
        color_tematica = config.get("color_tematica", "#FF5733")
        nombre_gimnasio = config.get("nombre_gimnasio", "Mi Gimnasio")

        actualizar_estados_clientes()
        clientes = obtener_clientes()
        # Tomar SIEMPRE el valor actualizado de page.global_scale
        scale = page.global_scale
        page.bgcolor = color_fondo
        page.window_maximized = True

        menu = vista_menu(page, color_letras=color_letras, color_fondo=color_fondo, color_tematica=color_tematica)
        header = ft.Container(
            content=ft.Row(
                controls=[
                    menu,
                    ft.Text(nombre_gimnasio, size=23, weight="bold", color="black")
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=0,
            bgcolor=color_tematica,
            border_radius=10,
        )

        # --- MODAL GLOBAL ---
        if not hasattr(page, "cliente_panel_content"):
            page.cliente_panel_content = None
        if not hasattr(page, "is_panel_abierto"):
            page.is_panel_abierto = False
        if not hasattr(page, "cliente_panel_modal"):
            page.cliente_panel_modal = ft.Container(
                content=None,
                bgcolor=ft.Colors.with_opacity(0.98, color=color_fondo),
                padding=20*scale,
                border_radius=15*scale,
                alignment=ft.alignment.center_right,  # Panel alineado a la derecha
                border=ft.border.all(2*scale, color=color_tematica),
                width=0,
                visible=False,
                animate_size=True,
                animate=ft.Animation(duration=int(300*scale), curve=ft.AnimationCurve.EASE_IN_OUT),
                scale=scale,
                expand=False,  # No expand, para que sea tipo panel
            )

        overlay = ft.Container(
            visible=page.is_panel_abierto,
            bgcolor=ft.Colors.with_opacity(0.5, "#000000"),
            width=float("inf"),
            height=float("inf"),
            alignment=ft.alignment.center,
            on_click=lambda e: None,
        )

        def mostrar_detalles_cliente(cliente):
            page.is_panel_abierto = True
            page.cliente_panel_content = vista_detalles_cliente(
                cliente, color_letras, color_tematica, page, cerrar_panel_detalles, mostrar_detalles_cliente
            )
            page.cliente_panel_modal.content = page.cliente_panel_content
            page.cliente_panel_modal.visible = True
            page.cliente_panel_modal.width = 400*scale  # Más ancho para panel lateral
            page.cliente_panel_modal.update()
            page.update()

        def cerrar_panel_detalles():
            page.is_panel_abierto = False
            page.cliente_panel_content = None
            page.cliente_panel_modal.content = None
            page.cliente_panel_modal.visible = False
            page.cliente_panel_modal.width = 0
            page.cliente_panel_modal.update()
            page.update()

        rol = getattr(page, "rol", None)
        tabla_clientes_dict = vista_tabla_clientes(
            page,
            mostrar_detalles_cliente,
            color_letras,
            color_tematica,
            scale=scale,
            rol=rol,
            devolver_funcion_limpiar=True
        )
        tabla_clientes = tabla_clientes_dict['tabla']

        filtros = vista_filtros(
            page, color_letras, color_fondo, color_tematica, tabla_clientes, clientes, mostrar_detalles_cliente, scale=scale
        )
        leyendas = vista_leyendas(color_letras, color_fondo, color_tematica, page, scale=1.0)

        contenido_escalado = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(leyendas, margin=ft.margin.only(top=20)),
                    ft.Container(filtros, scale=scale),
                    ft.Container(tabla_clientes, scale=scale)
                ],
                spacing=int(20*scale),
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                expand=True,
                scroll="auto"
            ),
            expand=True,
            height=None,
            bgcolor=None,
            padding=0
        )

        contenido_principal = ft.Column(
            controls=[
                header,
                contenido_escalado
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=True
        )
        page.scroll = "auto"

        # Ajustar el ancho del main_container si el panel está abierto
        ancho_panel = 400*scale if page.is_panel_abierto else 0
        main_container = ft.Container(
            content=ft.Row([
                ft.Container(content=contenido_principal, width=1300-ancho_panel, expand=True)
            ], alignment=ft.MainAxisAlignment.START),
            alignment=ft.alignment.top_left,  # Cambiado a top_left para dejar espacio a la derecha
            width=1350-ancho_panel,  # Fijar el ancho del main_container
            expand=True
        )
        # Layout con Stack expandido para panel derecho
        dashboard_area = ft.Container(
            content=ft.Stack([
                main_container,
                overlay,
                ft.Row([
                    ft.Container(width=1, expand=True),  # Espaciador
                    page.cliente_panel_modal
                ], alignment=ft.MainAxisAlignment.END, expand=True)
            ], expand=True),
            expand=True
        )
        return dashboard_area
    except Exception as ex:
        print(f"❌ Error en vista_dashboard: {ex}")
        return None