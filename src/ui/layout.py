"""Module to define the main layout of the app."""
import asyncio
import flet as ft
from database import load_objects
from .dialog import open_add_dialog
from .objects import add_object


class AppUI(ft.Column):
    """Class to define the main layout of the app."""

    def __init__(self, page, ble_handler):
        super().__init__()
        self.page = page
        self.ble_handler = ble_handler
        self.current_mode = "BUS"
        self.objects_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.alert_text = ft.Text("", color="red", size=16, weight="bold")

        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = ft.Colors.BLACK
        self.add_button = ft.ElevatedButton(
            "Añadir Objeto", 
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            on_click=lambda e: open_add_dialog(page, self.objects_list, self.ble_handler),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )


        # 🔄 Botón para cambiar entre tema claro y oscuro
        self.theme_toggle = ft.IconButton(
            icon="dark_mode",
            selected_icon="light_mode",
            on_click=lambda e: self.toggle_theme(page),
            style=ft.ButtonStyle(
            color={"": ft.Colors.BLACK, "selected": ft.Colors.WHITE},
            ),
            selected=page.theme_mode == ft.ThemeMode.DARK
        )

        self.mode_toggle = ft.ElevatedButton(
            "Cambiar a modo Seguimiento", 
            icon=ft.Icons.SWAP_HORIZ,
            on_click=lambda e: self.toggle_mode(),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        self.load_objects_from_db()

        self.controls = [
            ft.Container(
                ft.Text("Objetos Vinculados", size=18, weight="bold"),
                padding=10,
                alignment=ft.alignment.center,
            ),
            self.objects_list,
            ft.Container(self.add_button,
                          padding=10,
                          alignment=ft.alignment.center),
            ft.Container(self.mode_toggle,
                         padding=10,
                         alignment=ft.alignment.center),
            ft.Container(self.theme_toggle,
                         padding=10,
                         alignment=ft.alignment.center),
            ft.Container(self.alert_text,
                         padding=10,
                         alignment=ft.alignment.center),
        ]

    def toggle_theme(self, page):
        """Toggle between light and dark theme."""
        is_dark_mode = page.theme_mode != ft.ThemeMode.DARK
        page.theme_mode = ft.ThemeMode.DARK if is_dark_mode else ft.ThemeMode.LIGHT
        self.theme_toggle.selected = is_dark_mode
        bg_color = ft.Colors.BLACK if is_dark_mode else ft.Colors.WHITE
        page.bgcolor = bg_color
        page.update()

    def load_objects_from_db(self):
        """Carga los objetos desde MongoDB al iniciar la app"""
        saved_objects = load_objects()
        for obj in saved_objects:
            add_object(self.page,
                       self.objects_list,
                       obj["name"],
                       obj["uuid"],
                       obj["is_active"],
                       self.ble_handler)

    def send_active_tags_to_esp32(self):
        """Envía todos los UUID activos al ESP32 vía BLE"""
        async def send():
            if not self.ble_handler.client.is_connected:
                print("[BLE] No conectado, intentando conectar...")
                await self.ble_handler.connect()  # Asegura conexión y descubrimiento

            all_objects = load_objects()
            active_uuids = [obj["uuid"] for obj in all_objects if obj["is_active"]]

            for uuid in active_uuids:
                command = f"ADD:{uuid.upper()}"
                print(f"[BLE] Enviando UUID activo: {command}")
                await self.ble_handler.send_command(command)
                await asyncio.sleep(0.1)  # Pequeña pausa entre comandos

        self.page.run_task(send)

    def toggle_mode(self):
        """Alterna entre modos Búsqueda y Seguimiento y envía el comando por BLE."""
        async def send_mode_command():
            if not self.ble_handler.client.is_connected:
                print("[BLE] No conectado, intentando conectar...")
                await self.ble_handler.connect()

            # Cambiar el modo actual
            self.current_mode = "SEG" if self.current_mode == "BUS" else "BUS"
            command = f"MODE:{self.current_mode}"
            print(f"[BLE] Enviando comando: {command}")
            await self.ble_handler.send_command(command)

            # Actualizar el texto del botón
            if self.current_mode == "BUS":
                self.mode_toggle.text = "Cambiar a modo Seguimiento"
            else:
                self.mode_toggle.text = "Cambiar a modo Búsqueda"

            self.page.update()

        self.page.run_task(send_mode_command)
