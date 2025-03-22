import flet as ft

def vista_detalles_cliente(cliente, color_letras, color_tematica, cliente_panel):
    return ft.Column(
        controls=[
            ft.Text(
                f"Detalles de {cliente['nombre']} {cliente['apellido']}", 
                size=24, 
                weight="bold", 
                color=color_tematica
            ),
            ft.Text(f"Sexo: {cliente['sexo']}", size=16, color=color_letras),
            ft.Text(f"Apta Médica: {'Sí' if cliente['apta_medica'] else 'No'}", size=16, color=color_letras),
            ft.Text(f"Enfermedades: {cliente.get('enfermedades', 'No especificado')}", size=16, color=color_letras),
            ft.Text(f"Edad: {cliente['edad']}", size=16, color=color_letras),
            ft.Text(f"Fecha de Inicio: {cliente['fecha_inicio']}", size=16, color=color_letras),
            ft.Text(f"Fecha de Vencimiento: {cliente['fecha_vencimiento']}", size=16, color=color_letras),
        ]
    )
def ocultar_detalles_cliente(cliente_panel):
    cliente_panel.visible = False
    cliente_panel.update()