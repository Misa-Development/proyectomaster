# tematica.py
import flet as ft
import json

# Ruta del archivo de configuración
config_file = "config.json"

# Leer configuración desde el archivo JSON
def leer_configuracion():
    global color_fondo, color_tematica
    with open(config_file, "r") as file:
        config = json.load(file)
        color_fondo = config["color_fondo"]
        color_tematica = config["color_tematica"]
        color_letras = config.get("color_letras", "#000000")  # Valor predeterminado, puedes cambiarlo según tu preferencia
        
        

# Escribir configuración en el archivo JSON
def escribir_configuracion():
    with open(config_file, "w") as file:
        config = {
            "color_fondo": color_fondo,
            "color_tematica": color_tematica,
            "color_letras": color_letras 
        }
        json.dump(config, file)

# Variables globales para los colores (inicializados con valores por defecto)
color_fondo = "#FFFFFF"
color_tematica = "#000000"
color_letras = "#000000"  # Valor predeterminado, puedes cambiarlo según tu preferencia


# Leer la configuración al iniciar
leer_configuracion()

def actualizar_tematica(page):
    page.bgcolor = color_fondo  # Aplicar el color de fondo directamente a la página
    page.theme = ft.Theme(
        text_theme=ft.TextTheme(
            display_large=ft.TextStyle(color=color_letras),
            headline_large=ft.TextStyle(color=color_letras),
            label_large=ft.TextStyle(color=color_letras)
        ),
        icon_theme=ft.IconTheme(color=color_tematica)
    )
    page.update()

def setear_colores(nuevo_color_fondo, nuevo_color_tematica,nuevo_color_letras):
    global color_fondo, color_tematica
    color_fondo = nuevo_color_fondo
    color_tematica = nuevo_color_tematica
    color_letras = nuevo_color_letras 
    escribir_configuracion()
