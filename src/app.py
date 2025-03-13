import flet as ft
import bluetooth

def main(page: ft.Page):
    page.title = "Conexión Bluetooth"
    page.add(ft.Text("Dispositivos Bluetooth"))

    def buscar_dispositivos(e):
        dispositivos = bluetooth.discover_devices(lookup_names=True)
        lista_dispositivos.controls.clear()
        for addr, name in dispositivos:
            lista_dispositivos.controls.append(ft.ListTile(
                title=ft.Text(f"{name} - {addr}"),
                on_click=lambda e, addr=addr: obtener_servicios(addr)
            ))
        page.update()

    def obtener_servicios(addr):
        try:
            servicios = bluetooth.find_service(address=addr)
            if servicios:
                for svc in servicios:
                    if svc["protocol"] == "RFCOMM":
                        conectar_dispositivo(addr, svc["port"])
                        return
            page.add(ft.Text(f"No se encontraron servicios RFCOMM en {addr}"))
        except Exception as ex:
            page.add(ft.Text(f"Error al obtener servicios de {addr}: {ex}"))

    def conectar_dispositivo(addr, port):
        try:
            page.add(ft.Text(f"Intentando conectar a {addr} en el puerto {port}..."))
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            page.add(ft.Text("Socket inicializado correctamente."))
            sock.connect((addr, port))
            page.add(ft.Text(f"Conectado a {addr} en el puerto {port}"))
            sock.send("Hola desde Python")
            page.add(ft.Text(f"Mensaje enviado a {addr}"))
            sock.close()
            page.add(ft.Text(f"Conexión cerrada con {addr}"))
        except bluetooth.btcommon.BluetoothError as bt_err:
            page.add(ft.Text(f"Error Bluetooth al conectar a {addr}: {bt_err}"))
            # Intentar con puerto alternativo
            try:
                alt_port = 3  # Puerto alternativo
                page.add(ft.Text(f"Intentando puerto alternativo {alt_port}..."))
                sock.connect((addr, alt_port))
                page.add(ft.Text(f"Conectado a {addr} en el puerto alternativo {alt_port}"))
                sock.send("Hola desde Python (Puerto alternativo)")
                page.add(ft.Text(f"Mensaje enviado a {addr} desde el puerto alternativo"))
                sock.close()
                page.add(ft.Text(f"Conexión cerrada con {addr} desde el puerto alternativo"))
            except Exception as ex_alt:
                page.add(ft.Text(f"Error al conectar a {addr} en el puerto alternativo: {ex_alt}"))
        except Exception as ex:
            page.add(ft.Text(f"Error general al conectar a {addr}: {ex}"))

    btn_buscar = ft.ElevatedButton(text="Buscar dispositivos", on_click=buscar_dispositivos)
    lista_dispositivos = ft.ListView()

    page.add(btn_buscar)
    page.add(lista_dispositivos)

ft.app(target=main)
