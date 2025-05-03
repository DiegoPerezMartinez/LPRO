"""Module for managing the objects in the list."""
import flet as ft
from database import save_object, update_object_status, delete_object

def add_object(page, objects_list, name, uuid, is_active=True, ble_handler=None):
    """Add a new object to the list."""
    status_text = ft.Text(f"Estado: {'Activado' if is_active else 'Desactivado'}")

    async def toggle_active_ble():
        if ble_handler:
            await ble_handler.send_command(f"UPDATE:{uuid.upper()}")

    def toggle_active(e):
        """Toggle the active state of the object."""
        nonlocal is_active
        is_active = e.control.value  # Guardar el nuevo estado
        status_text.value = f"Estado: {'Activado' if is_active else 'Desactivado'}"
        update_object_status(name, uuid, is_active)
        page.update()
        page.run_task(toggle_active_ble)

    def confirm_delete(e):
        """Show a confirmation dialog before deleting the object."""
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Seguro que quieres eliminar '{name}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.close(confirm_dialog)),
                ft.TextButton("Confirmar",
                              on_click=lambda e: remove_object(page, objects_list, card,
                                                               name, uuid, confirm_dialog, ble_handler))
            ],
            modal=True
        )
        page.dialog = confirm_dialog
        page.open(confirm_dialog)

    toggle_button = ft.Switch(
        value=is_active,
        on_change=toggle_active
    )

    card = create_object_card(name, uuid, toggle_button, status_text, confirm_delete, page)


    objects_list.controls.append(card)
    save_object(name, uuid, is_active)
    page.update()

def remove_object(page, objects_list, card, name, uuid, confirm_dialog, ble_handler=None):
    """Remove an object from the list."""
    objects_list.controls.remove(card)
    delete_object(name, uuid)
    if ble_handler:
        async def send_del():
            await ble_handler.send_command(f"DEL:{uuid.upper()}")
        page.run_task(send_del)
    page.close(confirm_dialog)
    page.update()

def create_object_card(name, uuid, toggle_button, status_text, confirm_delete, page):
    """Create a card for the object."""
    def show_info_dialog(e):
        info_dialog = ft.AlertDialog(
            title=ft.Text(name),
            content=ft.Column([
                ft.Text(f"UUID: {uuid}"),
                status_text  # Ahora el estado se muestra dentro del diálogo
            ]),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: page.close(info_dialog))],
        )
        page.dialog = info_dialog
        page.open(info_dialog)

    card = ft.Card(
        content=ft.Container(
            ft.Row(
                [
                    ft.IconButton(ft.Icons.INFO_OUTLINE,
                                  on_click=show_info_dialog,
                                  tooltip="Información"),
                    ft.Text(name, size=16),
                    toggle_button,  
                    ft.IconButton(ft.Icons.DELETE, on_click=confirm_delete),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
        )
    )
    return card
