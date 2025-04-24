import asyncio
import flet as ft
from bleak import BleakClient

# Configuración BLE
BLE_ADDRESS = "64:E8:33:8C:D3:A2"  # Cambia si tu dirección es distinta
CHAR_UUID_TX = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
CHAR_UUID_RX = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

class BLETester:
    def __init__(self, address, tx_uuid, rx_uuid):
        self.address = address
        self.tx_uuid = tx_uuid  # Para notificaciones
        self.rx_uuid = rx_uuid  # Para escritura
        self.client = BleakClient(address)
        self.response_future = None

    async def connect(self):
        await self.client.connect()
        await self.client.start_notify(self.tx_uuid, self.notification_handler)
        print("[BLE] Conectado")

    async def disconnect(self):
        await self.client.disconnect()

    def notification_handler(self, sender, data):
        message = data.decode("utf-8")
        print(f"[BLE] Recibido: {message}")
        if self.response_future and not self.response_future.done():
            self.response_future.set_result(message)

    async def send_command(self, command):
        await self.client.write_gatt_char(self.rx_uuid, command.encode("utf-8"))

    async def wait_for_response(self, timeout=10):
        self.response_future = asyncio.get_event_loop().create_future()
        return await asyncio.wait_for(self.response_future, timeout)

async def main(page: ft.Page):
    page.title = "BLE Test App"
    page.scroll = ft.ScrollMode.ALWAYS

    tester = BLETester(BLE_ADDRESS, CHAR_UUID_TX, CHAR_UUID_RX)

    status = ft.Text("Conectando...")
    uuid_display = ft.Text("UUID recibido: ---", size=18)

    async def connect_ble():
        try:
            await tester.connect()
            status.value = "✅ Conectado al ESP32 por BLE"
        except Exception as e:
            status.value = f"❌ Error al conectar: {e}"
        page.update()

    async def leer_etiqueta(e):
        status.value = "⌛ Leyendo etiqueta..."
        uuid_display.value = ""
        page.update()

        try:
            print("Enviando comando LEER_ETIQUETA al ESP32...")
            await tester.send_command("LEER_ETIQUETA")
            response = await tester.wait_for_response()

            if response.startswith("UUID:"):
                uuid = response.split("UUID:")[1].strip()
                uuid_display.value = f"✅ UUID recibido: {uuid}"
            else:
                uuid_display.value = f"⚠ Respuesta inesperada: {response}"
        except Exception as e:
            uuid_display.value = f"❌ Error: {e}"
        status.value = "Listo para leer"
        page.update()

    button = ft.ElevatedButton("📡 Leer etiqueta RFID", on_click=leer_etiqueta)

    page.add(status, button, uuid_display)

    await connect_ble()

ft.app(target=main, view=ft.AppView.FLET_APP)
