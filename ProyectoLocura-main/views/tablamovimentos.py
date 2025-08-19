import flet as ft
from database.db import obtener_historial_movimientos, conectar_db

class HistorialMovimientosTable:
    def __init__(self, page: ft.Page, color_letras, color_tematica, color_fondo, scale=1.5, rol=None, mostrar_detalles_cliente=None):
        self.page = page
        self.color_letras = color_letras
        self.color_tematica = color_tematica
        self.color_fondo = color_fondo
        self.scale = scale
        self.rol = rol  # Nuevo: guardar el rol
        self.mostrar_detalles_cliente = mostrar_detalles_cliente
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tipo", color=self.color_letras, size=int(18*self.scale))),
                ft.DataColumn(ft.Text("Nombre", color=self.color_letras, size=int(18*self.scale))),
                ft.DataColumn(ft.Text("Apellido", color=self.color_letras, size=int(18*self.scale))),
                ft.DataColumn(ft.Text("DNI", color=self.color_letras, size=int(18*self.scale))),
                ft.DataColumn(ft.Text("Fecha y Hora", color=self.color_letras, size=int(18*self.scale))),
                ft.DataColumn(ft.Text("Notas", color=self.color_letras, size=int(18*self.scale))),
            ],
            rows=[],
        )

    def update_data(self):
        """Actualiza los datos de la tabla."""
        movimientos = obtener_historial_movimientos()
        # Ordenar por fecha/hora descendente (asumiendo que 'fecha' es YYYY-MM-DD HH:MM:SS)
        movimientos = sorted(movimientos, key=lambda m: m["fecha"], reverse=True)
        self.tabla.rows.clear()
        for mov in movimientos:
            def on_click(e, mov=mov):
                self.open_notes_dialog(e, mov)
            def on_nombre_click(e, mov=mov):
                if self.mostrar_detalles_cliente:
                    self.mostrar_detalles_cliente(mov)
            self.tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(mov["tipo"], color=self.color_letras, size=int(17*self.scale))),
                    ft.DataCell(ft.GestureDetector(
                        content=ft.Text(mov["nombre"], color=self.color_letras, size=int(17*self.scale)),
                        on_tap=on_nombre_click)),
                    ft.DataCell(ft.GestureDetector(
                        content=ft.Text(mov["apellido"], color=self.color_letras, size=int(17*self.scale)),
                        on_tap=on_nombre_click)),
                    ft.DataCell(ft.GestureDetector(
                        content=ft.Text(mov["dni"], color=self.color_letras, size=int(17*self.scale)),
                        on_tap=on_nombre_click)),
                    ft.DataCell(ft.Text(mov["fecha"], color=self.color_letras, size=int(17*self.scale))),
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.Icons.NOTE,
                            tooltip="Agregar/Editar Notas",
                            on_click=on_click,
                            icon_color=self.color_tematica,
                            icon_size=int(28*self.scale),
                        )
                    ),
                ])
            )
        self.page.update()

    def filtrar_movimientos(self, tipo, fecha):
        """Filtra los movimientos según el tipo y la fecha."""
        movimientos_filtrados = [
            mov for mov in obtener_historial_movimientos() if
            (tipo == "Todos" or mov["tipo"] == tipo) and
            (not fecha or fecha in mov["fecha"]) if fecha is not None
        ]
        # Ordenar por fecha/hora descendente
        movimientos_filtrados = sorted(movimientos_filtrados, key=lambda m: m["fecha"], reverse=True)
        self.tabla.rows.clear()
        for mov in movimientos_filtrados:
            def on_click(e, mov=mov):
                self.open_notes_dialog(e, mov)
            def on_nombre_click(e, mov=mov):
                if self.mostrar_detalles_cliente:
                    self.mostrar_detalles_cliente(mov)
            self.tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(mov["tipo"], color=self.color_letras, size=int(17*self.scale))),
                    ft.DataCell(ft.GestureDetector(
                        content=ft.Text(mov["nombre"], color=self.color_letras, size=int(17*self.scale)),
                        on_tap=on_nombre_click)),
                    ft.DataCell(ft.GestureDetector(
                        content=ft.Text(mov["apellido"], color=self.color_letras, size=int(17*self.scale)),
                        on_tap=on_nombre_click)),
                    ft.DataCell(ft.GestureDetector(
                        content=ft.Text(mov["dni"], color=self.color_letras, size=int(17*self.scale)),
                        on_tap=on_nombre_click)),
                    ft.DataCell(ft.Text(mov["fecha"], color=self.color_letras, size=int(17*self.scale))),
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.Icons.NOTE,
                            tooltip="Agregar/Editar Notas",
                            on_click=on_click,
                            icon_color=self.color_tematica,
                            icon_size=int(28*self.scale),
                        )
                    ),
                ])
            )
        self.page.update()

    def open_notes_dialog(self, e, mov):
        """Abre el diálogo para ver o editar las notas."""
        notes_text_ref = ft.Ref[ft.TextField]()
        initial_notes = mov.get("notas", "") if mov.get("notas", "") else ""
        notes_width = 350
        if mov["tipo"] == "Modificación":
            notes_width = 700
        notes_text = ft.TextField(
            label="Notas",
            value=initial_notes,
            multiline=True,
            color=self.color_letras,
            border_color=self.color_letras,
            ref=notes_text_ref,
            text_style=ft.TextStyle(size=int(17*self.scale)),
            read_only=(mov["tipo"] != "Alta"),
            width=notes_width
        )
        dialog_content = notes_text
        if mov["tipo"] == "Modificación":
            dialog_content = ft.Container(notes_text, width=notes_width, padding=10)

        def close_dialog(e):
            dialog.open = False
            self.page.update()
            self.page.dialog = None

        def save_notes(e):
            new_notes = notes_text_ref.current.value
            conn = None
            try:
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE historial_movimientos SET notas = ? WHERE id = ?", (new_notes, mov["id"]))
                conn.commit()
                close_dialog(e)
                self.update_data()
                self.page.update()
            except Exception as ex:
                print(ex)
            finally:
                if conn:
                    conn.close()
                self.page.update()

        dialog_actions = [
            ft.TextButton(
                "Cerrar" if mov["tipo"] != "Alta" else "Cancelar",
                on_click=close_dialog,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=int(17*self.scale), color=self.color_letras),
                    bgcolor=self.color_fondo
                )
            )
        ]
        if mov["tipo"] == "Alta":
            dialog_actions.append(
                ft.TextButton(
                    "Guardar",
                    on_click=save_notes,
                    style=ft.ButtonStyle(
                        text_style=ft.TextStyle(size=int(17*self.scale), color=self.color_letras),
                        bgcolor=self.color_tematica
                    )
                )
            )
        # Título dinámico según tipo
        if mov["tipo"] == "Baja":
            dialog_title = "Motivo de Baja"
        elif mov["tipo"] == "Modificación":
            dialog_title = "Se editaron los siguientes campos"
        elif mov["tipo"] == "Renovación":
            dialog_title = "Renovación de Membresía"
        else:
            dialog_title = "Notas"

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(dialog_title, color=self.color_letras, size=int(20*self.scale)),
            content=dialog_content,
            actions=dialog_actions,
            bgcolor=self.color_fondo
        )
        self.open_dlg(dialog)

    def open_dlg(self, dlg):
        print("Abriendo diálogo de notas... (add)")  # Depuración
        self.page.add(dlg)
        dlg.open = True
        self.page.update()

    def get_widget(self):
        """Devuelve la tabla envuelta en un contenedor con scroll vertical."""
        return ft.Container(
            content=ft.Column([self.tabla], scroll="auto"),
            height=500,  # Ajusta el alto según tu preferencia
            bgcolor=self.color_fondo,
            border_radius=8,
            padding=10,
        )
