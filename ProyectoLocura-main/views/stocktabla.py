import flet as ft
import sqlite3
from views.stockfunciones import mostrar_dialogo_edicion, mostrar_dialogo_confirmacion

def conectar_base_datos():
    """Establece conexión con la base de datos y devuelve el objeto conexión y cursor."""
    try:
        conn = sqlite3.connect("database/clientes_gimnasio.db")
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None, None

def cargar_datos_tabla(tabla, page, color_letras, filtro=""):
    """Carga los datos de la tabla 'stock' en el DataTable de Flet con opción de búsqueda."""
    conn, cursor = conectar_base_datos()
    if not conn or not cursor:
        return

    try:
        consulta = "SELECT * FROM stock"
        if filtro:
            consulta += " WHERE articulo LIKE ?"
            cursor.execute(consulta, (f"%{filtro}%",))
        else:
            cursor.execute(consulta)

        rows = cursor.fetchall()
        tabla.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(row[0]), color=color_letras)),  # ID
                ft.DataCell(ft.Text(row[1], color=color_letras)),  # Artículo
                ft.DataCell(ft.Text(str(row[2]), color=color_letras)),  # Cantidad
                ft.DataCell(ft.Text(f"${row[3]:.2f}", color=color_letras)),  # Monto compra
                ft.DataCell(ft.Text(f"${row[4]:.2f}", color=color_letras)),  # Monto venta
                ft.DataCell(ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        icon_color=ft.Colors.BLUE,
                        tooltip="Editar artículo",
                        on_click=lambda e, id=row[0]: mostrar_dialogo_edicion(
                            id, tabla, page, color_letras, {
                                "articulo": ft.TextField(value=row[1]),
                                "cantidad": ft.TextField(value=str(row[2])),
                                "monto_compra": ft.TextField(value=f"{row[3]:.2f}"),
                                "monto_venta": ft.TextField(value=f"{row[4]:.2f}")
                            }
                        )
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Eliminar artículo",
                        on_click=lambda e, id=row[0]: mostrar_dialogo_confirmacion(e, id, tabla, page, color_letras)
                    )
                ]))
            ])
            for row in rows
        ]

    except sqlite3.Error as e:
        print(f"Error al cargar datos de la tabla stock: {e}")
    finally:
        conn.close()

    page.update()

def construir_tabla(color_letras):
    """Construye y devuelve un DataTable para mostrar los datos de la tabla 'stock'."""
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