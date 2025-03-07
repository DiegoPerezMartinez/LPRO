import flet as ft
from ui import AppUI
from backend import RFIDBackend

def main(page: ft.Page):
    page.title = "Lossn't"
    page.window_width = 400
    page.window_height = 700
    page.scroll = ft.ScrollMode.AUTO  # Permitir scroll en móvil

    backend = RFIDBackend()
    app_ui = AppUI(page, backend)

    # Añadir la UI a la página
    page.add(app_ui)

ft.app(target=main, view=ft.AppView.FLET_APP)