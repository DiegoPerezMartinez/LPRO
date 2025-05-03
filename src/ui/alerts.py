"""Módulo para manejar alertas visuales y sonoras en la interfaz de usuario."""
import os
import winsound
import threading
import flet as ft
from database import load_objects

def play_sound(mode="BUS"):
    """Reproduce un sonido en segundo plano."""
    filename = "Enemy_Missing_ping_SFX.wav" if mode == "BUS" else "Caution_ping_SFX.wav"
    sound_path = os.path.join(os.path.dirname(__file__),
                              '..', 'sounds', filename)
    sound_path = os.path.abspath(sound_path)
    try:
        winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        print(f"[🔊 Error al reproducir sonido] {e}")

def notify_detection(page, uuid_detected, mode="BUS"):
    """Notifica visual y sonoramente la detección de un UUID según el modo."""
    matched = next((obj for obj in load_objects()
                    if obj["uuid"].upper() == uuid_detected.upper()), None)

    if matched:
        name = matched["name"]
    else:
        name = uuid_detected

    if mode == "BUS":
        message = f"📦 Objeto detectado: {name}" if matched else f"🆔 Etiqueta desconocida detectada: {uuid_detected}"
        color = ft.colors.GREEN_400
    else:  # modo SEGUIMIENTO
        message = f"❌ Objeto PERDIDO: {name}"
        color = ft.colors.RED_400

    snackbar = ft.SnackBar(ft.Text(message),
                           bgcolor=color,
                           show_close_icon=True)
    page.snack_bar = snackbar
    page.snack_bar.open = True
    page.open(snackbar)
    page.update()

    threading.Thread(target=play_sound, args=(mode,), daemon=True).start()
