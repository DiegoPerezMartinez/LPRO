import flet as ft
from .dialog import open_add_dialog
from .monitoring import start_monitoring

class AppUI(ft.Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.objects_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.alert_text = ft.Text("", color="red", size=16, weight="bold")

        self.add_button = ft.ElevatedButton(
            "Añadir Objeto", 
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            on_click=lambda e: open_add_dialog(page, self.objects_list),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        self.start_button = ft.ElevatedButton(
            "Iniciar Monitoreo", 
            icon=ft.Icons.NOTIFICATIONS_ACTIVE,
            on_click=lambda e: start_monitoring(page, self.objects_list, self.alert_text),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        # 🔄 Botón para cambiar entre tema claro y oscuro
        self.theme_toggle = ft.IconButton(
            icon="dark_mode",
            selected_icon="light_mode",
            on_click=lambda e: self.toggle_theme(page, e.control.selected),
            style=ft.ButtonStyle(
            color={"": ft.Colors.BLACK, "selected": ft.Colors.WHITE},
            )
        )

        self.controls = [
            ft.Container(
                ft.Text("Objetos Vinculados", size=18, weight="bold"),
                padding=10,
                alignment=ft.alignment.center,
            ),
            self.objects_list,
            ft.Container(self.add_button, padding=10, alignment=ft.alignment.center),
            ft.Container(self.start_button, padding=10, alignment=ft.alignment.center),
            ft.Container(self.theme_toggle, padding=10, alignment=ft.alignment.center),  # Moved here
            ft.Container(self.alert_text, padding=10, alignment=ft.alignment.center),
        ]

    # 🔧 Corregida la indentación del método
    def toggle_theme(self, page, is_dark_mode):
        page.theme_mode = ft.ThemeMode.DARK if is_dark_mode else ft.ThemeMode.LIGHT
        page.update()
        self.theme_toggle.selected = not self.theme_toggle.selected
