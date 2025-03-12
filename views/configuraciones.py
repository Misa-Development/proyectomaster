import flet as ft
import json
from tematica import actualizar_tematica, setear_colores
from views.Menu import vista_menu

# Ruta del archivo de configuración
CONFIG_FILE = "config.json"

# Leer configuración desde archivo
def cargar_configuracion():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        # Configuración predeterminada si el archivo no existe
        config = {
            "color_fondo": "#FFFFFF",
            "color_tematica": "#000000",
            "color_letras": "#000000",
            "nombre_gimnasio": "Mi Gimnasio",
            "idioma": "Español (es)"
        }

    # Asegurar que todas las claves necesarias estén presentes
    config.setdefault("color_fondo", "#FFFFFF")
    config.setdefault("color_tematica", "#000000")
    config.setdefault("color_letras", "#000000")
    config.setdefault("nombre_gimnasio", "Mi Gimnasio")
    config.setdefault("idioma", "Español (es)")
    return config

# Guardar configuración en archivo
def guardar_configuracion(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Función para abrir una paleta de colores RGB
def abrir_paleta_color(page, titulo, campo_color, key):
    # Obtener valores iniciales del color actual
    color_actual = campo_color.value
    r, g, b = (0, 0, 0)  # Valores predeterminados si no hay color previo
    if color_actual.startswith("rgb"):
        # Extraer valores RGB del formato "rgb(r, g, b)"
        r, g, b = map(int, color_actual[4:-1].split(","))

    # Sliders para la paleta de colores RGB
    red_slider = ft.Slider(min=0, max=255, divisions=255, value=r, label=f"Rojo: {r}")
    green_slider = ft.Slider(min=0, max=255, divisions=255, value=g, label=f"Verde: {g}")
    blue_slider = ft.Slider(min=0, max=255, divisions=255, value=b, label=f"Azul: {b}")
    
    # Actualizar dinámicamente el ejemplo de color
    color_ejemplo = ft.Container(
        width=50,
        height=50,
        bgcolor=f"rgb({r},{g},{b})",
        border_radius=5
    )

    def actualizar_color_ejemplo(e):
        nuevo_color = f"rgb({int(red_slider.value)},{int(green_slider.value)},{int(blue_slider.value)})"
        color_ejemplo.bgcolor = nuevo_color
        campo_color.value = nuevo_color  # Actualiza el campo dinámicamente
        configuracion[key] = nuevo_color  # Actualiza la configuración
        red_slider.label = f"Rojo: {int(red_slider.value)}"
        green_slider.label = f"Verde: {int(green_slider.value)}"
        blue_slider.label = f"Azul: {int(blue_slider.value)}"
        
        # Aplica cambios instantáneamente si es color de letras
        if key == "color_letras":
            actualizar_tematica(page)
        
        page.update()

    red_slider.on_change = actualizar_color_ejemplo
    green_slider.on_change = actualizar_color_ejemplo
    blue_slider.on_change = actualizar_color_ejemplo

    # Guardar el color seleccionado
    def guardar_color(e):
        nuevo_color = f"rgb({int(red_slider.value)},{int(green_slider.value)},{int(blue_slider.value)})"
        campo_color.value = nuevo_color
        configuracion[key] = nuevo_color  # Actualizar configuración
        guardar_configuracion(configuracion)  # Guardar cambios en config.json
        page.dialog.open = False
        page.update()

    # Diálogo para la paleta de colores
    dialog = ft.AlertDialog(
        title=ft.Text(titulo, weight="bold"),
        content=ft.Column([
            red_slider,
            green_slider,
            blue_slider,
            ft.Row([ft.Text("Color Actual:"), color_ejemplo])  # Mostrar color actual
        ], spacing=10),
        actions=[
            ft.TextButton("Guardar", on_click=guardar_color),
            ft.TextButton("Cancelar", on_click=lambda e: setattr(dialog, "open", False))
        ],
        modal=True
    )
    page.dialog = dialog
    dialog.open = True
    page.update()

# Función para cambiar colores en general
def cambiar_colores(page):
    setear_colores(campo_color_fondo.value, campo_color_tematica.value, campo_color_letras.value)
    configuracion["color_fondo"] = campo_color_fondo.value
    configuracion["color_tematica"] = campo_color_tematica.value
    configuracion["color_letras"] = campo_color_letras.value
    guardar_configuracion(configuracion)
    actualizar_tematica(page)
    page.snack_bar = ft.SnackBar(ft.Text("¡Colores actualizados correctamente!"))
    page.snack_bar.open = True
    page.update()

# Función para cambiar el nombre del gimnasio
def cambiar_nombre_gimnasio(page):
    nuevo_nombre = campo_nombre_gimnasio.value
    configuracion["nombre_gimnasio"] = nuevo_nombre
    guardar_configuracion(configuracion)
    page.snack_bar = ft.SnackBar(ft.Text("¡Nombre del gimnasio actualizado correctamente!"))
    page.snack_bar.open = True
    page.update()

# Función para cambiar el idioma
def cambiar_idioma(page):
    nuevo_idioma = selector_idioma.value
    configuracion["idioma"] = nuevo_idioma
    guardar_configuracion(configuracion)
    page.snack_bar = ft.SnackBar(ft.Text(f"Idioma cambiado a '{nuevo_idioma}'"))
    page.snack_bar.open = True
    page.update()
# Vista principal
def vista_configuraciones(page):
    page.title = "Configuraciones"
    page.window_maximized = True

    titulo = ft.Text(
        "Configuraciones",
        style="displaySmall",
        color=configuracion["color_letras"],
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )

    # Menú horizontal en la parte superior
    menu = vista_menu(page)

    # Campos de entrada para colores
    global campo_color_fondo, campo_color_tematica, campo_color_letras, campo_nombre_gimnasio, selector_idioma
    campo_color_fondo = ft.TextField(label="Color de Fondo", value=configuracion["color_fondo"])
    campo_color_tematica = ft.TextField(label="Color de la Temática", value=configuracion["color_tematica"])
    campo_color_letras = ft.TextField(label="Color de las Letras", value=configuracion["color_letras"])

    # Campo para cambiar el nombre del gimnasio
    campo_nombre_gimnasio = ft.TextField(
        label="Nombre del Gimnasio",
        value=configuracion["nombre_gimnasio"]
    )

    # Campo para cambiar el idioma
    selector_idioma = ft.Dropdown(
        label="Idioma",
        options=[
            ft.dropdown.Option("Español (es)"),
            ft.dropdown.Option("Inglés (en)")
        ],
        value=configuracion["idioma"]
    )

    # Tarjetas de configuración
    tarjetas_configuraciones = ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Text("Apariencia", style="headlineMedium", color=configuracion["color_letras"]),
                ft.Text("Configura los colores de la aplicación.", color=configuracion["color_letras"]),
                ft.Row([
                    campo_color_fondo,
                    ft.IconButton(
                        icon=ft.icons.PALETTE,
                        tooltip="Seleccionar color de fondo",
                        on_click=lambda e: abrir_paleta_color(page, "Color de Fondo", campo_color_fondo, "color_fondo")
                    )
                ]),
                ft.Row([
                    campo_color_tematica,
                    ft.IconButton(
                        icon=ft.icons.PALETTE,
                        tooltip="Seleccionar color de temática",
                        on_click=lambda e: abrir_paleta_color(page, "Color de Temática", campo_color_tematica, "color_tematica")
                    )
                ]),
                ft.Row([
                    campo_color_letras,
                    ft.IconButton(
                        icon=ft.icons.PALETTE,
                        tooltip="Seleccionar color de letras",
                        on_click=lambda e: abrir_paleta_color(page, "Color de Letras", campo_color_letras, "color_letras")
                    )
                ]),
                ft.ElevatedButton(
                    text="Aplicar Colores",
                    icon=ft.icons.COLOR_LENS,
                    on_click=lambda e: cambiar_colores(page)
                )
            ]),
            padding=5,
            border=ft.border.all(1),
            border_radius=5,
            margin=5
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Idioma", style="headlineMedium", color=configuracion["color_letras"]),
                ft.Text("Selecciona el idioma de la aplicación.", color=configuracion["color_letras"]),
                selector_idioma,
                ft.ElevatedButton(
                    text="Guardar Idioma",
                    icon=ft.icons.LANGUAGE,
                    on_click=lambda e: cambiar_idioma(page)
                )
            ]),
            padding=5,
            border=ft.border.all(1),
            border_radius=5,
            margin=5
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Nombre del Gimnasio", style="headlineMedium", color=configuracion["color_letras"]),
                campo_nombre_gimnasio,
                ft.ElevatedButton(
                    text="Guardar Nombre",
                    icon=ft.icons.SAVE,
                    on_click=lambda e: cambiar_nombre_gimnasio(page)
                )
            ]),
            padding=5,
            border=ft.border.all(1),
            border_radius=5,
            margin=5
        )
    ], spacing=10)

    # Contenedor desplazable
    layout = ft.ListView(
        controls=[
            menu,
            titulo,
            tarjetas_configuraciones
        ],
        spacing=20,
        expand=True
    )

    # Añadir todo a la página
    page.add(layout)
    actualizar_tematica(page)
    page.update()


# Cargar configuración inicial
configuracion = cargar_configuracion()
