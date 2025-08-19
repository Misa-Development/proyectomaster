import flet as ft
import sqlite3
from database.db import conectar_db
import datetime
from views.tablacliente import vista_tabla_clientes

# --------------------------------------
# Funciones reutilizables
# --------------------------------------

def obtener_datatable(tabla_con_scroll, default_columns):
    """Adapta la obtención de la tabla visual personalizada o crea un DataTable si no es compatible."""
    # Si es un DataTable clásico, lo retorna
    if isinstance(tabla_con_scroll, ft.DataTable):
        return tabla_con_scroll
    # Si es un Container con ListView (tabla personalizada), retorna el widget tal cual
    if isinstance(tabla_con_scroll, ft.Container):
        content = getattr(tabla_con_scroll, "content", None)
        if isinstance(content, ft.ListView):
            return tabla_con_scroll  # Devuelve el widget de la tabla personalizada
    # Si es un ListView directo (raro, pero por compatibilidad)
    if isinstance(tabla_con_scroll, ft.ListView):
        return tabla_con_scroll
    # Si nada coincide, retorna un DataTable vacío
    return ft.DataTable(columns=default_columns)

def crear_campo_busqueda(label, color_letras, color_tematica):
    """Crea un campo de búsqueda con estilo uniforme."""
    return ft.TextField(
        label=label, prefix_icon=ft.Icons.SEARCH, width=300,
        text_style=ft.TextStyle(color=color_letras), border_color=color_tematica,
        hint_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=color_letras),
    )

def crear_filtro_dropdown(label, options, color_letras, color_tematica):
    """Crea un dropdown para filtros."""
    return ft.Dropdown(
        label=label, options=[ft.dropdown.Option(opt) for opt in options], value="Todos",
        text_style=ft.TextStyle(color=color_letras), border_color=color_tematica,
        hint_style=ft.TextStyle(color=color_letras), label_style=ft.TextStyle(color=color_letras),
    )

def crear_fila_cliente(cliente, color_letras, mostrar_detalles_cliente):
    """Crea una fila en DataTable para un cliente."""
    return ft.DataRow(cells=[
        ft.DataCell(ft.Text(cliente["nombre"], color=color_letras)),
        ft.DataCell(ft.Text(cliente["apellido"], color=color_letras)),
        ft.DataCell(ft.Text(cliente["sexo"], color=color_letras)),
        ft.DataCell(ft.Text(str(cliente["edad"]), color=color_letras)),
        ft.DataCell(ft.Text(cliente["fecha_inicio"], color=color_letras)),
        ft.DataCell(ft.Text(cliente["fecha_vencimiento"], color=color_letras)),
        ft.DataCell(ft.Text("Sí" if cliente["apta_medica"] else "No", color=color_letras)),
        ft.DataCell(ft.Text("Activo" if cliente["estado"] == 1 else "Inactivo", color=color_letras)),
        ft.DataCell(ft.IconButton(icon=ft.Icons.VISIBILITY, tooltip="Ver Detalles", icon_color=color_letras,
                                  on_click=lambda e, c=cliente: mostrar_detalles_cliente(c))),
    ])

def crear_fila_sin_resultados(default_columns):
    """Crea una fila indicando que no hay resultados en la tabla."""
    return ft.DataRow(cells=[ft.DataCell(ft.Text("Sin resultados", color="red"))] +
                             [ft.DataCell(ft.Text("")) for _ in range(len(default_columns) - 1)])

# --------------------------------------
# Vista de filtros
# --------------------------------------

