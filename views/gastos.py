import flet as ft

def vista_gastos(page):
    # Limpiar la página
    page.controls.clear()

    # Título de la sección
    titulo = ft.Text("Registro de Gastos", size=24, weight="bold")

    # Formulario para registrar gastos
    descripcion = ft.TextField(label="Descripción")
    monto = ft.TextField(label="Monto", keyboard_type=ft.KeyboardType.NUMBER)
    fecha = ft.TextField(label="Fecha (dd/mm/aaaa)")
    
    def registrar_gasto(e):
        # Lógica para guardar el gasto
        print(f"Gasto registrado: {descripcion.value}, {monto.value}, {fecha.value}")
        descripcion.value = ""
        monto.value = ""
        fecha.value = ""
        page.update()

    boton_registrar = ft.ElevatedButton("Registrar Gasto", on_click=registrar_gasto)

    # Layout principal
    layout = ft.Column([
        titulo,
        descripcion,
        monto,
        fecha,
        boton_registrar
    ], alignment=ft.MainAxisAlignment.START, expand=True)

    page.add(layout)
    page.update()
