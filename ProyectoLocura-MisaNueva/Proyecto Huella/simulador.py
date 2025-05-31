import flet as ft
import random

def simular_huella():
    """Simula la captura de una huella digital"""
    huellas_fake = ["HUELLA_123", "HUELLA_456", "HUELLA_789"]
    return random.choice(huellas_fake)  # Devuelve una huella simulada

def main(page: ft.Page):
    page.title = "Simulador de Huella Digital"

    estado = ft.Text("Coloca tu dedo en el sensor", size=16, weight="bold", color="blue")
    imagen_huella = ft.Container(width=150, height=150, bgcolor="gray", border_radius=75, alignment=ft.alignment.center)

    def escanear_huella(e):
        estado.value = "Escaneando huella..."
        page.update()

        # Simular captura de huella
        huella = simular_huella()
        estado.value = f"Huella capturada: {huella}"
        estado.color = "green"
        page.update()

    btn_escanear = ft.ElevatedButton("Escanear Huella", on_click=escanear_huella)

    page.add(ft.Column([
        ft.Text("Simulador de Lector de Huella Digital", size=20, weight="bold"),
        estado,
        imagen_huella,
        btn_escanear
    ], alignment=ft.MainAxisAlignment.CENTER))

ft.app(target=main)