"""This module contains the function to open a dialog for adding a new object."""
import flet as ft
from .objects import add_object
from queue import Empty

def open_add_dialog(page, objects_list, ble_handler):
    """Open dialog to add a new object using shared BLE handler."""
    status_text = ft.Text("🔍 Añadiendo objeto, por favor acerque la etiqueta al lector...", size=16)
    name_input = ft.TextField(label="Nombre del objeto", autofocus=True)
    uuid_field = ft.TextField(label="UUID", read_only=True)

    # Esta variable almacenará el último UUID leído
    last_uuid = {"value": None}

    # Función de callback para manejar la respuesta BLE
    async def read_label():
        while not ble_handler.notification_queue.empty():
            try:
                ble_handler.notification_queue.get_nowait()
            except Empty:
                break
        await ble_handler.send_command("LEER_ETIQUETA")
        label_data = ble_handler.wait_for_response()
        if label_data and label_data != last_uuid["value"]:
            last_uuid["value"] = label_data
            uuid_field.value = label_data
            status_text.value = f"✅ Etiqueta detectada: {label_data}"
        else:
            status_text.value = "⚠ Ya se usó esta etiqueta. Intente con otra."
        page.update()

    def add_object_handler(e):
        """Handle the confirmation of the object."""
        if not name_input.value or not uuid_field.value:
            name_input.error_text = "⚠ Nombre y UUID requeridos"
            page.update()
            return

        add_object(page, objects_list, name_input.value.strip(), uuid_field.value,True ,ble_handler)
        page.close(dialog)
        page.update()

    def cancel_handler(e):
        """Handle cancellation of the dialog."""
        page.close(dialog)
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        open=True,
        title=ft.Text("Añadir nuevo objeto"),
        content=ft.Column([
            status_text,
            name_input,
            uuid_field,
        ]),
        actions=[
            ft.ElevatedButton("Añadir", on_click=add_object_handler),
            ft.TextButton("Cancelar", on_click=cancel_handler)
        ],
    )

    page.dialog = dialog
    page.open(dialog)
    page.update()
    page.run_task(read_label)
