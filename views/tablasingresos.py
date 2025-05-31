import flet as ft
import json
from database.db import obtener_ingresos  # Importar los ingresos desde la base de datos

# Ruta del archivo de configuración
CONFIG_FILE = "config.json"

def cargar_configuracion():
    """
    Cargar configuración desde un archivo JSON. Retorna un diccionario con valores por defecto si no se encuentra el archivo.
    """
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "color_fondo": "#FFFFFF",  # Blanco por defecto
            "color_letras": "#000000",  # Negro por defecto
        }

def inicializar_tabla_ingresos(color_letras):
    """
    Carga todos los datos existentes de la base de datos en la tabla al inicializar.
    """
    rows = [
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
    ]
    return rows

def tabla_ingresos():
    """
    Genera la tabla de ingresos con sus columnas y filas iniciales.
    """
    # Cargar configuración desde el archivo JSON
    config = cargar_configuracion()
    color_letras = config["color_letras"]

    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Artículo", color=color_letras)),
            ft.DataColumn(ft.Text("Monto", color=color_letras)),
            ft.DataColumn(ft.Text("Fecha", color=color_letras)),
            ft.DataColumn(ft.Text("Cliente", color=color_letras)),
            ft.DataColumn(ft.Text("Método de Pago", color=color_letras)),
        ],
        rows=inicializar_tabla_ingresos(color_letras),  # Cargar las filas iniciales con el color correcto
    )