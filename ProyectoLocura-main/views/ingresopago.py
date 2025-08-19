import flet as ft
import sqlite3
from database.db import insertar_ingreso
from views.custom_date_picker import open_custom_date_picker_modal

def obtener_productos_stock():
    conn = sqlite3.connect("database/clientes_gimnasio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT articulo, monto_de_venta FROM stock")
    productos = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return productos
def descontar_stock(articulo, cantidad):
    conn = sqlite3.connect("database/clientes_gimnasio.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE stock SET cantidad = cantidad - ? WHERE articulo = ?", (cantidad, articulo))
    conn.commit()
    conn.close()

def vista_ingreso_pago(page, tabla, color_letras, color_fondo, color_tematica, cerrar_panel):
    productos_stock = obtener_productos_stock()

    input_articulo = ft.Dropdown(
        label="Artículo",
        options=[ft.dropdown.Option(producto) for producto in productos_stock.keys()],
        text_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
        border_color=color_fondo,
        width=300
    )

    input_fecha = ft.TextField(
        label="Fecha (DD/MM/AAAA)",
        read_only=True,
        text_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
        border_color=color_fondo,
        width=200
    )
    input_monto = ft.TextField(
        label="Monto",
        read_only=True,
        text_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
        border_color=color_fondo,
        width=200
    )
    input_cliente = ft.TextField(
        label="Cliente",
        text_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
        border_color=color_fondo,
        width=300
    )
    input_cantidad = ft.TextField(
        label="Cantidad",
        text_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
        border_color=color_fondo,
        width=200
    )

    input_metodo_pago = ft.Dropdown(
        label="Método de Pago",
        options=[ft.dropdown.Option("Efectivo"), ft.dropdown.Option("Transferencia"), ft.dropdown.Option("Tarjeta")],
        text_style=ft.TextStyle(color=color_letras),
        label_style=ft.TextStyle(color=color_letras),
        border_color=color_fondo,
        width=250
    )

    def show_date_picker(e):
        def on_date_selected(date):
            input_fecha.value = date.strftime("%d/%m/%Y")
            for overlay in page.overlay[:]:
                if isinstance(overlay, ft.Container) and getattr(overlay, "width", None) == 350:
                    page.overlay.remove(overlay)
            page.update()
        page.overlay.append(open_custom_date_picker_modal(page, None, on_date_selected))
        page.update()

    boton_fecha = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=show_date_picker,
        style=ft.ButtonStyle(bgcolor=color_fondo, color="black"),
        tooltip="Seleccionar fecha"
    )

    def actualizar_monto(e):
        articulo_seleccionado = input_articulo.value
        if articulo_seleccionado in productos_stock:
            input_monto.value = f"${productos_stock[articulo_seleccionado]:.2f}"
        else:
            input_monto.value = ""
        page.update()

    input_articulo.on_change = actualizar_monto
    def descontar_stock(articulo, cantidad):
        conn = sqlite3.connect("database/clientes_gimnasio.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE stock SET cantidad = cantidad - ? WHERE articulo = ?", (cantidad, articulo))
        conn.commit()
        conn.close()
        
    def agregar_ingreso(e):
        articulo = input_articulo.value
        monto = input_monto.value.replace("$", "")
        cliente = input_cliente.value
        fecha = input_fecha.value
        metodo_pago = input_metodo_pago.value
        cantidad = input_cantidad.value

        if not all([articulo, monto, cliente, fecha, metodo_pago, cantidad]):
            page.snack_bar = ft.SnackBar(content=ft.Text("Completa todos los campos antes de agregar el ingreso."), open=True)
            return

        try:
            insertar_ingreso(articulo, float(monto), fecha, cliente, metodo_pago, int(cantidad))
            descontar_stock(articulo, float(cantidad))  # <-- Descuenta del stock

            for campo in [input_articulo, input_fecha, input_monto, input_cliente, input_metodo_pago, input_cantidad]:
                campo.value = ""

            page.snack_bar = ft.SnackBar(content=ft.Text("Ingreso agregado exitosamente."), open=True)
            tabla.rows.insert(0, ft.DataRow(cells=[
                ft.DataCell(ft.Text(cliente, color=color_letras)),
                ft.DataCell(ft.Text(articulo, color=color_letras)),
                ft.DataCell(ft.Text(f"${float(monto):.2f}", color=color_letras)),
                ft.DataCell(ft.Text(str(cantidad), color=color_letras)),
                ft.DataCell(ft.Text(fecha, color=color_letras)),
                ft.DataCell(ft.Text(metodo_pago, color=color_letras)),
            ]))
            page.update()
            cerrar_panel(None)
        except ValueError:
            page.snack_bar = ft.SnackBar(content=ft.Text("El monto y la cantidad deben ser válidos."), open=True)
    boton_agregar_ingreso = ft.ElevatedButton(
        text="Agregar ingreso",
        on_click=agregar_ingreso,
        bgcolor=color_fondo,
        color="black"
    )

    boton_cerrar = ft.IconButton(
        icon=ft.Icons.CLOSE,
        tooltip="Cerrar",
        on_click=cerrar_panel,
        style=ft.ButtonStyle(bgcolor=color_fondo, color="black")
    )

    return ft.Column(
        controls=[
            ft.Row([ft.Text("Ingresar", size=20, weight="bold", color=color_letras), boton_cerrar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            input_cliente,
            input_articulo,
            input_monto,
            input_cantidad,
            ft.Row([input_fecha, boton_fecha], spacing=8),
            input_metodo_pago,
            boton_agregar_ingreso
        ],
        spacing=15, alignment=ft.MainAxisAlignment.START
    )

def panel_ingreso_pago(page, tabla, color_letras, color_tematica, color_fondo, panel_visible, set_panel_visible):
    """Panel lateral derecho personalizado para el formulario de ingreso."""
    def cerrar_panel(e):
        set_panel_visible(False)
        page.update()

    return ft.Container(
        visible=True,
        right=0,
        top=0,
        width=420,
        height=page.height,
        bgcolor=color_tematica,  # Fondo del panel lateral
        border_radius=ft.border_radius.only(top_left=20, bottom_left=20),
        shadow=ft.BoxShadow(blur_radius=16, color="#88888844"),
        padding=20,
        alignment=ft.alignment.top_right,
        offset=ft.Offset(0, 0) if panel_visible else ft.Offset(1, 0),
        animate_offset=ft.Animation(400, "decelerate"),
        content=vista_ingreso_pago(page, tabla, color_letras, color_fondo, color_tematica, cerrar_panel),
    )