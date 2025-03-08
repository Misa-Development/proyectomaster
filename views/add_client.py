import flet as ft
import calendar
import datetime

def open_custom_date_picker_modal(page, initial_date, on_date_selected):
    # Usar hoy si no se proporciona fecha inicial
    if initial_date is None:
        initial_date = datetime.date.today()
    # Usar un diccionario mutable para almacenar el estado (año y mes actuales)
    state = {"year": initial_date.year, "month": initial_date.month}
    
    modal_container = ft.Container(
        content=ft.Text(""),  # se actualizará
        padding=10,
        bgcolor=ft.colors.WHITE,
        border_radius=ft.BorderRadius(10, 10, 10, 10),
        width=350,  # mayor ancho
        height=400,  # mayor alto para incluir controles
    )
    
    # Función que genera la rejilla del calendario para un año y mes
    def build_calendar(year, month):
        month_matrix = calendar.monthcalendar(year, month)
        rows = []
        # Encabezado con nombres de días
        days_header = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        header_row = ft.Row(
            [ft.Text(day, weight="bold", width=40, text_align=ft.TextAlign.CENTER)
             for day in days_header],
            alignment=ft.MainAxisAlignment.CENTER
        )
        rows.append(header_row)
        # Filas por cada semana
        for week in month_matrix:
            btns = []
            for day in week:
                if day == 0:
                    btns.append(ft.Text(" ", width=40))
                else:
                    # Capturamos el valor de day para la lambda
                    d = datetime.date(year, month, day)
                    btn = ft.TextButton(
                        text=str(day),
                        width=40,
                        on_click=lambda e, d=d: on_date_selected(d)
                    )
                    btns.append(btn)
            rows.append(ft.Row(btns, alignment=ft.MainAxisAlignment.CENTER))
        return ft.Column(rows, spacing=2)
    
    # Función para reconstruir el contenido del modal con controles de navegación
    def rebuild_modal():
        # Controles para navegar en el año
        def prev_year(e):
            state["year"] -= 1
            rebuild_modal()
        def next_year(e):
            state["year"] += 1
            rebuild_modal()
        year_row = ft.Row(
            [
                ft.IconButton(icon=ft.icons.ARROW_LEFT, tooltip="Año anterior", on_click=prev_year),
                ft.Text(str(state["year"]), size=18, weight="bold"),
                ft.IconButton(icon=ft.icons.ARROW_RIGHT, tooltip="Año siguiente", on_click=next_year),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        # Controles para navegar en el mes
        def prev_month(e):
            if state["month"] == 1:
                state["month"] = 12
                state["year"] -= 1
            else:
                state["month"] -= 1
            rebuild_modal()
        def next_month(e):
            if state["month"] == 12:
                state["month"] = 1
                state["year"] += 1
            else:
                state["month"] += 1
            rebuild_modal()
        month_row = ft.Row(
            [
                ft.IconButton(icon=ft.icons.ARROW_LEFT, tooltip="Mes anterior", on_click=prev_month),
                ft.Text(calendar.month_name[state["month"]], size=18, weight="bold"),
                ft.IconButton(icon=ft.icons.ARROW_RIGHT, tooltip="Mes siguiente", on_click=next_month),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        # Rejilla del calendario
        calendar_grid = build_calendar(state["year"], state["month"])
        # Botón "Cancelar" para cerrar el modal
        def close_modal(e):
            if overlay in page.overlay:
                page.overlay.remove(overlay)
            page.update()
        cancel_row = ft.Row(
            [ft.TextButton("Cancelar", on_click=close_modal)],
            alignment=ft.MainAxisAlignment.END
        )
        # Actualizar el contenido del contenedor modal
        modal_container.content = ft.Column(
            [
                year_row,
                month_row,
                calendar_grid,
                cancel_row
            ],
            spacing=10
        )
        page.update()
    
    rebuild_modal()
    
    overlay = ft.Container(
         content=modal_container,
         alignment=ft.alignment.center,
         expand=True,
         bgcolor=ft.colors.BLACK38,
    )
    return overlay

def vista_add_client(page):
    page.title = "Agregar Cliente"
    page.window_maximized = True
    page.bgcolor = "#111111"

    # Botón "Volver" para regresar al dashboard
    def regresar_dashboard(e):
        page.clean()
        from views.dashboard import vista_dashboard  # Verifica la ruta
        vista_dashboard(page)
        page.update()
    btn_volver = ft.IconButton(
        icon=ft.icons.ARROW_BACK,
        tooltip="Volver al Dashboard",
        on_click=regresar_dashboard
    )

    # Campos de entrada
    txt_name = ft.TextField(label="Nombre")
    txt_surname = ft.TextField(label="Apellido")
    txt_dni = ft.TextField(label="N° Documento", keyboard_type=ft.KeyboardType.NUMBER)
    txt_age = ft.TextField(label="Edad", keyboard_type=ft.KeyboardType.NUMBER)
    txt_email = ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL)
    dropdown_gender = ft.Dropdown(
        label="Seleccione el Sexo",
        options=[
            ft.dropdown.Option(key="Male", text="Masculino"),
            ft.dropdown.Option(key="Female", text="Femenino"),
            ft.dropdown.Option(key="Other", text="Otro"),
        ],
        value=""
    )
    txt_diseases = ft.TextField(label="Enfermedades")
    switch_medical = ft.Switch(label="Apta Médica", value=False)
    
    # Para la fecha, usamos TextField de solo lectura y un botón para el calendario personalizado
    txt_membership_start = ft.TextField(label="Inicio de Membresía", read_only=True)
    btn_pick_start = ft.IconButton(
        icon=ft.icons.CALENDAR_MONTH,
        tooltip="Seleccionar Fecha",
        on_click=lambda e: show_date_picker(txt_membership_start)
    )
    txt_membership_end = ft.TextField(label="Vencimiento de Membresía", read_only=True)
    btn_pick_end = ft.IconButton(
        icon=ft.icons.CALENDAR_MONTH,
        tooltip="Seleccionar Fecha",
        on_click=lambda e: show_date_picker(txt_membership_end)
    )
    
    def show_date_picker(text_field):
        def on_date_selected(selected_date):
            text_field.value = selected_date.strftime("%d/%m/%Y")
            if overlay in page.overlay:
                page.overlay.remove(overlay)
            page.update()
        overlay = open_custom_date_picker_modal(page, None, on_date_selected)
        page.overlay.append(overlay)
        page.update()
    
    def submit_client(e):
        client_data = {
            "name": txt_name.value,
            "surname": txt_surname.value,
            "dni": txt_dni.value,
            "age": txt_age.value,
            "email": txt_email.value,
            "gender": dropdown_gender.value,
            "diseases": txt_diseases.value,
            "medicalClearance": switch_medical.value,
            "membershipStart": txt_membership_start.value,
            "membershipEnd": txt_membership_end.value
        }
        print("Cliente registrado:", client_data)
        # Limpiar campos
        txt_name.value = ""
        txt_surname.value = ""
        txt_dni.value = ""
        txt_age.value = ""
        txt_email.value = ""
        dropdown_gender.value = ""
        txt_diseases.value = ""
        switch_medical.value = False
        txt_membership_start.value = ""
        txt_membership_end.value = ""
        page.update()
    
    btn_submit = ft.ElevatedButton(
        text="Agregar Cliente",
        on_click=submit_client,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.YELLOW,
            color=ft.colors.BLACK,
            padding=10
        )
    )
    
    membership_start_row = ft.Row([txt_membership_start, btn_pick_start], spacing=5)
    membership_end_row = ft.Row([txt_membership_end, btn_pick_end], spacing=5)
    
    form = ft.Column(
        [
            ft.Text("Agregar Cliente", size=32, weight="bold", color="#e49d1a"),
            txt_name,
            txt_surname,
            ft.Row([txt_dni, txt_age], spacing=10),
            txt_email,
            dropdown_gender,
            txt_diseases,
            switch_medical,
            membership_start_row,
            membership_end_row,
            btn_submit,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )
    
    container = ft.Container(
        content=form,
        alignment=ft.alignment.center,
        padding=20,
        bgcolor="#111111",
        border_radius=ft.BorderRadius(10, 10, 10, 10),
        width=500,
        height=800,
    )
    
    scrollable_layout = ft.ListView(
        expand=True,
        spacing=10,
        controls=[
            ft.Row([btn_volver], alignment=ft.MainAxisAlignment.START),
            container
        ]
    )
    
    page.add(scrollable_layout)
    page.update()

if __name__ == "__main__":
    ft.app(target=vista_add_client)
