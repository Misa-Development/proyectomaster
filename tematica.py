import flet as ft
import json

# Ruta del archivo de configuración
CONFIG_FILE = "config.json"

# Variables globales para los colores
color_fondo = "#FFFFFF"
color_tematica = "#000000"
color_letras = "#000000"

# Leer configuración desde el archivo JSON
def leer_configuracion():
    global color_fondo, color_tematica, color_letras
    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            # Respetar todas las claves del JSON
            color_fondo = config.get("color_fondo", "#FFFFFF")
            color_tematica = config.get("color_tematica", "#000000")
            color_letras = config.get("color_letras", "#000000")
            return config  # Retornar la configuración
    except FileNotFoundError:
        # Si el archivo no existe, crear con valores predeterminados
        config = {
            "color_fondo": "#FFFFFF",
            "color_tematica": "#000000",
            "color_letras": "#000000",
            "tema": "Light",  # Tema por defecto
            "nombre_gimnasio": "Mi Gimnasio",
            "idioma": "Español (es)"
        }
        escribir_configuracion(config)
        return config  # Retornar configuración recién creada

# Escribir configuración en el archivo JSON
def escribir_configuracion(config=None):
    global color_fondo, color_tematica, color_letras
    # Sincronizar las variables globales y las claves del JSON
    if config is None:
        config = {
            "color_fondo": color_fondo,
            "color_tematica": color_tematica,
            "color_letras": color_letras,
            "tema": "Light",  # Mantener el tema
            "nombre_gimnasio": "Mi Gimnasio",
            "idioma": "Español (es)"
        }
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

# Actualizar la temática visual en la página
def actualizar_tematica(page):
    # Actualizar directamente los colores del fondo y del tema visual
    page.bgcolor = color_fondo
    page.theme = ft.Theme(
        text_theme=ft.TextTheme(
            display_large=ft.TextStyle(color=color_letras),
            headline_large=ft.TextStyle(color=color_letras),
            label_large=ft.TextStyle(color=color_letras)
        ),
        icon_theme=ft.IconTheme(color=color_tematica)
    )
    page.update()  # Forzar actualización dinámica de la página

# Actualizar colores globales y guardar la configuración
def setear_colores(page, nuevo_color_fondo, nuevo_color_tematica, nuevo_color_letras):
    global color_fondo, color_tematica, color_letras
    
    # Actualizar las variables globales
    color_fondo = nuevo_color_fondo
    color_tematica = nuevo_color_tematica
    color_letras = nuevo_color_letras

    # Leer y actualizar el archivo JSON
    config = leer_configuracion()
    config["color_fondo"] = color_fondo
    config["color_tematica"] = color_tematica
    config["color_letras"] = color_letras
    escribir_configuracion(config)  # Guardar los cambios

    # Aplicar inmediatamente los colores
    actualizar_tematica(page)  # Actualizar la vista con los nuevos colores

# Leer la configuración al iniciar
leer_configuracion()