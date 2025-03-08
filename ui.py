import flet as ft

class AppUI(ft.Column):
    def __init__(self, page, backend):
        super().__init__()
        self.page = page
        self.backend = backend
        self.objects_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.alert_text = ft.Text("", color="red", size=16, weight="bold")

        # Botón para añadir objetos
        self.add_button = ft.ElevatedButton(
            "Añadir Objeto",
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            on_click=self.open_add_dialog,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        # Botón para iniciar monitoreo
        self.start_button = ft.ElevatedButton(
            "Iniciar Monitoreo",
            icon=ft.Icons.NOTIFICATIONS_ACTIVE,
            on_click=self.start_monitoring,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        )

        # Cuadro de diálogo (se crea vacío aquí para evitar errores)
        self.dialog = None

        # Layout principal
        self.controls = [
            ft.Container(
                ft.Text("Objetos Vinculados", size=18, weight="bold"),
                padding=10,
                alignment=ft.alignment.center,
            ),
            self.objects_list,
            ft.Container(self.add_button, padding=10, alignment=ft.alignment.center),
            ft.Container(self.start_button, padding=10, alignment=ft.alignment.center),
            ft.Container(self.alert_text, padding=10, alignment=ft.alignment.center),
        ]

    def open_add_dialog(self, e):
        print("🟢 Botón de 'Añadir Objeto' presionado")

        try:
            name_input = ft.TextField(label="Nombre del objeto", autofocus=True)
            range_dropdown = ft.Dropdown(
                label="Alcance (m)",
                options=[ft.dropdown.Option("1"), ft.dropdown.Option("3"), ft.dropdown.Option("5"), ft.dropdown.Option("10")],
            )

            def add_object(e):
                print("🟢 Confirmar objeto")
                name = name_input.value.strip()
                range_val = range_dropdown.value

                if not name or not range_val:
                    print("⚠ Falta nombre o alcance")
                    name_input.error_text = "⚠ Nombre y alcance requeridos"
                    self.page.update()
                    return

                print(f"✅ Añadiendo {name} con alcance {range_val}m")
                self.add_object(name, range_val)
                self.page.close(self.dialog)  # Cerrar el diálogo
                self.page.update()

            # Crear diálogo
            self.dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Añadir nuevo objeto"),
                content=ft.Column([name_input, range_dropdown], spacing=10),
                actions=[ft.TextButton("Añadir", on_click=add_object)],
            )

            # Asignar y abrir el diálogo
            self.page.dialog = self.dialog
            self.page.open(self.dialog)  # <- Aquí es donde realmente se muestra
            print("🟢 Diálogo debería estar visible ahora")

        except Exception as ex:
            print(f"❌ ERROR al abrir diálogo: {ex}")



    def add_object(self, name, range_val):
        """Añadir un objeto a la lista con botón de activación y eliminación"""
        
        # Estado inicial del objeto
        is_active = True  
        status_text = ft.Text(f"Estado: {'Activado' if is_active else 'Desactivado'}")

        # Función para manejar el cambio de estado
        def toggle_active(e):
            nonlocal is_active
            is_active = e.control.value  # Guardar el nuevo estado
            status_text.value = f"Estado: {'Activado' if is_active else 'Desactivado'}"
            self.page.update()  # Forzar actualización de la interfaz
            print(f"🔄 Estado de {name}: {status_text.value}")

        toggle_button = ft.Switch(
            value=is_active,
            on_change=toggle_active
        )

        card = ft.Card(
            content=ft.Container(
                ft.Row(
                    [
                        ft.Icon(ft.icons.RADIO_BUTTON_CHECKED, color=ft.colors.BLUE),
                        ft.Text(f"{name} (Alcance: {range_val}m)", size=16),
                        status_text,  # Texto que muestra el estado
                        toggle_button,
                        ft.IconButton(ft.icons.DELETE, on_click=lambda _: self.remove_object(card)),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=10,
            )
        )

        self.objects_list.controls.append(card)
        self.page.update()



    def remove_object(self, card):
        """Eliminar objeto de la lista"""
        self.objects_list.controls.remove(card)
        self.page.update()

    def start_monitoring(self, e):
        """Verifica SOLO los objetos activados antes de mostrar alertas"""

        active_objects = []

        # Recorremos la lista de objetos en la UI
        for card in self.objects_list.controls:
            if isinstance(card, ft.Card) and isinstance(card.content, ft.Container):
                row = card.content.content  # Aquí está el ft.Row con los elementos dentro
                if isinstance(row, ft.Row):
                    object_name = row.controls[1].value  # Nombre del objeto
                    toggle_button = row.controls[2]  # El Switch de activación
                    
                    if isinstance(toggle_button, ft.Switch):
                        print(f"🔍 {object_name}: {'Activado' if toggle_button.value else 'Desactivado'}")
                        
                        if toggle_button.value:  # Si el switch está activado
                            active_objects.append(object_name)

        # Depuración: imprimir los objetos activados
        print(f"✅ Objetos ACTIVADOS: {active_objects}")

        if not active_objects:
            self.alert_text.value = "⚠ No hay objetos ACTIVADOS para monitorear."
            self.page.update()
            return

        # Simulación del backend con los objetos activados
        lost_object = self.backend.check_objects()
        print(f"🚨 Objeto perdido detectado por backend: {lost_object}")

        if lost_object and lost_object in active_objects:
            self.alert_text.value = f"🚨 ¡Alerta! {lost_object} se ha alejado"
        else:
            self.alert_text.value = "✅ Todos los objetos activados están en rango"

        self.page.update()
