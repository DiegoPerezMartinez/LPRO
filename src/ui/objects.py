"""Module for managing the objects in the list."""
import flet as ft

def add_object(page, objects_list, name, range_val):
    """Add a new object to the list."""
    is_active = True
    status_text = ft.Text(f"Estado: {'Activado' if is_active else 'Desactivado'}")

    def toggle_active(e):
        """Toggle the active state of the object."""
        nonlocal is_active
        is_active = e.control.value  # Guardar el nuevo estado
        status_text.value = f"Estado: {'Activado' if is_active else 'Desactivado'}"
        page.update()  # Forzar actualización de la interfaz
        print(f"🔄 Estado de {name}: {status_text.value}")

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
                                  on_click=lambda _: remove_object(page, objects_list, card)),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
        )
    )

    objects_list.controls.append(card)
    page.update()

def remove_object(page, objects_list, card):
    """Remove an object from the list."""
    objects_list.controls.remove(card)
    page.update()
