"""Módulo para manejar la conexión BLE y recibir notificaciones."""
from bleak import BleakClient
import asyncio

class BLEHandler:
    """Clase para manejar la conexión BLE y recibir notificaciones."""
    def __init__(self, address, characteristic_uuid, on_data_callback):
        self.address = address
        self.characteristic_uuid = characteristic_uuid
        self.client = BleakClient(address)
        self.on_data_callback = on_data_callback

    async def connect(self):
        """Conecta al dispositivo BLE y comienza a recibir notificaciones."""
        await self.client.connect()
        print(f"[BLE] Conectado a {self.address}")
        await self.client.start_notify(self.characteristic_uuid, self.notification_handler)

    def notification_handler(self, sender, data):
        """Manejador de notificaciones. Se llama cuando se recibe una notificación."""
        decoded = data.decode("utf-8")
        print(f"[BLE] Recibido: {decoded}")
        self.on_data_callback(decoded)

    async def disconnect(self):
        """Desconecta del dispositivo BLE."""
        await self.client.stop_notify(self.characteristic_uuid)
        await self.client.disconnect()

    async def add_label(self):
        """Solicita al ESP32 leer una etiqueta."""
        if not self.client.is_connected:
            print("[BLE] No está conectado.")
            return None

        # Enviar mensaje al ESP32 para que lea una etiqueta
        await self.client.write_gatt_char(self.characteristic_uuid, b"LEER_ETIQUETA")
        print("[BLE] Enviando solicitud para leer etiqueta...")

        # Esperar a recibir los datos (esto depende del comportamiento del ESP32)
        await asyncio.sleep(2)  # Esperamos 2 segundos (ajustar según sea necesario)
        return None  # Aquí puedes devolver la etiqueta leída si el ESP32 la envía