import flet as ft

def main(page: ft.Page):
    dialog_container = ft.Container(
        visible=False,
        bgcolor=ft.colors.WHITE,
        padding=20,
        border_radius=10,
        alignment=ft.alignment.center,
        content=ft.Column([
            ft.Text("Diálogo de prueba"),
            ft.ElevatedButton("Cerrar", on_click=lambda e: hide_dialog())
        ], spacing=10),
    )

    def show_dialog(e):
        dialog_container.visible = True
        page.update()

    def hide_dialog():
        dialog_container.visible = False
        page.update()

    btn = ft.ElevatedButton("Mostrar diálogo", on_click=show_dialog)
    page.add(btn, dialog_container)
    page.update()

ft.app(target=main, view=ft.WEB_BROWSER)