def vista_filtros(page, color_letras, color_fondo, color_tematica, tabla_con_scroll, clientes, mostrar_detalles_cliente, scale=1.0, set_limpiar_hover_total=None):
    """Construye la vista de filtros y el DataTable dinámico."""

    default_columns = ["Nombre", "Apellido", "Sexo", "Edad", "Fecha de Inicio", "Fecha de Vencimiento",
                       "Apta Médica", "Activo/Inactivo", "Acción"]
    tabla_clientes = obtener_datatable(tabla_con_scroll, [ft.DataColumn(ft.Text(col, weight="bold", color=color_letras, size=int(15*scale))) for col in default_columns])

    # Definir filtros y campos de búsqueda
    filtros = {
        "nombre": ft.TextField(
            label="Buscar por nombre", prefix_icon=ft.Icons.SEARCH, width=int(300*scale),
            text_style=ft.TextStyle(color=color_letras, size=int(14*scale)), border_color=color_tematica,
            hint_style=ft.TextStyle(color=color_letras, size=int(14*scale)), label_style=ft.TextStyle(color=color_letras, size=int(14*scale)),
        ),
        "apellido": ft.TextField(
            label="Buscar por apellido", prefix_icon=ft.Icons.SEARCH, width=int(300*scale),
            text_style=ft.TextStyle(color=color_letras, size=int(14*scale)), border_color=color_tematica,
            hint_style=ft.TextStyle(color=color_letras, size=int(14*scale)), label_style=ft.TextStyle(color=color_letras, size=int(14*scale)),
        ),
        "dni": ft.TextField(
            label="Buscar por DNI", prefix_icon=ft.Icons.SEARCH, width=int(300*scale),
            text_style=ft.TextStyle(color=color_letras, size=int(14*scale)), border_color=color_tematica,
            hint_style=ft.TextStyle(color=color_letras, size=int(14*scale)), label_style=ft.TextStyle(color=color_letras, size=int(14*scale)),
        ),
        "genero": ft.Dropdown(
            label="Filtrar por género", options=[ft.dropdown.Option(opt) for opt in ["Todos", "Masculino", "Femenino"]], value="Todos",
            text_style=ft.TextStyle(color=color_letras, size=int(14*scale)), border_color=color_tematica,
            hint_style=ft.TextStyle(color=color_letras, size=int(14*scale)), label_style=ft.TextStyle(color=color_letras, size=int(14*scale)),
        ),
        "apta_medica": ft.Dropdown(
            label="Filtrar por apta médica", options=[ft.dropdown.Option(opt) for opt in ["Todos", "Sí", "No"]], value="Todos",
            text_style=ft.TextStyle(color=color_letras, size=int(14*scale)), border_color=color_tematica,
            hint_style=ft.TextStyle(color=color_letras, size=int(14*scale)), label_style=ft.TextStyle(color=color_letras, size=int(14*scale)),
        ),
        "estado": ft.Dropdown(
            label="Filtrar por estado", options=[ft.dropdown.Option(opt) for opt in ["Todos", "Activo", "Inactivo"]], value="Todos",
            text_style=ft.TextStyle(color=color_letras, size=int(14*scale)), border_color=color_tematica,
            hint_style=ft.TextStyle(color=color_letras, size=int(14*scale)), label_style=ft.TextStyle(color=color_letras, size=int(14*scale)),
        ),
    }

    def actualizar_color_switch(switch):
        switch.active_color = color_tematica if switch.value else color_letras
        switch.update()

    switch_proximas_renovaciones = ft.Switch(
        label="Próximas Renovaciones",
        value=False,
        active_color=color_tematica,
        inactive_track_color=color_tematica,
        inactive_thumb_color=color_fondo,
        label_style=ft.TextStyle(color=color_letras, size=int(14*scale)),
        on_change=lambda e: actualizar_color_switch(e.control)
    )

    switch_vencidos_recientes = ft.Switch(
        label="Vencidos Recientes", value=False, active_color=color_tematica,
        inactive_track_color=color_tematica,
        inactive_thumb_color=color_fondo,
        label_style=ft.TextStyle(color=color_letras, size=int(14*scale))
    )

    # Función para aplicar filtros
    def buscar_cliente():
        params = {k: v.value.lower() if isinstance(v, ft.TextField) else v.value for k, v in filtros.items()}
        proximas_renovaciones = switch_proximas_renovaciones.value
        vencidos_recientes = switch_vencidos_recientes.value
        hoy = datetime.date.today()
        clientes_filtrados = []
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            query_sql = "SELECT * FROM clientes WHERE 1=1"
            sql_params = []

            estado_filtrado = params.get("estado", "Todos")

            # Si el filtro de vencidos_recientes está activo, mostrar solo inactivos recientes
            if vencidos_recientes:
                query_sql += " AND estado = 0"

            for campo, valor in params.items():
                if valor and valor != "Todos":
                    if campo == "nombre":
                        query_sql += f" AND LOWER(nombre) LIKE ?"
                        sql_params.append(f"{valor}%")
                    elif campo == "apellido":
                        query_sql += f" AND LOWER(apellido) LIKE ?"
                        sql_params.append(f"{valor}%")
                    elif campo == "dni":
                        query_sql += f" AND LOWER(dni) LIKE ?"
                        sql_params.append(f"%{valor}%")
                    elif campo == "genero":
                        query_sql += " AND LOWER(sexo) = ?"
                        sql_params.append("male" if valor == "Masculino" else "female")
                    elif campo == "apta_medica":
                        query_sql += " AND apta_medica = ?"
                        sql_params.append(valor == "Sí")
                    elif campo == "estado":
                        query_sql += " AND estado = ?"
                        sql_params.append(1 if valor == "Activo" else 0)

            def fecha_sql_expr(campo):
                return (
                    f"CASE "
                    f"WHEN instr({campo}, '-') > 0 THEN {campo} "
                    f"WHEN length({campo})=8 THEN '20' || substr({campo}, 7, 2) || '-' || substr({campo}, 4, 2) || '-' || substr({campo}, 1, 2) "
                    f"WHEN length({campo})=10 THEN substr({campo}, 7, 4) || '-' || substr({campo}, 4, 2) || '-' || substr({campo}, 1, 2) "
                    f"ELSE {campo} END"
                )

            if proximas_renovaciones:
                hoy_str = hoy.strftime('%Y-%m-%d')
                en_15 = (hoy + datetime.timedelta(days=15)).strftime('%Y-%m-%d')
                query_sql += f"""
                    AND estado = 1
                    AND strftime('%s', {fecha_sql_expr('fecha_vencimiento')})
                        BETWEEN strftime('%s', ?) AND strftime('%s', ?)
                """
                sql_params.append(hoy_str)
                sql_params.append(en_15)
            if vencidos_recientes:
                hace_15 = (hoy - datetime.timedelta(days=15)).strftime('%Y-%m-%d')
                ayer = (hoy - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                query_sql += f"""
                    AND strftime('%s', {fecha_sql_expr('fecha_vencimiento')})
                        BETWEEN strftime('%s', ?) AND strftime('%s', ?)
                """
                sql_params.append(hace_15)
                sql_params.append(ayer)
            
            # Siempre ordenar por fecha de inicio (más recientes primero)
            query_sql += " ORDER BY fecha_inicio DESC, rowid DESC"
            
            cursor.execute(query_sql, sql_params)
            clientes_filtrados = [dict(cliente) for cliente in cursor.fetchall()]

            resultado = vista_tabla_clientes(page, mostrar_detalles_cliente, color_letras, color_tematica, scale=scale, clientes_filtrados=clientes_filtrados, tabla_listview=tabla_listview, devolver_funcion_limpiar=True)
            if set_limpiar_hover_total and resultado and 'limpiar_hover_total' in resultado:
                set_limpiar_hover_total(resultado['limpiar_hover_total'])

            is_valid = (
                tabla_listview is not None and
                hasattr(tabla_listview, '__page') and tabla_listview.__page is not None and
                hasattr(tabla_listview, '_Control__uid') and tabla_listview._Control__uid is not None and
                any(tabla_listview is c or (hasattr(c, 'listview') and c.listview is tabla_listview) for c in page.controls)
            )
            if is_valid:
                tabla_listview.controls.clear()
                for cliente in clientes_filtrados:
                    fila = crear_fila_cliente(cliente, color_letras, mostrar_detalles_cliente)
                    tabla_listview.controls.append(fila)
                tabla_listview.update()
            else:
                pass

        except sqlite3.Error as e:
            print("Error al filtrar clientes:", e)
        finally:
            if conn:
                conn.close()

    # Asociar eventos de cambio para aplicar la búsqueda
    for filtro in filtros.values():
        filtro.on_change = lambda e: buscar_cliente()

    switch_proximas_renovaciones.on_change = lambda e: buscar_cliente()
    switch_vencidos_recientes.on_change = lambda e: buscar_cliente()

    # Encuentra el ListView de la tabla personalizada
    tabla_listview = None
    if hasattr(tabla_con_scroll, "controls"):
        for c in tabla_con_scroll.controls:
            if isinstance(c, ft.ListView):
                tabla_listview = c
                break
        if tabla_listview is None and isinstance(tabla_con_scroll, ft.ListView):
            tabla_listview = tabla_con_scroll
    elif isinstance(tabla_con_scroll, ft.ListView):
        tabla_listview = tabla_con_scroll
    else:
        tabla_listview = tabla_con_scroll

    return ft.Column(
        controls=[
            ft.Row([filtros["nombre"], filtros["apellido"], filtros["estado"], filtros["genero"], filtros["apta_medica"]], spacing=int(10*scale)),
            ft.Row([filtros["dni"], switch_proximas_renovaciones, switch_vencidos_recientes], spacing=int(10*scale)),
        ],
        spacing=int(20*scale)
    )

