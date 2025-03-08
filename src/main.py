import flet as ft
from ui.layout import AppUI

def main(page: ft.Page):
    page.title = "Lossn't"
    page.window_width = 400
    page.window_height = 700
    page.scroll = ft.ScrollMode.AUTO  

    app_ui = AppUI(page)

    # Añadir la UI a la página
    page.add(app_ui)

ft.app(target=main, view=ft.AppView.FLET_APP)
