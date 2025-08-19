import flet as ft
import json
import time

def cargar_configuracion():
    with open("config.json", "r") as config_file:
        return json.load(config_file)

def vista_menu(page, color_letras=None, color_fondo=None, color_tematica=None):
    configuracion = cargar_configuracion()
    color_fondo = color_fondo or configuracion.get("color_fondo", "#FFFFFF")
    color_letras = color_letras or configuracion.get("color_letras", "#000000")
    color_tematica = color_tematica or configuracion.get("color_tematica", "#000000")

    def toggle_fullscreen(e=None):
        page.window.full_screen = not page.window.full_screen
        page.update()

    # Variable para el escalado global
    if not hasattr(page, "global_scale"):
        page.global_scale = 1.0

    def cambiar_escala(delta):
        try:
            page.update()
            nueva_escala = max(0.5, min(2.0, round(page.global_scale + delta, 2)))
            if nueva_escala <= 0:
                print(f"[DEBUG] Valor de escala inválido: {nueva_escala}")
                return
            page.global_scale = nueva_escala
            print(f"[DEBUG] Escala cambiada a: {page.global_scale}")
            # Forzar limpiar controles y overlays antes de reconstruir
            page.controls.clear()
            # Solo limpiar overlays que no sean el menú
            page.overlay[:] = [ctrl for ctrl in page.overlay if ctrl is menu]
            page.update()
            # Refrescar ambas vistas si existen
            rebuilds = []
            if hasattr(page, "rebuild_vista_actual") and callable(page.rebuild_vista_actual):
                try:
                    print("[DEBUG] Llamando a rebuild_vista_actual() tras zoom")
                    page.rebuild_vista_actual()
                    rebuilds.append("rebuild_vista_actual")
                except Exception as ex:
                    import traceback
                    print(f"[DEBUG] Error al reconstruir la vista actual tras zoom: {ex}")
                    traceback.print_exc()
            if hasattr(page, "rebuild_dashboard") and callable(page.rebuild_dashboard):
                try:
                    print("[DEBUG] Llamando a rebuild_dashboard() tras zoom")
                    page.rebuild_dashboard()
                    rebuilds.append("rebuild_dashboard")
                except Exception as ex:
                    import traceback
                    print(f"[DEBUG] Error al reconstruir el dashboard tras zoom: {ex}")
                    traceback.print_exc()
            if not rebuilds:
                if hasattr(page, "on_route_change") and callable(page.on_route_change):
                    route = getattr(page, "route", None) or getattr(page, "last_route", "/")
                    try:
                        page.on_route_change(type('Event', (), {'route': route})())
                    except Exception as ex:
                        import traceback
                        print(f"[DEBUG] Error en on_route_change tras zoom: {ex}")
                        traceback.print_exc()
                else:
                    # Fallback: recarga la página según la ruta actual
                    page.clean()
                    if hasattr(page, "add") and callable(page.add):
                        try:
                            route = getattr(page, "route", None) or getattr(page, "last_route", "/")
                            vista = None
                            if route == "/historial_movimientos":
                                try:
                                    from views.historial_movimientos import vista_historial_movimientos
                                    vista = vista_historial_movimientos(page)
                                except Exception as ex:
                                    import traceback
                                    print(f"[DEBUG] Error cargando vista_historial_movimientos: {ex}")
                                    traceback.print_exc()
                            elif route == "/Stock":
                                from views.Stock import vista_stock
                                vista = vista_stock(page)
                            elif route == "/add_client":
                                from views.add_client import vista_add_client
                                vista = vista_add_client(page)
                            elif route == "/historial_pagos":
                                from views.Ingresos import vista_ingresos
                                vista = vista_ingresos(page)
                            elif route == "/configuraciones":
                                from views.configuraciones import vista_configuraciones
                                vista = vista_configuraciones(page)
                            else:
                                from views.dashboard import vista_dashboard
                                vista = vista_dashboard(page)
                            if vista is not None:
                                page.add(vista)
                            else:
                                print(f"[DEBUG] No se pudo recargar la vista para la ruta: {route}")
                        except Exception as ex:
                            import traceback
                            print(f"[DEBUG] No se pudo recargar la vista tras zoom: {ex}")
                            traceback.print_exc()
                    page.update()
        except Exception as ex:
            import traceback
            print(f"[DEBUG] Error en cambiar_escala: {ex}")
            traceback.print_exc()

    # Crear el menú desplegable como un `Container` con animaciones
    menu = ft.Container(
        visible=False,  # Oculto por defecto
        width=300,
        height=page.window.height,  # Fijar el alto al crear
        bgcolor=color_fondo,
        alignment=ft.alignment.top_left,
        opacity=0,  # Inicia con opacidad 0 para animación de apertura
        left=-300,  # Inicia fuera de pantalla para animación de deslizamiento
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        animate_position=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        top=0,
        content=ft.Row(
            controls=[
                ft.Container(
                    width=288,  # Deja espacio para la línea vertical
                    height=page.window.height,
                    bgcolor=color_fondo,
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                alignment=ft.alignment.top_right,
                                padding=0,
                                content=ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    on_click=lambda _: cerrar_menu(page, menu),
                                    style=ft.ButtonStyle(
                                        bgcolor="transparent",
                                        icon_color=color_letras,
                                        shape=ft.CircleBorder(),
                                        padding=ft.padding.all(8),
                                    ),
                                    tooltip="Cerrar menú"
                                ),
                            ),
                            ft.Container(
                                alignment=ft.alignment.center_left,
                                padding=ft.padding.only(left=8, bottom=8),
                                content=ft.Text("Menú Principal", size=22, weight="bold", color=color_letras),
                            ),
                            ft.ListView(
                                controls=[
                                    ft.ListTile(title=ft.Text("Dashboard", color=color_letras), leading=ft.Icon(ft.Icons.DASHBOARD, color=color_tematica), on_click=lambda _: navegar_y_cerrar(page, menu, "/")),
                                    ft.ListTile(title=ft.Text("Historial de Movimientos", color=color_letras), leading=ft.Icon(ft.Icons.HISTORY, color=color_tematica), on_click=lambda _: navegar_y_cerrar(page, menu, "/historial_movimientos")),
                                    ft.ListTile(title=ft.Text("Agregar Clientes", color=color_letras), leading=ft.Icon(ft.Icons.PERSON_ADD, color=color_tematica), on_click=lambda _: navegar_y_cerrar(page, menu, "/add_client")),
                                    ft.ListTile(title=ft.Text("Ingresos", color=color_letras), leading=ft.Icon(ft.Icons.ATTACH_MONEY, color=color_tematica), on_click=lambda _: navegar_y_cerrar(page, menu, "/historial_pagos")),
                                    ft.ListTile(title=ft.Text("Stock", color=color_letras), leading=ft.Icon(ft.Icons.STORE, color=color_tematica), on_click=lambda _: navegar_y_cerrar(page, menu, "/Stock")),
                                    ft.ListTile(title=ft.Text("Configuraciones", color=color_letras), leading=ft.Icon(ft.Icons.SETTINGS, color=color_tematica), on_click=lambda _: navegar_y_cerrar(page, menu, "/configuraciones")),
                                ]
                            ),
                            ft.Container(height=200),
                            ft.Container(
                                alignment=ft.alignment.center,
                                padding=ft.padding.all(8),
                                content=ft.Row([
                                    ft.IconButton(
                                        icon=ft.Icons.FULLSCREEN,
                                        tooltip="Full-screen",
                                        style=ft.ButtonStyle(
                                            bgcolor=color_fondo,
                                            icon_color=color_tematica,
                                            shape=ft.CircleBorder(),
                                            padding=ft.padding.all(12),
                                        ),
                                        on_click=toggle_fullscreen,
                                        width=48,
                                        height=48,
                                    ),
                                ], spacing=16),
                                margin=ft.margin.only(top=8, bottom=16)
                            ),
                        ],
                        scroll="adaptive",
                    ),
                    padding=0
                ),
                # Línea vertical color_tematica a la derecha
                ft.Container(
                    width=3,
                    height=page.window.height,
                    bgcolor=color_tematica,
                    alignment=ft.alignment.top_right,
                ),
            ]
        ),
        padding=0
    )
    menu.is_menu_panel = True  # Atributo único para identificar el menú lateral

    # Agregar menú a `page.overlay` solo una vez y siempre al principio
    if menu not in page.overlay:
        page.overlay.insert(0, menu)

    def actualizar_alto_menu(e=None):
        if hasattr(menu, 'page') and menu.page is not None:
            menu.height = menu.page.window.height
            if isinstance(menu.content, ft.Row):
                for c in menu.content.controls:
                    c.height = menu.page.window.height
            menu.update()

    # Vincular el evento de resize de la ventana
    page.on_resize = actualizar_alto_menu
    # Botón para abrir el menú con animación
    boton_menu = ft.IconButton(
        icon=ft.Icons.MENU,
        on_click=lambda _: abrir_menu(page, menu),
        style=ft.ButtonStyle(bgcolor=color_tematica, icon_color="black"),
    )

    return ft.Container(
        content=boton_menu,
        alignment=ft.alignment.top_left,
        padding=10
    )

def abrir_menu(page, menu):
    menu.height = page.window.height
    if isinstance(menu.content, ft.Row):
        for c in menu.content.controls:
            c.height = page.window.height
    menu.left = 0
    menu.opacity = 1
    menu.visible = True
    page.update()

def cerrar_menu(page, menu):
    """Cierra el menú con una animación de desvanecimiento y deslizamiento usando time.sleep()."""
    menu.opacity = 0
    menu.left = -300
    page.update()
    time.sleep(0.2)
    menu.visible = False
    page.update()

def navegar_y_cerrar(page, menu, ruta):
    """Cambia de vista y cierra el menú con animación. Limpia la página y overlays antes de navegar, pero nunca elimina el menú del overlay."""
    if page.route == ruta:
        cerrar_menu(page, menu)
        return  # No navega ni limpia si ya está en la misma ruta
    cerrar_menu(page, menu)
    # Elimina todos los overlays excepto el menú
    page.overlay[:] = [ctrl for ctrl in page.overlay if ctrl is menu]
    page.clean()  # Limpia todos los controles antes de navegar
    page.global_scale = 1.0  # Resetear zoom al valor por defecto
    page.go(ruta)