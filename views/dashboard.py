import flet as ft
import json
from views.Menu import vista_menu  # Importamos el menú
from views.add_client import vista_add_client

# Cargar configuración desde config.json
with open("config.json", "r") as config_file:
    configuracion = json.load(config_file)

# Obtener colores desde el archivo
color_fondo = configuracion.get("color_fondo", "#FFFFFF")
color_tematica = configuracion.get("color_tematica", "#FFFFFF")
color_letras = configuracion.get("color_letras", "#000000")

def vista_dashboard(page):
    # Aplicar color de fondo
    page.bgcolor = color_fondo
    page.window_maximized = True

    # Crear una instancia de diálogo global
    detalles_cliente_dialog = ft.AlertDialog(
        modal=True,  # Asegura comportamiento de ventana emergente
        open=False   # Inicialmente cerrado
    )
    page.dialog = detalles_cliente_dialog  # Lo asignamos a la página

    # Función para cambiar a la vista de agregar cliente
    def ir_agregar_cliente(e):
        page.clean()  # Limpia la vista actual
        vista_add_client(page)
        page.update()

    # Función para buscar clientes
    def buscar_cliente(e):
        query = search_input.value.lower()
        for fila in tabla_clientes.rows:
            client_name = fila.cells[0].content.value.lower()
            fila.visible = query in client_name
        page.update()

    # Función para cerrar el diálogo
    def close_dialog(e):
        detalles_cliente_dialog.open = False
        page.update()

    # Función para mostrar detalles del cliente
    def mostrar_detalles(cliente):
        print(f"Cliente seleccionado: {cliente}")  # Debug para verificar datos
        # Actualizamos el contenido del diálogo con la información del cliente
        detalles_cliente_dialog.title = ft.Text(f"Detalles del Cliente: {cliente['nombre']}")
        detalles_cliente_dialog.content = ft.Column([
            ft.Text(f"Nombre: {cliente['nombre']}"),
            ft.Text(f"Apellido: {cliente['apellido']}"),
            ft.Text(f"Sexo: {cliente['sexo']}"),
            ft.Text(f"Edad: {cliente['edad']} años"),
            ft.Text(f"Email: {cliente['email']}"),
            ft.Text(f"Enfermedades: {cliente['enfermedades'] or 'Ninguna'}"),
            ft.Text(f"Apta Médica: {'Sí' if cliente['apta_medica'] else 'No'}"),
            ft.Text(f"Inicio de Membresía: {cliente['inicio_membresia']}"),
            ft.Text(f"Vencimiento de Membresía: {cliente['fin_membresia']}")
        ])
        detalles_cliente_dialog.actions = [
            ft.TextButton("Cerrar", on_click=close_dialog)
        ]
        detalles_cliente_dialog.open = True  # Abrimos el diálogo
        page.update()  # Aseguramos que se reflejen los cambios en la página

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
        label="Buscar clientes...",
        width=400,
        on_change=buscar_cliente
    )

    # Tabla profesional
    tabla_clientes = ft.DataTable(
    columns=[
        ft.DataColumn(ft.Container(ft.Text("Nombre", weight="bold"),
                    alignment=ft.alignment.center, width=100)),
        ft.DataColumn(ft.Container(ft.Text("Apellido", weight="bold"),
                    alignment=ft.alignment.center, width=100)),
        ft.DataColumn(ft.Container(ft.Text("Sexo", weight="bold"),
                    alignment=ft.alignment.center, width=100)),
        ft.DataColumn(ft.Container(ft.Text("Edad", weight="bold"),
                    alignment=ft.alignment.center, width=100)),
        ft.DataColumn(ft.Container(ft.Text("Vencimiento", weight="bold"),
                    alignment=ft.alignment.center, width=100)),
        ft.DataColumn(ft.Container(ft.Text("Acción", weight="bold"),
                    alignment=ft.alignment.center, width=100))  # Elimina el Container aquí
    ],
    rows=[
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Container(
                    ft.Text(cliente["nombre"]),
                    alignment=ft.alignment.center,
                    width=100
                )),
                ft.DataCell(ft.Container(
                    ft.Text(cliente["apellido"]),
                    alignment=ft.alignment.center,
                    width=100
                )),
                ft.DataCell(ft.Container(
                    ft.Text(cliente["sexo"]),
                    alignment=ft.alignment.center,
                    width=100
                )),
                ft.DataCell(ft.Container(
                    ft.Text(str(cliente["edad"])),
                    alignment=ft.alignment.center,
                    width=100
                )),
                ft.DataCell(ft.Container(
                    ft.Text(cliente["fin_membresia"]),
                    alignment=ft.alignment.center,
                    width=100
                )),
                ft.DataCell(ft.Container(
                    ft.IconButton(
                        icon=ft.icons.VISIBILITY,
                        tooltip="Ver Detalles",
                        on_click=lambda e, c=cliente: mostrar_detalles(c)
                    ),
                    alignment=ft.alignment.center,
                    width=100
                )),
            ]
        )
        for cliente in clientes
    ]
)

    # Usar el menú definido en Menu.py
    menu = vista_menu(page)

    # Crear un header para "Clientes del Gimnasio" con el botón +
    header_clientes = ft.Row(
        controls=[
            ft.Text("Clientes del Gimnasio", size=20, weight="bold", color=color_letras),
            ft.IconButton(icon=ft.icons.ADD, tooltip="Agregar Cliente", on_click=ir_agregar_cliente)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    # Layout principal
    layout = ft.Column([
        menu,
        ft.Container(
            ft.Text("Nombre del Gimnasio", size=24, weight="bold", color=color_letras),
            alignment=ft.alignment.center,
            padding=10
        ),
        ft.Container(search_input, alignment=ft.alignment.center, padding=10),
        ft.Container(header_clientes, alignment=ft.alignment.center, padding=5),
        ft.Container(
            tabla_clientes,
            expand=True,
            alignment=ft.alignment.top_center,
            padding=10,
        )
    ], spacing=10, expand=True)

    page.add(layout)
    page.update()

if __name__ == "__main__":
    ft.app(target=vista_dashboard)
