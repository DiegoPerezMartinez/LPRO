"""Import the necessary modules and
create the main function to initialize"""
import flet as ft
from ui.layout import AppUI
from constants import PROJECT_NAME

def main(page: ft.Page):
    """Main function to initialize the
    app and set the UI layout."""
    page.title = PROJECT_NAME
    page.window_width = 400
    page.window_height = 700
    page.scroll = ft.ScrollMode.AUTO

    app_ui = AppUI(page)

    # Añadir la UI a la página
    page.add(app_ui)

ft.app(target=main, view=ft.AppView.FLET_APP)
