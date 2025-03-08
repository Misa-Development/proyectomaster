# views/Productos.py
import flet as ft
from views.Menu import vista_menu

def vista_productos(page):
    # Título de productos
    page.title = "Productos"
    
    # Menú horizontal en la esquina superior izquierda
    menu = vista_menu(page)
    
    # Contenido de productos
    productos_content = ft.Column([
        ft.Container(
            content=ft.Text("Productos", size=24),
            alignment=ft.alignment.center,
            expand=True
        )
        # Aquí puedes agregar más contenido de productos
    ], alignment=ft.MainAxisAlignment.CENTER, expand=True)

    # Layout principal con el menú horizontal en la parte superior izquierda
    layout = ft.Column([menu, productos_content], expand=True)
    page.add(layout)
