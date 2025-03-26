import flet as ft
import sqlite3
from database.db import conectar_db
from views.custom_date_picker import open_custom_date_picker_modal

# Vista para los filtros conectados
def vista_filtros(page, color_letras, open_custom_date_picker_modal, tabla_con_scroll, clientes, mostrar_detalles_cliente):
    tabla_clientes = tabla_con_scroll.controls[0]  # Primer control del ListView

    # Campo de búsqueda
    search_input = ft.TextField(
        label="Buscar clientes por nombre",
        prefix_icon=ft.icons.SEARCH,
        width=300,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        hint_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
    )

    # Filtro por género
    filtro_genero = ft.Dropdown(
        label="Filtrar por género",
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Masculino"),
            ft.dropdown.Option("Femenino"),
        ],
        value="Todos",
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        hint_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
    )

    # Filtro por aptitud médica
    filtro_apta_medica = ft.Dropdown(
        label="Filtrar por apta médica",
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Sí"),
            ft.dropdown.Option("No"),
        ],
        value="Todos",
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        hint_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
    )

    # Filtro por estado (Activo/Inactivo)
    filtro_estado = ft.Dropdown(
        label="Filtrar por estado",
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Activo"),
            ft.dropdown.Option("Inactivo"),
        ],
        value="Todos",
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        hint_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
    )

    # Campos de fechas
    txt_fecha_desde = ft.TextField(
        label="Inicio de membresía desde",
        read_only=True,
        width=150,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        hint_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
    )
    btn_fecha_desde = ft.IconButton(
        icon=ft.icons.CALENDAR_MONTH,
        tooltip="Seleccionar fecha de inicio desde",
        on_click=lambda e: open_calendar(txt_fecha_desde, page, open_custom_date_picker_modal),
    )

    txt_fecha_hasta = ft.TextField(
        label="Inicio de membresía hasta",
        read_only=True,
        width=150,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        hint_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
    )
    btn_fecha_hasta = ft.IconButton(
        icon=ft.icons.CALENDAR_MONTH,
        tooltip="Seleccionar fecha de inicio hasta",
        on_click=lambda e: open_calendar(txt_fecha_hasta, page, open_custom_date_picker_modal),
    )

    # Función para mostrar el calendario
    def open_calendar(text_field, page, open_custom_date_picker_modal):
        def on_date_selected(selected_date):
            text_field.value = selected_date.strftime("%Y-%m-%d")  # Actualiza el campo con la fecha seleccionada
            if page.overlay:
                page.overlay.pop()  # Cierra el popup después de seleccionar la fecha
            page.update()

        overlay = open_custom_date_picker_modal(page, None, on_date_selected)
        page.overlay.append(overlay)  # Añade el popup al overlay de la página
        page.update()

    # Función para aplicar filtros
    def buscar_cliente():
        query = search_input.value.lower()
        genero = filtro_genero.value
        apta_medica = filtro_apta_medica.value
        estado = filtro_estado.value
        fecha_desde = txt_fecha_desde.value
        fecha_hasta = txt_fecha_hasta.value

        # Conectar a la base de datos y aplicar los filtros
        try:
            conn = conectar_db()
            cursor = conn.cursor()

            # Construir la consulta SQL dinámicamente
            query_sql = '''
                SELECT *, 
                CASE 
                    WHEN fecha_vencimiento >= DATE('now') THEN 'Activo'
                    ELSE 'Inactivo'
                END AS estado
                FROM clientes WHERE 1=1
            '''
            params = []

            if query:
                query_sql += " AND LOWER(nombre) LIKE ?"
                params.append(f"%{query}%")

            if genero != "Todos":
                query_sql += " AND LOWER(sexo) = ?"
                params.append(genero.lower())

            if apta_medica == "Sí":
                query_sql += " AND apta_medica = ?"
                params.append(True)
            elif apta_medica == "No":
                query_sql += " AND apta_medica = ?"
                params.append(False)

            if estado != "Todos":
                query_sql += " AND estado = ?"
                params.append(estado)

            if fecha_desde:
                query_sql += " AND fecha_inicio >= ?"
                params.append(fecha_desde)

            if fecha_hasta:
                query_sql += " AND fecha_inicio <= ?"
                params.append(fecha_hasta)

            cursor.execute(query_sql, params)
            clientes_filtrados = cursor.fetchall()

            # Actualizar las filas del DataTable
            tabla_clientes.rows.clear()
            for cliente in clientes_filtrados:
                tabla_clientes.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(cliente["nombre"], color=color_letras)),
                        ft.DataCell(ft.Text(cliente["apellido"], color=color_letras)),
                        ft.DataCell(ft.Text(cliente["sexo"], color=color_letras)),
                        ft.DataCell(ft.Text(cliente["fecha_inicio"], color=color_letras)),
                        ft.DataCell(ft.Text(cliente["fecha_vencimiento"], color=color_letras)),
                        ft.DataCell(ft.Text("Sí" if cliente["apta_medica"] else "No", color=color_letras)),
                        ft.DataCell(ft.Text(cliente["estado"], color=color_letras)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.icons.VISIBILITY,
                                tooltip="Ver Detalles",
                                on_click=lambda e, c=dict(cliente): mostrar_detalles_cliente(c)
                            )
                        ),
                    ])
                )
            page.update()
        except sqlite3.Error as e:
            print(f"Error al filtrar clientes: {e}")
        finally:
            if conn:
                conn.close()

    # Asociar eventos de cambio a la función de búsqueda
    search_input.on_change = lambda e: buscar_cliente()
    filtro_genero.on_change = lambda e: buscar_cliente()
    filtro_apta_medica.on_change = lambda e: buscar_cliente()
    filtro_estado.on_change = lambda e: buscar_cliente()

    # Diseño de los filtros
    filtros = ft.Column(
        controls=[
            ft.Row([search_input, filtro_genero, filtro_apta_medica, filtro_estado], spacing=10),
            ft.Row([txt_fecha_desde, btn_fecha_desde, txt_fecha_hasta, btn_fecha_hasta], spacing=10),
        ],
        spacing=20
    )

    return filtros