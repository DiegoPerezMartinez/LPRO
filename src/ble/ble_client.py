"""Módulo para manejar la conexión BLE y recibir notificaciones."""
from bleak import BleakClient
import asyncio
import threading
from queue import Queue

class BLEHandler:
    """Clase para manejar la conexión BLE y recibir notificaciones."""
    def __init__(self, address, tx_uuid, rx_uuid, on_data_callback):
        self.address = address
        self.tx_uuid = tx_uuid
        self.rx_uuid = rx_uuid
        self.client = BleakClient(address)
        self.on_data_callback = on_data_callback
        self.notification_queue = Queue()

    async def connect(self):
        """Conecta al dispositivo BLE y comienza a recibir notificaciones."""
        await self.client.connect()
        print(f"[BLE] Conectado a {self.address}")
        await self.client.start_notify(self.tx_uuid, self.notification_handler)

    def notification_handler(self, sender, data):
        """Manejador de notificaciones. Se llama cuando se recibe una notificación."""
        decoded = data.decode("utf-8")
        print(f"[BLE] Recibido: {decoded}")
        self.on_data_callback(decoded)
        self.notification_queue.put(decoded)

    async def disconnect(self):
        """Desconecta del dispositivo BLE."""
        await self.client.stop_notify(self.tx_uuid)
        await self.client.disconnect()

    async def send_command(self, command: str):
        """Envía un comando al dispositivo BLE (como 'LEER_ETIQUETA')."""
        await self.client.write_gatt_char(self.rx_uuid, command.encode("utf-8"))
        print(f"[BLE] Enviado comando: {command}")


    def wait_for_response(self, timeout=30):
        """Esperar la respuesta con un tiempo de espera determinado."""
        try:
            print(f"[BLE] Esperando respuesta con timeout de {timeout} segundos...")
            # Intentar obtener el resultado de la cola dentro del tiempo límite (en segundos)
            return self.notification_queue.get(timeout=timeout)
        except Exception as e:
            print(f"[BLE] Error al recibir respuesta: {e}")
            return None