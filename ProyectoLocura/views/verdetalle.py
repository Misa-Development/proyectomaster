import flet as ft

def vista_detalles_cliente(cliente, color_letras, color_tematica, cliente_panel):
    # Necesitamos obtener el objeto `page` desde el cliente_panel
    page = cliente_panel.page

    # Función para cerrar el cuadro de diálogo
    def cerrar_dialogo():
        page.dialog.open = False
        page.update()

    # Función para mostrar la confirmación antes de eliminar
    def confirmar_eliminacion_cliente():
        def eliminar_cliente_confirmado(e):
            print(f"Cliente {cliente['nombre']} {cliente['apellido']} eliminado.")  # Aquí va la lógica para eliminar el cliente
            cerrar_dialogo()  # Cierra el cuadro de diálogo después de confirmar
            ocultar_detalles_cliente(cliente_panel)

        # Mostrar cuadro de diálogo de confirmación
        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmación"),
            content=ft.Text(f"¿Estás seguro de que deseas eliminar a {cliente['nombre']} {cliente['apellido']}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo()),
                ft.TextButton("Eliminar", on_click=eliminar_cliente_confirmado),
            ],
        )
        page.dialog.open = True
        page.update()

    # Función para editar cliente (puede abrir un formulario o una nueva vista)
    def editar_cliente():
        print(f"Editar cliente: {cliente['nombre']} {cliente['apellido']}")  # Aquí puedes implementar la lógica para editar el cliente

    # Este es el contenido del panel con los detalles del cliente
    return ft.Column(
        controls=[
            ft.IconButton(  # Botón para cerrar el panel
                icon=ft.icons.CLOSE,
                tooltip="Cerrar",
                icon_color=color_letras,
                on_click=lambda e: ocultar_detalles_cliente(cliente_panel),
            ),
            ft.Text(
                f"Detalles de {cliente['nombre']} {cliente['apellido']}",
                size=24,
                weight="bold",
                color=color_letras,
            ),
            ft.Text(f"Sexo: {cliente['sexo']}", size=16, color=color_letras),
            ft.Text(f"Apta Médica: {'Sí' if cliente['apta_medica'] else 'No'}", size=16, color=color_letras),
            ft.Text(f"Enfermedades: {cliente['enfermedades'] if 'enfermedades' in cliente else 'No especificado'}", size=16, color=color_letras),
            ft.Text(f"Edad: {cliente['edad']}", size=16, color=color_letras),
            ft.Text(f"Fecha de Inicio: {cliente['fecha_inicio']}", size=16, color=color_letras),
            ft.Text(f"Fecha de Vencimiento: {cliente['fecha_vencimiento']}", size=16, color=color_letras),
            ft.Row(  # Botones de acción
                controls=[
                    ft.ElevatedButton(
                        text="Eliminar Cliente",
                        icon=ft.icons.DELETE,
                        on_click=lambda e: confirmar_eliminacion_cliente(),
                        style=ft.ButtonStyle(
                            color=ft.colors.RED,
                            bgcolor=color_letras,
                        ),
                    ),
                    ft.ElevatedButton(
                        text="Editar Cliente",
                        icon=ft.icons.EDIT,
                        on_click=lambda e: editar_cliente(),
                        style=ft.ButtonStyle(
                            color=color_tematica,
                            bgcolor=color_letras
                        ),
                    ),
                ],
                spacing=20,
            ),
        ]
    )

def ocultar_detalles_cliente(cliente_panel):
    cliente_panel.width = 0  # Ocultar el panel lateral reduciendo su ancho
    cliente_panel.content = None  # Limpia el contenido del panel
    cliente_panel.update()