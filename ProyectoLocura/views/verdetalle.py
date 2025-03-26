import flet as ft

def vista_detalles_cliente(cliente, color_letras, color_tematica, cliente_panel):
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
        ]
    )

def ocultar_detalles_cliente(cliente_panel):
    cliente_panel.width = 0  # Ocultar el panel lateral reduciendo su ancho
    cliente_panel.content = None  # Limpia el contenido del panel
    cliente_panel.update()