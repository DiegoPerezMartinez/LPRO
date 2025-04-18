"""Import the necessary modules and
create the main function to initialize"""
import threading
import asyncio
import flet as ft
from ui.layout import AppUI
from constants import PROJECT_NAME,BLE_ADDRESS, CHAR_UUID_TX
from ble.ble_client import BLEHandler

def run_ble_loop(on_data_callback):
    """Function to run the BLE loop in a separate thread."""
    async def runner():
        ble = BLEHandler(BLE_ADDRESS, CHAR_UUID_TX, on_data_callback)
        try:
            await ble.connect()
            print("[BLE] Conectado y escuchando...")
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            print(f"❌ Error BLE: {e}")

    threading.Thread(target=lambda: asyncio.run(runner()), daemon=True).start()

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

    def on_ble_data(data):
        print(f"Received BLE data: {data}")
        

    run_ble_loop(on_ble_data)

ft.app(target=main, view=ft.AppView.FLET_APP)
