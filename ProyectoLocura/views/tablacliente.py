import flet as ft
import sqlite3
import sys
import os

# Agregar el directorio database al path
sys.path.append(os.path.join(os.path.dirname(__file__), '../database'))
from database.db import conectar_db

def vista_tabla_clientes(page, mostrar_detalles_cliente, color_letras, color_tematica):
    try:
        conn = conectar_db()
        conn.row_factory = sqlite3.Row  # Configurar el cursor para devolver diccionarios
        cursor = conn.cursor()

        # Consultar los clientes desde la base de datos
        cursor.execute('''
            SELECT nombre, apellido, sexo, edad, fecha_inicio, fecha_vencimiento, apta_medica,
                   CASE 
                       WHEN fecha_vencimiento >= DATE('now') THEN 'Activo'
                       ELSE 'Inactivo'
                   END AS estado
            FROM clientes
        ''')
        clientes = cursor.fetchall()  # Lista de clientes como diccionarios

    except sqlite3.Error as e:
        print(f"Error al obtener clientes: {e}")
        clientes = []  # Lista vacía si hay un error
    finally:
        if conn:
            conn.close()

    # Crear la tabla en Flet
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Apellido", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Sexo", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Fecha de Inicio", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Fecha de Vencimiento", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Apta Médica", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Activo/Inactivo", weight="bold", color=color_letras)),
            ft.DataColumn(ft.Text("Acción", weight="bold", color=color_letras))
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(cliente["nombre"], color=color_letras)),
                    ft.DataCell(ft.Text(cliente["apellido"], color=color_letras)),
                    ft.DataCell(ft.Text(cliente["sexo"], color=color_letras)),
                    ft.DataCell(ft.Text(cliente["fecha_inicio"], color=color_letras)),
                    ft.DataCell(ft.Text(cliente["fecha_vencimiento"], color=color_letras)),
                    ft.DataCell(ft.Text("Sí" if cliente["apta_medica"] else "No", color=color_letras)),
                    ft.DataCell(ft.Text(cliente["estado"], color=color_letras)),
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.icons.VISIBILITY,
                            tooltip="Ver Detalles",
                            icon_color=color_tematica,
                            on_click=lambda e, c=dict(cliente): mostrar_detalles_cliente(c)  # Convertir Row a diccionario
                        )
                    ),
                ]
            )
            for cliente in clientes  # Itera sobre los clientes obtenidos
        ]
    )

    # Envolver la tabla en un ListView con scroll
    tabla_con_scroll = ft.ListView(
        controls=[tabla],
        expand=True  # Permite que la tabla ocupe todo el espacio disponible con scroll
    )

    return tabla_con_scroll