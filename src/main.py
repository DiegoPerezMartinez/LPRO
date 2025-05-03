import threading
import asyncio
import flet as ft
from ui.layout import AppUI
from constants import PROJECT_NAME, BLE_ADDRESS, CHAR_UUID_TX, CHAR_UUID_RX
from ble.ble_client import BLEHandler
from ui.alerts import notify_detection

# Un evento para indicar cuando BLE está conectado
connection_event = asyncio.Event()

def run_ble_loop(ble_handler):
    """Función que corre el bucle BLE en un hilo separado."""
    async def runner():
        try:
            await ble_handler.connect()
            print("[BLE] Conectado y escuchando...")
            connection_event.set()  # Señalizamos que la conexión BLE ha sido exitosa
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            print(f"❌ Error BLE: {e}")

    threading.Thread(target=lambda: asyncio.run(runner()), daemon=True).start()

def main(page: ft.Page):
    """Función principal que inicializa la app y su layout."""
    page.title = PROJECT_NAME
    page.window_width = 400
    page.window_height = 700
    page.scroll = ft.ScrollMode.AUTO

    def on_ble_data(data):
        print(f"Received BLE data: {data}")
        notify_detection(page, data)

    ble_handler = BLEHandler(BLE_ADDRESS, CHAR_UUID_TX, CHAR_UUID_RX, on_ble_data)
    run_ble_loop(ble_handler)
    
    app_ui = AppUI(page, ble_handler)
    page.add(app_ui)

    async def wait_and_send_tags():
        # Esperamos a que BLE se conecte correctamente antes de enviar los tags
        await connection_event.wait()  # Esperamos hasta que la conexión BLE esté lista
        await asyncio.sleep(2)
        app_ui.send_active_tags_to_esp32()

    page.run_task(wait_and_send_tags)

ft.app(target=main, view=ft.AppView.FLET_APP)
