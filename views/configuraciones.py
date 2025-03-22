import flet as ft
import json
from tematica import setear_colores
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
            "color_tematica": "#E8E8E8",
            "color_letras": "#000000",
            "tema": "Light",  # Tema por defecto
            "nombre_gimnasio": "Mi Gimnasio",
            "idioma": "Español"
        }
        guardar_configuracion(config)  # Crear archivo con valores predeterminados
        return config

    # Verificar claves necesarias y completarlas si faltan
    claves_necesarias = {
        "color_fondo": "#FFFFFF",
        "color_tematica": "#E8E8E8",
        "color_letras": "#000000",
        "tema": "Light",
        "nombre_gimnasio": "Mi Gimnasio",
        "idioma": "Español"
    }
    for clave, valor_defecto in claves_necesarias.items():
        if clave not in config:
            config[clave] = valor_defecto
    return config

# Guardar configuración en archivo
def guardar_configuracion(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Función para aplicar el tema
def aplicar_tema(page, configuracion):
    tema = configuracion["tema"]
    if tema == "Light":  # Tema claro
        configuracion["color_fondo"] = "#FFFFFF"
        configuracion["color_tematica"] = "#D3D3D3"
        configuracion["color_letras"] = "#000000"
    elif tema == "Dark":  # Tema oscuro
        configuracion["color_fondo"] = "#000000"
        configuracion["color_tematica"] = "#303030"
        configuracion["color_letras"] = "#FFFFFF"

    # Aplicar los colores sincronizados
    setear_colores(
        page,
        configuracion["color_fondo"],
        configuracion["color_tematica"],
        configuracion["color_letras"]
    )
    guardar_configuracion(configuracion)  # Guardar los cambios
    page.bgcolor = configuracion["color_fondo"]
    page.update()

# Función principal de la vista de configuraciones
def vista_configuraciones(page):
    configuracion = cargar_configuracion()  # Cargar configuración desde archivo
    aplicar_tema(page, configuracion)  # Aplicar el tema al cargar

    def reconstruir_vista():
        # Crear título con color dinámico
        titulo = ft.Text(
            "Configuraciones",
            style="displaySmall",
            color=configuracion["color_letras"],
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )

        # Crear menú horizontal
        menu = vista_menu(page)

        # Cambiar tema dinámicamente
        def cambiar_tema(e):
            configuracion["tema"] = selector_tema.value
            aplicar_tema(page, configuracion)  # Aplicar el nuevo tema
            reconstruir_vista()  # Reconstruir la vista

        # Guardar nombre del gimnasio
        def cambiar_nombre_gimnasio(e):
            configuracion["nombre_gimnasio"] = campo_nombre_gimnasio.value
            guardar_configuracion(configuracion)
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"¡Nombre del gimnasio actualizado a '{configuracion['nombre_gimnasio']}'!", color=configuracion["color_letras"])
            )
            page.snack_bar.open = True

        # Guardar idioma
        def cambiar_idioma(e):
            configuracion["idioma"] = selector_idioma.value
            guardar_configuracion(configuracion)
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Idioma cambiado a '{configuracion['idioma']}'!", color=configuracion["color_letras"])
            )
            page.snack_bar.open = True

        # Campos y botones dinámicos
        campo_nombre_gimnasio = ft.TextField(
            label="Nombre del Gimnasio",
            hint_text="Escribe aquí el nombre...",
            value=configuracion["nombre_gimnasio"],
            hint_style=ft.TextStyle(color=configuracion["color_letras"]),
            label_style=ft.TextStyle(color=configuracion["color_letras"]),
            text_style=ft.TextStyle(color=configuracion["color_letras"]),
            border_color=configuracion["color_letras"],
            bgcolor=configuracion["color_tematica"]
        )

        selector_idioma = ft.Dropdown(
            label="Idioma",
            options=[
                ft.dropdown.Option(key="Español", text="Español", style=ft.TextStyle(color=configuracion["color_letras"])),
                ft.dropdown.Option(key="Inglés", text="Inglés", style=ft.TextStyle(color=configuracion["color_letras"])),
            ],
            value=configuracion["idioma"],
            label_style=ft.TextStyle(color=configuracion["color_letras"]),
            text_style=ft.TextStyle(color=configuracion["color_letras"]),  # Texto seleccionado dinámico
            border_color=configuracion["color_letras"],
            bgcolor=configuracion["color_tematica"]
        )

        selector_tema = ft.Dropdown(
            label="Tema",
            options=[
                ft.dropdown.Option(key="Light", text="Tema Claro", style=ft.TextStyle(color=configuracion["color_letras"])),
                ft.dropdown.Option(key="Dark", text="Tema Oscuro", style=ft.TextStyle(color=configuracion["color_letras"])),
            ],
            value=configuracion["tema"],
            label_style=ft.TextStyle(color=configuracion["color_letras"]),
            text_style=ft.TextStyle(color=configuracion["color_letras"]),  # Texto seleccionado dinámico
            border_color=configuracion["color_letras"],
            bgcolor=configuracion["color_tematica"]
        )

        boton_guardar_nombre = ft.ElevatedButton(
            text="Guardar Nombre",
            icon=ft.icons.SAVE,
            style=ft.ButtonStyle(bgcolor=configuracion["color_tematica"], color=configuracion["color_letras"]),
            on_click=cambiar_nombre_gimnasio
        )

        boton_guardar_idioma = ft.ElevatedButton(
            text="Guardar Idioma",
            icon=ft.icons.LANGUAGE,
            style=ft.ButtonStyle(bgcolor=configuracion["color_tematica"], color=configuracion["color_letras"]),
            on_click=cambiar_idioma
        )

        boton_guardar_tema = ft.ElevatedButton(
            text="Guardar Tema",
            icon=ft.icons.COLOR_LENS,
            style=ft.ButtonStyle(bgcolor=configuracion["color_tematica"], color=configuracion["color_letras"]),
            on_click=cambiar_tema
        )

        # Contenedores para cada configuración
        contenedor_gimnasio = ft.Container(
            content=ft.Column([
                ft.Text("Configuración del Gimnasio", style="headlineMedium", color=configuracion["color_letras"]),
                campo_nombre_gimnasio,
                boton_guardar_nombre
            ]),
            padding=10,
            border=ft.border.all(1),
            border_radius=5,
            bgcolor=configuracion["color_tematica"]
        )

        contenedor_idioma = ft.Container(
            content=ft.Column([
                ft.Text("Configuración del Idioma", style="headlineMedium", color=configuracion["color_letras"]),
                selector_idioma,
                boton_guardar_idioma
            ]),
            padding=10,
            border=ft.border.all(1),
            border_radius=5,
            bgcolor=configuracion["color_tematica"]
        )

        contenedor_apariencia = ft.Container(
            content=ft.Column([
                ft.Text("Apariencia", style="headlineMedium", color=configuracion["color_letras"]),
                selector_tema,
                boton_guardar_tema
            ]),
            padding=10,
            border=ft.border.all(1),
            border_radius=5,
            bgcolor=configuracion["color_tematica"]
        )

        # Crear diseño completo
        layout = ft.Column(
            [
                menu,
                titulo,
                contenedor_apariencia,
                contenedor_gimnasio,
                contenedor_idioma
            ],
            spacing=20,
            expand=True,
            scroll="auto"
        )

        # Redibujar la página
        page.controls.clear()
        page.add(layout)
        page.update()

    reconstruir_vista()  # Construir vista inicial