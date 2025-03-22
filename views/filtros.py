import flet as ft

# Función para manejar el popup del calendario
def open_custom_date_picker_modal(page, initial_date, on_date_selected):
    def cerrar_dialogo(e):
        page.dialog.open = False  # Cierra el popup
        page.update()

    date_picker = ft.DatePicker(
        value=initial_date,  # Fecha inicial
        on_change=lambda e: on_date_selected(e.control.value)  # Evento para seleccionar la fecha
    )

    return ft.AlertDialog(
        modal=True,
        title=ft.Text("Selecciona una fecha"),
        content=date_picker,
        actions=[
            ft.TextButton("Cerrar", on_click=cerrar_dialogo)  # Botón para cerrar el modal
        ]
    )

# Vista para los filtros
def vista_filtros(page, color_letras, open_custom_date_picker_modal, tabla_clientes, clientes):
    # Componentes del filtro
    search_input = ft.TextField(
        label="Buscar clientes",
        prefix_icon=ft.icons.SEARCH,
        width=300,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
    )

    filtro_genero = ft.Dropdown(
        label="Género",
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Masculino"),
            ft.dropdown.Option("Femenino"),
        ],
        value="Todos",
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
    )

    filtro_apta_medica = ft.Dropdown(
        label="Apta Médica",
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Sí"),
            ft.dropdown.Option("No"),
        ],
        value="Todos",
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
    )

    txt_fecha_desde = ft.TextField(
        label="Desde",
        read_only=True,
        width=150,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
    )

    btn_fecha_desde = ft.IconButton(
        icon=ft.icons.CALENDAR_MONTH,
        tooltip="Seleccionar Fecha Desde",
        on_click=lambda e: show_calendar(txt_fecha_desde, page, open_custom_date_picker_modal),
    )

    txt_fecha_hasta = ft.TextField(
        label="Hasta",
        read_only=True,
        width=150,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
    )

    btn_fecha_hasta = ft.IconButton(
        icon=ft.icons.CALENDAR_MONTH,
        tooltip="Seleccionar Fecha Hasta",
        on_click=lambda e: show_calendar(txt_fecha_hasta, page, open_custom_date_picker_modal),
    )

    # Función para mostrar el calendario
    def show_calendar(field, page, open_custom_date_picker_modal):
        def on_date_selected(selected_date):
            if selected_date:
                field.value = selected_date.strftime("%d/%m/%Y")  # Actualiza el campo con la fecha seleccionada
                page.dialog.open = False
                page.update()

        overlay = open_custom_date_picker_modal(page, None, on_date_selected)
        page.dialog = overlay
        page.dialog.open = True
        page.overlay.append(overlay)  # Agrega el modal al layout
        page.update()

    # Función para buscar clientes
    def buscar_cliente(e):
        query = search_input.value.lower()
        for fila, cliente in zip(tabla_clientes.rows, clientes):
            client_name = cliente.get("nombre", "").lower()  # Usa `.get()` porque `cliente` es un diccionario
            visible = query in client_name
            fila.visible = visible
        page.update()
        # Asociar el callback a los eventos de cambio en los filtros
        search_input.on_change = buscar_cliente
        filtro_genero.on_change = buscar_cliente
        filtro_apta_medica.on_change = buscar_cliente

    # Estructura del layout de filtros
    filtros = ft.Row(
        controls=[
            search_input,
            filtro_genero,
            txt_fecha_desde, btn_fecha_desde,
            txt_fecha_hasta, btn_fecha_hasta,
            filtro_apta_medica,
        ],
        spacing=10,
    )

    return filtros