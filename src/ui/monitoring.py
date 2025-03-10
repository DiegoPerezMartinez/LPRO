"""Monitoring module."""
import random
import flet as ft

def check_objects(tracked_objects):
    """Check if any object is out of range."""
    if random.random() < 0.05:  # Simulación de pérdida (30% de probabilidad)
        return random.choice(tracked_objects)
    return None

def start_monitoring(page, objects_list, alert_text):
    """Start monitoring the objects."""
    active_objects = []

    for card in objects_list.controls:
        if isinstance(card, ft.Card):
            row = card.content.content
            object_name = row.controls[1].value
            toggle_button = row.controls[2]

            if toggle_button.value:
                active_objects.append(object_name)

    if not active_objects:
        alert_text.value = "⚠ No hay objetos ACTIVADOS para monitorear."
        page.update()
        return

    lost_object = check_objects(active_objects)

    if lost_object:
        alert_text.value = f"🚨 ¡Alerta! {lost_object} se ha alejado"
    else:
        alert_text.value = "✅ Todos los objetos activados están en rango"

    page.update()
