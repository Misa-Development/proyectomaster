import flet as ft
from database.db import obtener_ingresos
from views.custom_date_picker import open_custom_date_picker_modal

def actualizar_tabla_ingresos(tabla_ingresos, filtros, color_letras, page):
    cliente = filtros.get("cliente", "").lower()
    articulo = filtros.get("articulo", "")
    fecha = filtros.get("fecha", "")

    def cumple_filtros(ingreso):
        return (
            (cliente in ingreso["cliente"].lower())
            and (articulo in ("", "__todos__") or ingreso["articulo"] == articulo)
            and (fecha == "" or ingreso["fecha"] == fecha)
        )

    tabla_ingresos.rows = [
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(ingreso["cliente"], color=color_letras)),
                ft.DataCell(ft.Text(ingreso["articulo"], color=color_letras)),
                ft.DataCell(ft.Text(f"${ingreso['monto']:.2f}", color=color_letras)),
                ft.DataCell(ft.Text(str(ingreso.get("cantidad", 1)), color=color_letras)),
                ft.DataCell(ft.Text(ingreso["fecha"], color=color_letras)),
                ft.DataCell(ft.Text(ingreso["metodo_pago"], color=color_letras)),
            ]
        )
        for ingreso in reversed(obtener_ingresos())  # Para que los más recientes estén arriba
        if cumple_filtros(ingreso)
    ]
    page.update()

def filtros_ingresos(page, tabla_ingresos, color_letras, color_tematica):
    filtros = {"cliente": "", "articulo": "__todos__", "fecha": ""}

    articulos = sorted({ing["articulo"] for ing in obtener_ingresos()})
    CAMPO_ANCHO = 200

    cliente_field = ft.TextField(
        label="Cliente",
        hint_text="Buscar por cliente...",
        prefix_icon=ft.Icons.SEARCH,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_tematica,
        label_style=ft.TextStyle(color=color_letras),
        width=CAMPO_ANCHO,
        on_change=lambda e: (
            filtros.update({"cliente": e.control.value}),
            actualizar_tabla_ingresos(tabla_ingresos, filtros, color_letras, page)
        ),
    )

    articulo_dropdown = ft.Dropdown(
        label="Artículo",
        options=[ft.dropdown.Option("__todos__", "Todos")] + [ft.dropdown.Option(a, a) for a in articulos],
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_tematica,
        label_style=ft.TextStyle(color=color_letras),
        width=CAMPO_ANCHO,
        value="__todos__",
        on_change=lambda e: (
            filtros.update({"articulo": e.control.value}),
            actualizar_tabla_ingresos(tabla_ingresos, filtros, color_letras, page)
        ),
    )

    fecha_field = ft.TextField(
        label="Fecha",
        hint_text="DD/MM/YYYY",
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_tematica,
        label_style=ft.TextStyle(color=color_letras),
        width=CAMPO_ANCHO,
        read_only=True,
    )

    def show_date_picker(e):
        def on_date_selected(date):
            fecha_field.value = date.strftime("%d/%m/%Y")
            fecha_field.update()
            filtros.update({"fecha": fecha_field.value})
            actualizar_tabla_ingresos(tabla_ingresos, filtros, color_letras, page)
        page.overlay.append(open_custom_date_picker_modal(page, None, on_date_selected))
        page.update()

    fecha_field.suffix = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=show_date_picker,
        style=ft.ButtonStyle(bgcolor="transparent", color=color_tematica),
        tooltip="Seleccionar fecha"
    )

    def limpiar_campos(e):
        cliente_field.value = ""
        cliente_field.update()
        articulo_dropdown.value = "__todos__"
        articulo_dropdown.update()
        fecha_field.value = ""
        fecha_field.update()
        filtros.update({"cliente": "", "articulo": "__todos__", "fecha": ""})
        actualizar_tabla_ingresos(tabla_ingresos, filtros, color_letras, page)

    boton_limpiar = ft.ElevatedButton(
        text="Limpiar campos",
        on_click=limpiar_campos,
        bgcolor=color_tematica,
        color="black",
        width=CAMPO_ANCHO
    )

    return ft.Column([
        ft.Text("Filtros de Ingresos", size=18, weight="bold", color=color_letras),
        ft.Row([
            cliente_field,
            articulo_dropdown,
            fecha_field,
            boton_limpiar
        ], spacing=10)
    ], spacing=10)