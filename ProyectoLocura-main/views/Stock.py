import flet as ft
import json
from database.db import conectar_db
from views.Menu import vista_menu
from views.stocktabla import construir_tabla, cargar_datos_tabla

CONFIG_FILE = "config.json"

def cargar_configuracion():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"color_fondo": "#FFFFFF", "color_letras": "#000000", "color_tematica": "#000000"}

def crear_tabla_stock_si_no_existe():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            articulo TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            monto_de_compra REAL NOT NULL,
            monto_de_venta REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def vista_stock(page, cambiar_vista=None):
    crear_tabla_stock_si_no_existe()  # Asegura que la tabla exista antes de usarla
    page.title = "Gestión de Stock"
    config = cargar_configuracion()
    color_fondo, color_letras, color_tematica = config.get("color_fondo"), config.get("color_letras"), config.get("color_tematica")
    menu = vista_menu(page)

    def guardar_stock(e):
        conn = conectar_db()
        cursor = conn.cursor()
        valores = [campo.value for campo in (articulo_input, cantidad_input, monto_compra_input, monto_venta_input)]

        if all(valores):
            try:
                cursor.execute("INSERT INTO stock (articulo, cantidad, monto_de_compra, monto_de_venta) VALUES (?, ?, ?, ?)",
                               (valores[0], valores[1], float(valores[2]), float(valores[3])))
                conn.commit()
                page.snack_bar = ft.SnackBar(content=ft.Text("Stock guardado exitosamente.", color=color_letras), open=True, bgcolor=color_fondo)
                for campo in (articulo_input, cantidad_input, monto_compra_input, monto_venta_input): campo.value = ""
                cargar_datos_tabla(tabla, page, color_letras)
            except Exception as err:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Error al guardar el stock: {err}", color=color_letras), open=True, bgcolor="red")
            finally:
                conn.close()
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text("Por favor, completa todos los campos.", color=color_letras), open=True, bgcolor=color_fondo)

        page.update()

    def crear_textfield(label, tipo="text"):
        return ft.TextField(label=label, label_style=ft.TextStyle(color=color_letras), text_style=ft.TextStyle(color=color_letras),
                            border_color=color_tematica, keyboard_type="number" if tipo == "number" else "text")

    articulo_input, cantidad_input, monto_compra_input, monto_venta_input = [crear_textfield(label, tipo) for label, tipo in [
        ("Artículo", "text"), ("Cantidad", "number"), ("Monto de Compra", "number"), ("Monto de Venta", "number")]]

    guardar_button = ft.ElevatedButton(text="Guardar Stock", on_click=guardar_stock, bgcolor=color_tematica, color=color_letras)
    tabla = construir_tabla(color_letras)
    cargar_datos_tabla(tabla, page, color_letras)

    layout = ft.Container(
        content=ft.Column(controls=[
            menu, ft.Text("Gestión de Stock", style=ft.TextThemeStyle.HEADLINE_MEDIUM, color=color_letras),
            articulo_input, cantidad_input, monto_compra_input, monto_venta_input, guardar_button,
            ft.Text("Stock Actual", style=ft.TextThemeStyle.TITLE_LARGE, color=color_letras),
            ft.Container(ft.ListView([tabla], height=220), border=ft.border.all(1, color_tematica), border_radius=5, padding=10)
        ], spacing=10, alignment=ft.MainAxisAlignment.START),
        bgcolor=color_fondo, padding=10
    )

    page.add(layout)
    return layout

if __name__ == "__main__":
    ft.app(target=vista_stock)