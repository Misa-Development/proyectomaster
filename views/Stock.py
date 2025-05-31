import flet as ft
import json
from database.db import conectar_db  # Asegurarte de importar conectar_db desde db.py
from views.Menu import vista_menu
from views.tablastock import construir_tabla, cargar_datos_tabla

# Ruta del archivo de configuración
CONFIG_FILE = "config.json"

def cargar_configuracion():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "color_fondo": "#FFFFFF",
            "color_letras": "#000000",
            "color_tematica": "#000000",
        }

def vista_stock(page):
    config = cargar_configuracion()
    color_fondo = config["color_fondo"]
    color_letras = config["color_letras"]
    color_tematica = config["color_tematica"]

    menu = vista_menu(page)

    def guardar_stock(e):
        conn = conectar_db()  # Usar siempre la función conectar_db
        cursor = conn.cursor()
        articulo = articulo_input.value
        cantidad = cantidad_input.value
        monto_compra = monto_compra_input.value
        monto_venta = monto_venta_input.value

        if articulo and cantidad and monto_compra and monto_venta:
            try:
                cursor.execute('''
                    INSERT INTO stock (articulo, cantidad, monto_de_compra, monto_de_venta)
                    VALUES (?, ?, ?, ?)
                ''', (articulo, cantidad, float(monto_compra), float(monto_venta)))
                conn.commit()
                print("Stock guardado correctamente.")

                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Stock guardado exitosamente.", color=color_letras),
                    open=True,
                    bgcolor=color_fondo
                )

                # Limpiar campos después de guardar
                articulo_input.value = ""
                cantidad_input.value = ""
                monto_compra_input.value = ""
                monto_venta_input.value = ""

                cargar_datos_tabla(tabla, page, color_letras)  # Actualiza la tabla
            except Exception as err:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error al guardar el stock: {err}", color=color_letras),
                    open=True,
                    bgcolor="red"
                )
            finally:
                conn.close()
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Por favor, completa todos los campos.", color=color_letras),
                open=True,
                bgcolor=color_fondo
            )

        page.update()

    articulo_input = ft.TextField(
        label="Artículo",
        label_style=ft.TextStyle(color=color_letras),
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras
    )
    cantidad_input = ft.TextField(
        label="Cantidad",
        label_style=ft.TextStyle(color=color_letras),
        keyboard_type="number",
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras
    )
    monto_compra_input = ft.TextField(
        label="Monto de Compra",
        label_style=ft.TextStyle(color=color_letras),
        keyboard_type="number",
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras
    )
    monto_venta_input = ft.TextField(
        label="Monto de Venta",
        label_style=ft.TextStyle(color=color_letras),
        keyboard_type="number",
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras
    )

    guardar_button = ft.ElevatedButton(
        text="Guardar Stock",
        on_click=guardar_stock,
        bgcolor=color_tematica,
        color=color_letras
    )

    tabla = construir_tabla(color_letras)
    cargar_datos_tabla(tabla, page, color_letras)

    layout = ft.Container(
        content=ft.Column(
            controls=[
                menu,
                ft.Text("Gestión de Stock", style=ft.TextThemeStyle.HEADLINE_MEDIUM, color=color_letras),
                articulo_input,
                cantidad_input,
                monto_compra_input,
                monto_venta_input,
                guardar_button,
                ft.Text("Stock Actual", style=ft.TextThemeStyle.TITLE_LARGE, color=color_letras),
                ft.Container(
                    ft.ListView([tabla], height=220),
                    border=ft.border.all(1, color_tematica),
                    border_radius=5,
                    padding=10
                )
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor=color_fondo,
        padding=10
    )

    page.add(layout)

# Ejecutar la aplicación
if __name__ == "__main__":
    ft.app(target=vista_stock)