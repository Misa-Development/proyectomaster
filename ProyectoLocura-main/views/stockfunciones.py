import flet as ft
import sqlite3
import json

CONFIG_FILE = "config.json"

def cargar_configuracion():
    """Carga la configuración de colores desde un archivo JSON."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"color_fondo": "#FFFFFF", "color_tematica": "#E8E8E8", "color_letras": "#000000"}

def conectar_base_datos():
    """Establece conexión con la base de datos y devuelve conexión y cursor."""
    try:
        conn = sqlite3.connect("database/clientes_gimnasio.db")
        return conn, conn.cursor()
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None, None

def actualizar_dato(id_articulo, campo, nuevo_valor, tabla, page):
    from views.stocktabla import cargar_datos_tabla
    """Actualiza un valor específico de un artículo en la base de datos."""
    
    config = cargar_configuracion()
    color_letras = config["color_letras"]

    # Asegurar nombres correctos de columnas antes de la actualización
    columnas_validas = {
        "monto_compra": "monto_de_compra",
        "monto_venta": "monto_de_venta"
    }
    campo = columnas_validas.get(campo, campo)  # Corregir el nombre del campo si es necesario

    conn, cursor = conectar_base_datos()
    if not conn or not cursor:
        return

    try:
        cursor.execute("UPDATE stock SET {} = ? WHERE id = ?".format(campo), (nuevo_valor, id_articulo))
        conn.commit()
        cargar_datos_tabla(tabla, page, color_letras)
    except sqlite3.Error as e:
        print(f"Error al actualizar el artículo: {e}")
    finally:
        conn.close()

def mostrar_dialogo_edicion(id_articulo, tabla, page, color_letras, valores_actuales):
    """Muestra un cuadro de diálogo para confirmar la edición de un artículo."""
    config = cargar_configuracion()

    # Obtener los valores correctos del producto desde la base de datos
    conn, cursor = conectar_base_datos()
    if not conn or not cursor:
        return

    try:
        cursor.execute("SELECT articulo, cantidad, monto_de_compra, monto_de_venta FROM stock WHERE id = ?", (id_articulo,))
        producto = cursor.fetchone()
        conn.close()
        if producto:
            valores_actuales = {
                "articulo": producto[0],
                "cantidad": str(producto[1]),
                "monto_compra": f"{producto[2]:.2f}",
                "monto_venta": f"{producto[3]:.2f}"
            }
        else:
            print(f"Error: No se encontraron datos para el ID {id_articulo}.")
            return
    except sqlite3.Error as e:
        print(f"Error al obtener los datos del producto: {e}")
        return

    # Aplicar estilos a los valores autocompletados con leyendas estáticas
    valores_modificados = {
        "articulo": ft.TextField(
            label="Nombre",
            value=valores_actuales["articulo"],
            text_style=ft.TextStyle(color=config["color_letras"]),
            bgcolor=config["color_tematica"]
        ),
        "cantidad": ft.TextField(
            label="Cantidad",
            value=valores_actuales["cantidad"],
            text_style=ft.TextStyle(color=config["color_letras"]),
            bgcolor=config["color_tematica"]
        ),
        "monto_compra": ft.TextField(
            label="Monto de compra",
            value=valores_actuales["monto_compra"],
            text_style=ft.TextStyle(color=config["color_letras"]),
            bgcolor=config["color_tematica"]
        ),
        "monto_venta": ft.TextField(
            label="Monto de venta",
            value=valores_actuales["monto_venta"],
            text_style=ft.TextStyle(color=config["color_letras"]),
            bgcolor=config["color_tematica"]
        )
    }

    def cerrar_dialogo(e):
        dialogo.open = False
        page.update()

    def cerrar_dialogo_confirmacion(e):
        dialogo_confirmacion.open = False
        page.update()

    def confirmar_guardado(e):
        global dialogo_confirmacion
        dialogo_confirmacion = ft.AlertDialog(
            title=ft.Text("Confirmar guardado", color=config["color_letras"]),
            content=ft.Text("¿Estás seguro de guardar los cambios?", color=config["color_letras"]),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo_confirmacion),
                ft.TextButton("Guardar", on_click=confirmar_edicion, style=ft.ButtonStyle(color="green"))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=config["color_fondo"]
        )
        page.overlay.append(dialogo_confirmacion)
        dialogo_confirmacion.open = True
        page.update()

    def confirmar_edicion(e):
        dialogo_confirmacion.open = False
        page.update()
        for campo, nuevo_valor in valores_modificados.items():
            actualizar_dato(id_articulo, campo, nuevo_valor.value.strip(), tabla, page)  # Se eliminan espacios en blanco innecesarios
        dialogo.open = False
        page.update()

    dialogo = ft.AlertDialog(
        title=ft.Text("Editar artículo", color=config["color_letras"]),
        content=ft.Column([
            ft.Text("Revisa los cambios antes de confirmar.", color=config["color_letras"]),
            *valores_modificados.values()
        ]),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo),
            ft.TextButton("Guardar", on_click=confirmar_guardado, style=ft.ButtonStyle(color=config["color_letras"]))
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=config["color_fondo"]
    )

    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()
def mostrar_dialogo_confirmacion(e, id_articulo, tabla, page, color_letras):
    """Muestra un cuadro de diálogo para confirmar la eliminación de un artículo."""
    config = cargar_configuracion()

    def confirmar_eliminacion(e):
        conn, cursor = conectar_base_datos()
        if not conn or not cursor:
            return

        try:
            cursor.execute("DELETE FROM stock WHERE id = ?", (id_articulo,))
            conn.commit()
            print(f"Artículo con ID {id_articulo} eliminado correctamente.")
            from views.stocktabla import cargar_datos_tabla
            cargar_datos_tabla(tabla, page, config["color_letras"])

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Artículo eliminado correctamente.", color=config["color_letras"]),
                bgcolor=config["color_fondo"]  # <-- Se corrigió color_fondo para usar el valor del JSON
            )
            page.snack_bar.open = True

        except sqlite3.Error as e:
            print(f"Error al eliminar artículo: {e}")
        finally:
            conn.close()

        dialogo.open = False
        page.update()

    def cerrar_dialogo(e):
        dialogo.open = False
        page.update()

    # Definimos el diálogo antes de usarlo en confirmar_eliminacion
    dialogo = ft.AlertDialog(
        title=ft.Text("Confirmar eliminación", color=config["color_letras"]),
        content=ft.Text(f"¿Estás seguro de eliminar el artículo con ID {id_articulo}?", color=config["color_letras"]),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo),
            ft.TextButton("Eliminar", on_click=confirmar_eliminacion, style=ft.ButtonStyle(color="red"))
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=config["color_tematica"]
    )

    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()