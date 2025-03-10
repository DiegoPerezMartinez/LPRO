"""Implement dialog to add a new object to the list of objects"""
import flet as ft
from .objects import add_object

def open_add_dialog(page, objects_list):
    """Open dialog to add a new object"""
    name_input = ft.TextField(label="Nombre del objeto", autofocus=True)
    range_dropdown = ft.Dropdown(
        label="Alcance (m)",
        options=[ft.dropdown.Option(str(m)) for m in [1, 3, 5, 10]]
    )

    def add_object_handler():
        """Handle the addition of a new object"""
        if not name_input.value or not range_dropdown.value:
            name_input.error_text = "⚠ Nombre y alcance requeridos"
            page.update()
            return

        add_object(page, objects_list, name_input.value.strip(), range_dropdown.value)
        page.close(dialog)
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        open=True,
        title=ft.Text("Añadir nuevo objeto"),
        content=ft.Column([name_input, range_dropdown]),
        actions=[ft.ElevatedButton("Añadir", on_click=add_object_handler)],
    )

    page.dialog = dialog
    page.open(dialog)
    page.update()
