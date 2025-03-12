import flet as ft

def vista_propaganda(page):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Propaganda",
                    size=18,
                    weight="bold",
                    color="white",
                    # Aplica BoxShadow si es compatible con el texto:
                    # No todos los widgets admiten sombras directamente,
                    # por lo que quizás necesites usarlo en un contenedor externo.
                ),
                ft.Text("Contenido de la propaganda...", color="white"),
            ],
            spacing=10,
        ),
        bgcolor="#2C3E50",
        padding=15,
        alignment=ft.alignment.top_left,
        expand=True,
        shadow=ft.BoxShadow(  # Aplica sombra para el contenedor en su lugar
            spread_radius=2,
            blur_radius=10,
            color="black"
        )
    )
