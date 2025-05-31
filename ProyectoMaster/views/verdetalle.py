import flet as ft
import sqlite3
from database.db import conectar_db, eliminar_cliente_por_dni

def vista_detalles_cliente(cliente, color_letras, color_tematica, cliente_panel, actualizar_lista_clientes):
    def ocultar_detalles_cliente():
        cliente_panel.width = 0
        cliente_panel.content = ft.Text("No hay detalles disponibles.", color=color_letras)
        cliente_panel.page.update()

    def obtener_dni(cliente):
        """Busca el DNI correcto en la base de datos si no está en el objeto cliente."""
        if "dni" not in cliente or not cliente["dni"] or cliente["dni"] == "No especificado":
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT dni FROM clientes WHERE nombre=? AND apellido=?", (cliente["nombre"], cliente["apellido"]))
            resultado = cursor.fetchone()
            conn.close()
            return resultado[0] if resultado else "No especificado"
        return cliente["dni"]

    def eliminar_cliente_confirmado(cliente, dialog):
        """Cierra el diálogo y elimina el cliente."""
        cerrar_dialogo(dialog)
        eliminar_cliente(cliente)

    def confirmar_eliminacion(cliente):
        """Muestra un cuadro de confirmación antes de eliminar un cliente."""
        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING, color="red"),
                ft.Text("Confirmación de Eliminación", weight="bold", color=color_letras)
            ]),
            content=ft.Text(f"⚠️ ¿Estás seguro de que deseas eliminar a {cliente['nombre']} {cliente['apellido']}?", color=color_letras),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(dialog)),
                ft.TextButton("Eliminar", on_click=lambda e: eliminar_cliente_confirmado(cliente, dialog))
            ]
        )
        cliente_panel.page.overlay.append(dialog)
        dialog.open = True
        cliente_panel.page.update()

    def cerrar_dialogo(dialog):
        """Cierra el cuadro de diálogo."""
        dialog.open = False
        cliente_panel.page.update()

    def eliminar_cliente(cliente):
        dni_cliente = obtener_dni(cliente)
        if eliminar_cliente_por_dni(dni_cliente):
            ocultar_detalles_cliente()
            actualizar_lista_clientes()

    def editar_cliente(cliente):
        cliente_panel.width = 350
        cliente_panel.margin = 30

        dni_actualizado = obtener_dni(cliente)

        edit_dni = ft.TextField(label="DNI", value=dni_actualizado, text_size=16, color=color_letras)
        fields = [ft.TextField(label=label, value=str(cliente.get(field, "No especificado")), text_size=16, color=color_letras)
                for label, field in [("Nombre", "nombre"), ("Apellido", "apellido"), ("Sexo", "sexo"),
                                    ("Edad", "edad"), ("Fecha de Inicio", "fecha_inicio"),
                                    ("Fecha de Vencimiento", "fecha_vencimiento"), ("Enfermedades", "enfermedades")]]

        switch_medical = ft.Switch(
            label="Apta Médica",
            value=bool(cliente.get("apta_medica", False)),
            active_color=color_letras,
            label_style=ft.TextStyle(color=color_letras)  # Esto da color a la etiqueta
        )
        def guardar_cambios(e):
            nuevo_dni = edit_dni.value.strip() or dni_actualizado
            nuevo_nombre = fields[0].value
            nuevo_apellido = fields[1].value
            nuevo_sexo = fields[2].value
            nuevo_edad = fields[3].value
            nuevo_fecha_inicio = fields[4].value
            nuevo_fecha_vencimiento = fields[5].value
            nuevas_enfermedades = fields[6].value
            nuevo_apta_medica = 1 if switch_medical.value else 0

            conn = conectar_db()
            cursor = conn.cursor()
            query = """UPDATE clientes SET nombre=?, apellido=?, sexo=?, edad=?, fecha_inicio=?, fecha_vencimiento=?,
                    apta_medica=?, enfermedades=?, dni=? WHERE dni=?"""
            cursor.execute(query, (nuevo_nombre, nuevo_apellido, nuevo_sexo, nuevo_edad,
                                nuevo_fecha_inicio, nuevo_fecha_vencimiento, nuevo_apta_medica,
                                nuevas_enfermedades, nuevo_dni, dni_actualizado))

            if cursor.rowcount == 0:
                print(f"⚠️ No se actualizó ningún cliente. Verifica que el DNI {dni_actualizado} es correcto.")
            else:
                conn.commit()
                print("✅ Cliente actualizado correctamente.")

            cursor.execute("SELECT * FROM clientes WHERE dni=?", (nuevo_dni,))
            cliente_actualizado = cursor.fetchone()
            conn.close()

            if cliente_actualizado:
                cliente.update({"nombre": nuevo_nombre, "apellido": nuevo_apellido, "sexo": nuevo_sexo,
                                "edad": nuevo_edad, "fecha_inicio": nuevo_fecha_inicio, "fecha_vencimiento": nuevo_fecha_vencimiento,
                                "apta_medica": nuevo_apta_medica, "enfermedades": nuevas_enfermedades, "dni": nuevo_dni})
                actualizar_lista_clientes()
                cliente_panel.content = vista_estatica(cliente)
                cliente_panel.page.update()

        cliente_panel.content = ft.Container(
            content=ft.Column([
                ft.IconButton(icon=ft.Icons.CLOSE, tooltip="Cerrar", icon_color=color_letras, on_click=lambda e: ocultar_detalles_cliente()),
                ft.Text(f"Editar Cliente: {cliente['nombre']} {cliente['apellido']}", size=24, weight="bold", color=color_letras),
                edit_dni, *fields, switch_medical,
                ft.Row([
                    ft.ElevatedButton(text="Guardar Cambios", on_click=guardar_cambios,
                                    style=ft.ButtonStyle(bgcolor=color_tematica, color=color_letras)),
                    ft.ElevatedButton(text="Cancelar", on_click=lambda e: ocultar_detalles_cliente(),
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED, color="white"))
                ], alignment=ft.MainAxisAlignment.END, spacing=10)
            ], spacing=20, scroll="adaptive"),  # Aquí agregamos scroll
            expand=True
        )

        cliente_panel.page.update()

    def vista_estatica(cliente):
        dni_actualizado = obtener_dni(cliente)
        apta_medica_estado = "Sí" if cliente.get("apta_medica", False) == 1 else "No"

        return ft.Column([
            ft.IconButton(icon=ft.Icons.CLOSE, tooltip="Cerrar", icon_color=color_letras, on_click=lambda e: ocultar_detalles_cliente()),
            *[ft.Text(f"{label}: {cliente.get(field, 'No especificado')}", size=16, color=color_letras)
              for label, field in [("Nombre", "nombre"), ("Apellido", "apellido"), ("Sexo", "sexo"),
                                   ("Edad", "edad"), ("Fecha de Inicio", "fecha_inicio"),
                                   ("Fecha de Vencimiento", "fecha_vencimiento"), ("Enfermedades", "enfermedades")]],
            ft.Text(f"DNI: {dni_actualizado}", size=16, color=color_letras),
            ft.Text(f"Apta Médica: {apta_medica_estado}", size=16, color=color_letras),
            ft.Container(expand=True, height=200),
            ft.Row([
                ft.ElevatedButton(text="✏️ Editar Cliente", on_click=lambda e: editar_cliente(cliente),
                                  style=ft.ButtonStyle(bgcolor=color_tematica, color=color_letras)),
                ft.ElevatedButton(text="🗑️ Eliminar Cliente", on_click=lambda e: confirmar_eliminacion(cliente),
                                  style=ft.ButtonStyle(bgcolor=ft.Colors.RED, color="white"))
            ], alignment=ft.MainAxisAlignment.END, spacing=10)
        ], expand=True, spacing=20)

    return vista_estatica(cliente)