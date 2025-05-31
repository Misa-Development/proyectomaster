import flet as ft
import sqlite3
from database.db import conectar_db

def cargar_datos_tabla(tabla, page, color_letras):
    try:
        conn = sqlite3.connect("database/clientes_gimnasio.db")
        cursor = conn.cursor()

        # Verifica que la tabla 'stock' exista
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock'")
        if not cursor.fetchone():
            print("La tabla 'stock' no existe. No se pueden cargar datos.")
            return

        # Carga los datos de la tabla 'stock'
        cursor.execute("SELECT * FROM stock")
        rows = cursor.fetchall()

        tabla.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row[0]), color=color_letras)),  # id
                ft.DataCell(ft.Text(row[1], color=color_letras)),      # articulo
                ft.DataCell(ft.Text(str(row[2]), color=color_letras)), # cantidad
                ft.DataCell(ft.Text(f"${row[3]:.2f}", color=color_letras)), # monto de compra
                ft.DataCell(ft.Text(f"${row[4]:.2f}", color=color_letras)), # monto de venta
                ft.DataCell(ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED,
                    tooltip="Eliminar artículo",
                    on_click=lambda e, id=row[0]: mostrar_dialogo_confirmacion(e, id, tabla, page, color_letras)
                ))  # acción
            ])
            for row in rows
        ]

    except sqlite3.Error as e:
        print(f"Error al cargar datos de la tabla stock: {e}")
    finally:
        if conn:
            conn.close()

    page.update()

def mostrar_dialogo_confirmacion(e, id_articulo, tabla, page, color_letras):
    def confirmar_eliminacion(e):
        try:
            conn = sqlite3.connect("database/clientes_gimnasio.db")  # Ruta corregida
            cursor = conn.cursor()

            cursor.execute("DELETE FROM stock WHERE id = ?", (id_articulo,))
            conn.commit()

            print(f"Artículo con ID {id_articulo} eliminado correctamente.")
            cargar_datos_tabla(tabla, page, color_letras)  # Actualiza la tabla

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Artículo eliminado correctamente.", color=color_letras),
                bgcolor="lightgreen"
            )
            page.snack_bar.open = True

        except sqlite3.Error as e:
            print(f"Error al eliminar artículo: {e}")
        finally:
            if conn:
                conn.close()

        dialogo.open = False
        page.update()

    def cerrar_dialogo(e):
        dialogo.open = False
        page.update()

    dialogo = ft.AlertDialog(
        title=ft.Text("Confirmar eliminación", color=color_letras),
        content=ft.Text(f"¿Estás seguro de eliminar el artículo con ID {id_articulo}?", color=color_letras),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo),
            ft.TextButton("Eliminar", on_click=confirmar_eliminacion, style=ft.ButtonStyle(color=ft.Colors.RED))
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor="lightyellow"
    )

    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()


def construir_tabla(color_letras):
    return ft.DataTable(
        columns=[
            ft.DataColumn(label=ft.Text("ID", color=color_letras)),
            ft.DataColumn(label=ft.Text("Artículo", color=color_letras)),
            ft.DataColumn(label=ft.Text("Cantidad", color=color_letras)),
            ft.DataColumn(label=ft.Text("Monto de Compra", color=color_letras)),
            ft.DataColumn(label=ft.Text("Monto de Venta", color=color_letras)),
            ft.DataColumn(label=ft.Text("Acciones", color=color_letras)),
        ],
        rows=[]
    )
