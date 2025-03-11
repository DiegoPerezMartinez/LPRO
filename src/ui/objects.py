"""Module for managing the objects in the list."""
import flet as ft
from database import save_object, update_object_status, delete_object

def add_object(page, objects_list, name, range_val, is_active=True):
    """Add a new object to the list."""
    status_text = ft.Text(f"Estado: {'Activado' if is_active else 'Desactivado'}")

    def toggle_active(e):
        """Toggle the active state of the object."""
        nonlocal is_active
        is_active = e.control.value  # Guardar el nuevo estado
        status_text.value = f"Estado: {'Activado' if is_active else 'Desactivado'}"
        update_object_status(name, range_val, is_active)
        page.update()  # Forzar actualización de la interfaz

    def confirm_delete(e):
        """Show a confirmation dialog before deleting the object."""
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Seguro que quieres eliminar '{name}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.close(confirm_dialog)),
                ft.TextButton("Confirmar", 
                              on_click=lambda e: remove_object(page, objects_list, card, 
                                                               name, range_val, confirm_dialog))
            ],
            modal=True
        )
        page.dialog = confirm_dialog
        page.open(confirm_dialog)

    toggle_button = ft.Switch(
        value=is_active,
        on_change=toggle_active
    )

    card = ft.Card(
        content=ft.Container(
            ft.Row(
                [
                    ft.Icon(ft.icons.RADIO_BUTTON_CHECKED, color=ft.colors.BLUE),
                    ft.Text(f"{name} (Alcance: {range_val}m)", size=16),
                    toggle_button,
                    status_text,
                    ft.IconButton(ft.icons.DELETE,
                                  on_click=confirm_delete),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
        )
    )

    objects_list.controls.append(card)
    save_object(name, range_val, is_active)
    page.update()

def remove_object(page, objects_list, card, name, range_val, confirm_dialog):
    """Remove an object from the list."""
    objects_list.controls.remove(card)
    delete_object(name, range_val)
    page.close(confirm_dialog)
    page.update()
