# notifier.py
import os
from database import load_objects
import threading
import flet as ft
import winsound

# Ruta del archivo de sonido (puedes cambiarla a tu gusto)
SOUND_FILE = "alerta.mp3"

def play_sound():
    """Reproduce un sonido en segundo plano."""
    sound_path = os.path.join(os.path.dirname(__file__), '..', 'sounds', 'Enemy_Missing_ping_SFX.wav')
    sound_path = os.path.abspath(sound_path)
    try:
        winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        print(f"[🔊 Error al reproducir sonido] {e}")

def notify_detection(page, uuid_detected):
    """Notifica visual y sonoramente la detección de un UUID."""
    # Buscar el objeto por UUID
    matched = next((obj for obj in load_objects() if obj["uuid"].upper() == uuid_detected.upper()), None)

    if matched:
        name = matched["name"]
        message = f"📦 Objeto detectado: {name}"
    else:
        name = uuid_detected
        message = f"🆔 Etiqueta desconocida detectada: {uuid_detected}"

    # Mostrar alerta visual
    snackbar = ft.SnackBar(ft.Text(message), bgcolor=ft.colors.GREEN_400, show_close_icon=True)
    page.snack_bar = snackbar
    page.snack_bar.open = True
    page.open(snackbar)
    page.update()

    # Reproducir sonido en hilo separado
    threading.Thread(target=play_sound, daemon=True).start()
