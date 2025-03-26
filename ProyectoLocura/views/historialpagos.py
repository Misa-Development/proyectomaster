import flet as ft
from database.db import obtener_historial_pagos, insertar_ingreso
from views.Menu import vista_menu  # Importar el menú

def vista_historial_pagos(page):
    page.title = "Historial de Pagos y Gestión de Ingresos"
    page.scroll = "auto"

    # Obtener datos iniciales de la base de datos
    datos_pagos = obtener_historial_pagos()

    # Barra de búsqueda para filtrar datos en la tabla
    filtro = ft.TextField(
        label="Buscar cliente en pagos",
        hint_text="Escribe el nombre del cliente...",
        on_change=lambda e: actualizar_tabla_pagos(filtro.value),
        expand=True
    )

    # Crear filas dinámicas de historial de pagos (por filtro)
    def crear_filas_historial_pagos(valor_filtro):
        datos_filtrados = [pago for pago in datos_pagos if valor_filtro.lower() in pago["cliente"].lower()]
        return [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(pago["cliente"])),
                    ft.DataCell(ft.Text(f"${pago['monto']:.2f}")),
                    ft.DataCell(ft.Text(pago["fecha_pago"])),
                    ft.DataCell(ft.Text(pago["metodo_pago"])),
                ]
            )
            for pago in datos_filtrados
        ]

    # Tabla dinámica del historial de pagos
    tabla_historial_pagos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Cliente")),
            ft.DataColumn(ft.Text("Monto")),
            ft.DataColumn(ft.Text("Fecha de Pago")),
            ft.DataColumn(ft.Text("Método de Pago")),
        ],
        rows=crear_filas_historial_pagos(""),  # Mostrar todas las filas inicialmente
        bgcolor="#FFFFFF",
        border_radius=10,
        horizontal_lines=True,
        column_spacing=10,
        heading_row_color=ft.colors.LIGHT_BLUE_100
    )

    # Función para actualizar la tabla según el filtro
    def actualizar_tabla_pagos(valor_filtro):
        tabla_historial_pagos.rows = crear_filas_historial_pagos(valor_filtro)
        page.update()

    # Inputs para agregar ingresos
    input_articulo = ft.TextField(label="Artículo", width=200)
    input_fecha = ft.TextField(label="Fecha (DD/MM/AAAA)", width=150)
    input_monto = ft.TextField(label="Monto", width=150)
    input_cliente = ft.TextField(label="Cliente", width=200)

    # Función para agregar un nuevo ingreso
    def agregar_ingreso(e):
        articulo = input_articulo.value
        monto = input_monto.value
        cliente = input_cliente.value
        fecha = input_fecha.value

        if not articulo or not monto or not cliente or not fecha:
            page.snack_bar = ft.SnackBar(content=ft.Text("Por favor, completa todos los campos antes de agregar el ingreso."))
            page.snack_bar.open = True
            return

        try:
            monto_float = float(monto)
            insertar_ingreso(articulo, monto_float, fecha, cliente)
            # Limpiar los campos después de agregar el ingreso
            input_articulo.value = ""
            input_fecha.value = ""
            input_monto.value = ""
            input_cliente.value = ""
            page.snack_bar = ft.SnackBar(content=ft.Text("Ingreso agregado exitosamente."))
            page.snack_bar.open = True
            page.update()
        except ValueError:
            page.snack_bar = ft.SnackBar(content=ft.Text("El monto debe ser un número válido."))
            page.snack_bar.open = True

    # Botón para agregar ingreso
    boton_agregar_ingreso = ft.ElevatedButton("Agregar ingreso", on_click=agregar_ingreso)

    # Layout de filtros y formularios
    layout_filtros_prompts = ft.Column(
        controls=[
            ft.Text("Gestión de Historial e Ingresos", size=28, weight="bold"),
            filtro,  # Barra de búsqueda dinámica
            ft.Row([input_articulo, input_fecha, input_monto, input_cliente, boton_agregar_ingreso], spacing=10)
        ],
        spacing=20
    )

    # Diseño principal que incluye el menú
    layout = ft.Column(
        controls=[
            vista_menu(page),  # Menú superior
            layout_filtros_prompts,
            tabla_historial_pagos
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=20
    )

    page.add(layout)
    page.update()