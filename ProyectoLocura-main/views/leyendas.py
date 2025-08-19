import flet as ft
import threading
import time
from views.logicaleyendas import obtener_clientes_activos, obtener_proximas_renovaciones, \
    obtener_clientes_vencidos, obtener_fecha_hora_actual

# ---------------------------------------------------------------------------
# Vista de leyendas (dashboard de indicadores).
def vista_leyendas(color_letras, color_fondo, color_tematica, page: ft.Page, scale=1.0):
    # Se obtienen los valores iniciales.
    fechaoficial, horaoficial = obtener_fecha_hora_actual()
    clientes_activos = obtener_clientes_activos()
    proximas_renovaciones = obtener_proximas_renovaciones()
    clientes_vencidos = obtener_clientes_vencidos()

    # Controles de texto para cada tarjeta.
    time_text = ft.Text(f"{fechaoficial} | {horaoficial}", size=int(25 * scale), weight="bold", color="#000000")
    active_clients_text = ft.Text(str(clientes_activos), size=int(38 * scale), weight="bold", color="#000000")
    renovaciones_text = ft.Text(str(proximas_renovaciones), size=int(42 * scale), weight="bold", color="#000000")
    vencidos_text = ft.Text(str(clientes_vencidos), size=int(44 * scale), weight="bold", color="#000000")

    # Tarjeta: Clientes Activos.
    card_activos = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Clientes Activos", size=int(16 * scale), weight="bold", color=color_fondo),
                    ft.Row(
                        controls=[
                            ft.Image(src="assets/chest_body_building_gym_fitness_icon_224827.png", width=int(110 * scale), height=int(70 * scale)),
                            active_clients_text,
                        ],
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            gradient=ft.LinearGradient(
                colors=["#D3D3D3", "#9E9E9E", "#545454"],
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right
            ),
            padding=int(15 * scale),
            border_radius=int(8 * scale),
            width=int(250 * scale),
            height=int(140 * scale),
            border=ft.border.all(color=color_fondo, width=1.5 * scale),
        ),
        elevation=14,
        shadow_color=color_tematica,
        margin=ft.margin.all(8 * scale),
    )

    # Tarjeta: Fecha y Hora Actual.
    card_fecha = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Fecha y Hora", size=int(16 * scale), weight="bold", color=color_fondo),
                    ft.Row(
                        controls=[
                            time_text,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Image(src="assets/OIPr.png", width=int(40 * scale), height=int(20 * scale)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=int(5 * scale)
            ),
            gradient=ft.LinearGradient(
                colors=["#D3D3D3", "#9E9E9E", "#545454"],
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right
            ),
            padding=int(15 * scale),
            border_radius=int(8 * scale),
            width=int(350 * scale),
            height=int(140 * scale),
            border=ft.border.all(color=color_fondo, width=1.5 * scale),
        ),
        elevation=14,
        shadow_color=color_tematica,
        margin=ft.margin.all(8 * scale),
    )

    # Tarjeta: Próximas Renovaciones.
    card_renovaciones = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Próximas Renovaciones", size=int(16 * scale), weight="bold", color=color_fondo),
                    ft.Row(
                        controls=[
                            renovaciones_text,
                            ft.Image(src="assets/corazon.png", width=int(60 * scale), height=int(50 * scale)),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=int(10 * scale)
                    ),
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=int(16 * scale), color=color_fondo),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=int(5 * scale)
            ),
            gradient=ft.LinearGradient(
                colors=["#D3D3D3", "#9E9E9E", "#545454"],
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right
            ),
            padding=int(15 * scale),
            border_radius=int(8 * scale),
            width=int(250 * scale),
            height=int(140 * scale),
            border=ft.border.all(color=color_fondo, width=1.5 * scale),
        ),
        elevation=14,
        shadow_color=color_tematica,
        margin=ft.margin.all(8 * scale),
    )

    # Tarjeta: Clientes Vencidos.
    card_vencidos = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Vencidos Recientes", size=int(17 * scale), weight="bold", color=color_fondo),
                    ft.Row(
                        controls=[
                            ft.Image(src="assets/debilidad.png", width=int(70 * scale), height=int(50 * scale)),
                            vencidos_text,
                        ]),
                    ft.Text("(15 días)", size=int(11 * scale), weight="bold", color=color_fondo),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=int(5 * scale)
            ),
            gradient=ft.LinearGradient(
                colors=["#D3D3D3", "#9E9E9E", "#545454"],
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right
            ),
            padding=int(15 * scale),
            border_radius=int(8 * scale),
            width=int(250 * scale),
            height=int(140 * scale),
            border=ft.border.all(color=color_fondo, width=1.5 * scale),
        ),
        elevation=14,
        shadow_color=color_tematica,
        margin=ft.margin.all(8 * scale),
    )

    # Composición final: 4 tarjetas en un Row.
    leyenda = ft.Row(
        controls=[card_fecha, card_activos, card_renovaciones, card_vencidos],
        spacing=int(20 * scale),
        alignment=ft.MainAxisAlignment.CENTER,
        wrap=True
    )

    # Actualización periódica usando un hilo clásico (sin timer ni run_on_ui_thread)
    import threading
    import time
    def actualizar_info():
        while True:
            fechaoficial, horaoficial = obtener_fecha_hora_actual()
            clientes_activos = obtener_clientes_activos()
            proximas_renovaciones = obtener_proximas_renovaciones()
            clientes_vencidos = obtener_clientes_vencidos()

            time_text.value = f"{fechaoficial} | {horaoficial}"
            active_clients_text.value = str(clientes_activos)
            renovaciones_text.value = str(proximas_renovaciones)
            vencidos_text.value = str(clientes_vencidos)
            try:
                page.update()
            except Exception:
                pass
            time.sleep(1)

    hilo_actualizacion = threading.Thread(target=actualizar_info, daemon=True)
    hilo_actualizacion.start()

    return leyenda