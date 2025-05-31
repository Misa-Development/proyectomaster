import flet as ft
import sqlite3
import simulador  # Importamos el simulador de huellas

conn = sqlite3.connect("clientes.db", check_same_thread=False)
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    apellido TEXT,
    dni TEXT,
    huella_dactilar TEXT
)
""")
conn.commit()

def capturar_huella():
    """Usa el simulador de huella digital"""
    return simulador.simular_huella()

def main(page: ft.Page):
    page.title = "Registro de Clientes"

    def actualizar_tabla():
        """Actualizar la tabla con los clientes almacenados"""
        conn = sqlite3.connect("clientes.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellido, dni, huella_dactilar FROM cliente")
        clientes = cursor.fetchall()
        conn.close()

        tabla.rows.clear()
        for cliente in clientes:
            tabla.rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(cliente[0]))),  # ID
                    ft.DataCell(ft.Text(cliente[1])),  # Nombre
                    ft.DataCell(ft.Text(cliente[2])),  # Apellido
                    ft.DataCell(ft.Text(cliente[3])),  # DNI
                    ft.DataCell(ft.Text(cliente[4]))  # Huella digital simulada
                ]
            ))
        page.update()

    def agregar_cliente(e):
        """Agregar un cliente con su huella digital simulada"""
        conn = sqlite3.connect("clientes.db", check_same_thread=False)
        cursor = conn.cursor()
        huella = capturar_huella()  # Llama al simulador de huella
        cursor.execute("INSERT INTO cliente (nombre, apellido, dni, huella_dactilar) VALUES (?, ?, ?, ?)", 
                       (nombre_input.value, apellido_input.value, dni_input.value, huella))
        conn.commit()
        conn.close()
        actualizar_tabla()

    # Elementos de entrada
    nombre_input = ft.TextField(label="Nombre")
    apellido_input = ft.TextField(label="Apellido")
    dni_input = ft.TextField(label="DNI")
    btn_agregar = ft.ElevatedButton("Agregar Cliente", on_click=agregar_cliente)

    # Tabla de clientes
    tabla = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("ID")),
        ft.DataColumn(ft.Text("Nombre")),
        ft.DataColumn(ft.Text("Apellido")),
        ft.DataColumn(ft.Text("DNI")),
        ft.DataColumn(ft.Text("Huella Digital"))
    ])

    actualizar_tabla()

    # Vista principal con escaneo de huella y tabla de clientes
    page.add(ft.Column([
        ft.Text("Registro de Clientes", size=20, weight="bold"),
        nombre_input, apellido_input, dni_input, btn_agregar,
        ft.Divider(),
        ft.Text("Lista de Clientes", size=18, weight="bold"),
        tabla
    ]))

ft.app(target=main, view=ft.WEB_BROWSER)  # Evita múltiples pestañas abiertas