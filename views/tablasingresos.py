import flet as ft
from database.db import conectar_db, obtener_ingresos, obtener_historial_pagos
# Vista de tabla clientes
def vista_tabla_clientes(page, color_letras, color_tematica):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('''SELECT nombre, apellido, sexo, edad, fecha_inicio, fecha_vencimiento, apta_medica FROM clientes''')
        clientes = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        clientes = []
    finally:
        if conn:
            conn.close()

    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Apellido", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Sexo", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Fecha de Inicio", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Fecha de Vencimiento", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Apta Médica", weight="bold", color=color_letras)),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(cliente[0], color=color_letras)),
                    ft.DataCell(ft.Text(cliente[1], color=color_letras)),
                    ft.DataCell(ft.Text(cliente[2], color=color_letras)),
                    ft.DataCell(ft.Text(cliente[3], color=color_letras)),
                    ft.DataCell(ft.Text(cliente[4], color=color_letras)),
                    ft.DataCell(ft.Text("Sí" if cliente[5] else "No", color=color_letras)),
                ]
            )
            for cliente in clientes
        ]
    )

# Vista de tabla historial de pagos
def vista_tabla_historial_pagos(page, color_letras, color_tematica):
    pagos = obtener_historial_pagos()
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Cliente", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Monto", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Fecha de Pago", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Método de Pago", weight="bold", color=color_letras)),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(pago["cliente"], color=color_letras)),
                    ft.DataCell(ft.Text(f"${pago['monto']:.2f}", color=color_letras)),
                    ft.DataCell(ft.Text(pago["fecha_pago"], color=color_letras)),
                    ft.DataCell(ft.Text(pago["metodo_pago"], color=color_letras)),
                ]
            )
            for pago in pagos
        ]
    )

# Vista de tabla ingresos
def vista_tabla_ingresos(page, color_letras, color_tematica):
    ingresos = obtener_ingresos()
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Artículo", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Monto", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Fecha", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Cliente", weight="bold", color=color_letras)),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(ingreso["articulo"], color=color_letras)),
                    ft.DataCell(ft.Text(f"${ingreso['monto']:.2f}", color=color_letras)),
                    ft.DataCell(ft.Text(ingreso["fecha"], color=color_letras)),
                    ft.DataCell(ft.Text(ingreso["cliente"], color=color_letras)),
                ]
            )
            for ingreso in ingresos
        ]
    )

def main(page: ft.Page):
    page.title = "Gestión de Gimnasio"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "auto"
    color_letras = "black"
    color_tematica = "blue"

    # Componentes de la interfaz
    page.add(
        ft.Text("Tablas de Gestión", size=24, weight="bold", color=color_tematica),
        ft.Divider(),
        ft.Text("Clientes", size=18, weight="bold", color=color_tematica),
        vista_tabla_clientes(page, color_letras, color_tematica),
        ft.Divider(),
        ft.Text("Historial de Pagos", size=18, weight="bold", color=color_tematica),
        vista_tabla_historial_pagos(page, color_letras, color_tematica),
        ft.Divider(),
        ft.Text("Ingresos", size=18, weight="bold", color=color_tematica),
        vista_tabla_ingresos(page, color_letras, color_tematica),
    )

if __name__ == "__main__":
    ft.app(target=main)