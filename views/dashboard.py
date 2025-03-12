import flet as ft
import json
from views.Menu import vista_menu  # Importamos el menú
from views.add_client import vista_add_client, open_custom_date_picker_modal
from views.Propaganda import vista_propaganda


# Cargar configuración desde config.json
with open("config.json", "r") as config_file:
    configuracion = json.load(config_file)

# Obtener colores y nombre del gimnasio desde el archivo
color_fondo = configuracion.get("color_fondo", "#FFFFFF")
color_tematica = configuracion.get("color_tematica", "#FF5733")
color_letras = configuracion.get("color_letras", "#000000")
nombre_gimnasio = configuracion.get("nombre_gimnasio", "Mi Gimnasio")


def vista_dashboard(page):
    # Leer configuración actualizada de config.json
    with open("config.json", "r") as config_file:
        configuracion = json.load(config_file)
        
    # Configurar colores y nombre
    color_fondo = configuracion.get("color_fondo", "#FFFFFF")
    color_letras = configuracion.get("color_letras", "#000000")
    color_tematica = configuracion.get("color_tematica", "#FF5733")
    nombre_gimnasio = configuracion.get("nombre_gimnasio", "Mi Gimnasio")

    # Aplicar color de fondo
    page.bgcolor = color_fondo
    page.window_maximized = True

    # Diálogo global para detalles del cliente
    detalles_cliente_dialog = ft.AlertDialog(
        modal=True,
        open=False,
        shape=ft.RoundedRectangleBorder(radius=10),  # Borde redondeado
    )
    page.dialog = detalles_cliente_dialog

    # Función para cambiar a la vista de agregar cliente
    def ir_agregar_cliente(e):
        page.clean()
        vista_add_client(page)
        page.update()

    # Función para buscar clientes
    def buscar_cliente(e):
        query = search_input.value.lower()
        genero_filtro = filtro_genero.value
        apta_medica_filtro = filtro_apta_medica.value

        for fila, cliente in zip(tabla_clientes.rows, clientes):
            client_name = cliente["nombre"].lower()
            client_genero = cliente["sexo"]
            client_apta_medica = "Sí" if cliente["apta_medica"] else "No"

            # Filtrar por nombre, género y apta médica
            visible = query in client_name and \
                      (genero_filtro == "Todos" or genero_filtro == client_genero) and \
                      (apta_medica_filtro == "Todos" or apta_medica_filtro == client_apta_medica)
            fila.visible = visible
        page.update()

    # Función para filtrar clientes por rango de fechas
    def filtrar_por_fecha(e):
        try:
            desde = ft.datetime.strptime(txt_fecha_desde.value, "%d/%m/%Y")
            hasta = ft.datetime.strptime(txt_fecha_hasta.value, "%d/%m/%Y")
        except ValueError:
            return  # No filtrar si las fechas no son válidas

        for fila, cliente in zip(tabla_clientes.rows, clientes):
            inicio = ft.datetime.strptime(cliente["inicio_membresia"], "%d/%m/%Y")
            fin = ft.datetime.strptime(cliente["fin_membresia"], "%d/%m/%Y")
            visible = inicio >= desde and fin <= hasta
            fila.visible = visible
        page.update()

    # Mostrar calendario para selección de fechas
    def show_calendar(field):
        def on_date_selected(selected_date):
            field.value = selected_date.strftime("%d/%m/%Y")
            page.update()
        overlay = open_custom_date_picker_modal(page, None, on_date_selected)
        page.overlay.append(overlay)
        page.update()

    # Datos de ejemplo
    clientes = [
        {"nombre": "Juan", "apellido": "Pérez", "sexo": "Masculino", "edad": 25,
         "email": "juan.perez@gmail.com", "enfermedades": "Ninguna",
         "apta_medica": True, "inicio_membresia": "01/01/2023", "fin_membresia": "31/12/2023"},
        {"nombre": "María", "apellido": "Gómez", "sexo": "Femenino", "edad": 30,
         "email": "maria.gomez@gmail.com", "enfermedades": "Asma",
         "apta_medica": False, "inicio_membresia": "01/02/2023", "fin_membresia": "31/01/2024"}
    ]

    # Input de búsqueda
    search_input = ft.TextField(
        label="Buscar clientes por nombre...",
        width=400,
        prefix_icon=ft.icons.SEARCH,
        border_radius=10,
        color=color_letras,
        on_change=buscar_cliente
    )

    # Inputs para rango de fechas
    txt_fecha_desde = ft.TextField(label="Desde", read_only=True, width=200)
    btn_fecha_desde = ft.IconButton(icon=ft.icons.CALENDAR_MONTH, on_click=lambda e: show_calendar(txt_fecha_desde))
    txt_fecha_hasta = ft.TextField(label="Hasta", read_only=True, width=200)
    btn_fecha_hasta = ft.IconButton(icon=ft.icons.CALENDAR_MONTH, on_click=lambda e: show_calendar(txt_fecha_hasta))
    btn_aplicar_filtro = ft.ElevatedButton(
        text="Filtrar por Fechas",
        on_click=filtrar_por_fecha,
        bgcolor=color_tematica,
        color=ft.colors.WHITE
    )

    filtro_rango_fechas = ft.Row(
        controls=[
            ft.Row([txt_fecha_desde, btn_fecha_desde], spacing=10),
            ft.Row([txt_fecha_hasta, btn_fecha_hasta], spacing=10),
            btn_aplicar_filtro
        ],
        spacing=20
    )

    # Filtros de género y apta médica
    filtro_genero = ft.Dropdown(
        label="Género",
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Masculino"),
            ft.dropdown.Option("Femenino")
        ],
        value="Todos",
        width=200,
        border_radius=10,
        on_change=buscar_cliente
    )

    filtro_apta_medica = ft.Dropdown(
        label="Apta Médica",
        options=[
            ft.dropdown.Option("Todos"),
            ft.dropdown.Option("Sí"),
            ft.dropdown.Option("No")
        ],
        value="Todos",
        width=200,
        border_radius=10,
        on_change=buscar_cliente
    )
        
    # Tabla profesional con estilo
    tabla_clientes = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Apellido", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Sexo", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Edad", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Vencimiento", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Acción", weight="bold", color=color_letras))
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(cliente["nombre"], color=color_letras)),
                    ft.DataCell(ft.Text(cliente["apellido"], color=color_letras)),
                    ft.DataCell(ft.Text(cliente["sexo"], color=color_letras)),
                    ft.DataCell(ft.Text(str(cliente["edad"]), color=color_letras)),
                    ft.DataCell(ft.Text(cliente["fin_membresia"], color=color_letras)),
                    ft.DataCell(ft.IconButton(
                        icon=ft.icons.VISIBILITY,
                        tooltip="Ver Detalles",
                        icon_color=color_tematica,
                        on_click=lambda e, c=cliente: buscar_cliente(e)
                    )),
                ]
            )
            for cliente in clientes
        ]
    )

    # Usar el menú definido en Menu.py
    menu = vista_menu(page)

    # Header visualmente atractivo
    header_clientes = ft.Row(
        controls=[
            ft.Text("Clientes del Gimnasio", size=24, weight="bold", color=color_letras),
            ft.IconButton(icon=ft.icons.ADD, tooltip="Agregar Cliente", icon_color=color_letras, on_click=ir_agregar_cliente)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    # Layout principal
        # Layout principal con dos columnas
    layout = ft.Row([
    ft.Column([  # Columna izquierda
        menu,
        ft.Container(
    content=ft.Text(
        nombre_gimnasio,
        size=36,
        weight="bold",
        color=color_letras
    ),
    alignment=ft.alignment.center,
    padding=20,
    gradient=ft.LinearGradient(
        colors=[color_tematica,color_tematica, "WHITE"],  # Degradado entre dos colores
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right
    ),
    border_radius=10
)


,

            ft.Container(
                ft.Column(
                    controls=[
                        search_input,
                        filtro_rango_fechas,
                        ft.Row([filtro_genero, filtro_apta_medica], spacing=15)
                    ],
                    spacing=15
                ),
                alignment=ft.alignment.center,
                padding=10
            ),
            ft.Container(header_clientes, alignment=ft.alignment.center, padding=10),
            ft.Container(
                tabla_clientes,
                expand=True,
                alignment=ft.alignment.top_center,
                padding=10,
            )
        ], spacing=10, expand=True),  # Columna izquierda expandida
        ft.Container(
        vista_propaganda(page),
        width=300  # Ajusta el ancho a 300px (puedes modificar este valor)
    )
  # Columna derecha: módulo Propaganda
    ], spacing=20, expand=True)

    page.add(layout)
    page.update()

if __name__ == "__main__":
    ft.app(target=vista_dashboard)
