import flet as ft
import json
from database.db import obtener_ingresos  # Importar los ingresos desde la base de datos

def actualizar_tabla_ingresos(tabla_ingresos, valor_filtro, color_letras, page):
    """
    Filtra los ingresos de la tabla según el valor del filtro proporcionado.
    """
    # Actualiza las filas de la tabla basándose en el filtro aplicado
    tabla_ingresos.rows = [
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(ingreso["articulo"], color=color_letras)),
                ft.DataCell(ft.Text(f"${ingreso['monto']:.2f}", color=color_letras)),
                ft.DataCell(ft.Text(ingreso["fecha"], color=color_letras)),
                ft.DataCell(ft.Text(ingreso["cliente"], color=color_letras)),
                ft.DataCell(ft.Text(ingreso["metodo_pago"], color=color_letras)),  # Celda añadida
            ]
        )
        for ingreso in obtener_ingresos()
        if valor_filtro.lower() in ingreso["cliente"].lower()  # Filtrar por cliente
    ]
    page.update()

def filtros_ingresos(page, tabla_ingresos, color_letras):
    """
    Genera los filtros para buscar ingresos en la tabla, con color personalizado.
    """
    return ft.TextField(
        label="Buscar ingresos por cliente",
        hint_text="Escribe el nombre del cliente...",
        prefix_icon=ft.Icons.SEARCH,
        text_style=ft.TextStyle(color=color_letras),
        border_color=color_letras,
        label_style=ft.TextStyle(color=color_letras),
        on_change=lambda e: actualizar_tabla_ingresos(tabla_ingresos, e.control.value, color_letras, page),  # Pasa color_letras
    )