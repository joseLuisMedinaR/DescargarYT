import flet as ft
import re
import yt_dlp
import asyncio
import threading

def main(page: ft.Page):
    page.title = "Descargar Audios y Videos de YouTube"
    page.window.width = 500
    page.window.height = 450
    page.window.maximizable = False
    page.window.bgcolor = ft.colors.TRANSPARENT
    page.bgcolor = ft.colors.BLUE_500

    selected_folder = ft.Text()

    def on_folder_result(e: ft.FilePickerResultEvent):
        if e.path:
            selected_folder.value = e.path
            tb2.value = e.path  # Actualizar tb2 con la ruta seleccionada
            page.update()

    file_picker = ft.FilePicker(on_result=on_folder_result)
    page.overlay.append(file_picker)

    async def mostrar_snackbar(mensaje, duration=4000):
        snackbar = ft.SnackBar(ft.Text(mensaje), duration=duration)
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()
        await asyncio.sleep(duration / 1000)
        snackbar.open = False
        page.update()

    def run_async(coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            asyncio.create_task(coro)
        else:
            asyncio.run(coro)

    def obtener_mp3(e):
        url = tb1.value
        if not url:
            run_async(mostrar_snackbar("Ingrese una URL para poder descargar el audio."))
            return
        elif not validate_url(url):
            run_async(mostrar_snackbar("La URL ingresada no es válida."))
            return
        if not selected_folder.value:
            run_async(mostrar_snackbar("Seleccione una carpeta de descarga."))
            return
        threading.Thread(target=lambda: run_async(descargar_mp3(url))).start()

    def obtener_mp4(e):
        url = tb1.value
        if not url:
            run_async(mostrar_snackbar("Ingrese una URL para poder descargar el video."))
            return
        elif not validate_url(url):
            run_async(mostrar_snackbar("La URL ingresada no es válida."))
            return
        if not selected_folder.value:
            run_async(mostrar_snackbar("Seleccione una carpeta de descarga."))
            return
        threading.Thread(target=lambda: run_async(descargar_mp4(url))).start()

    def close_dlg_help(e):
        dlg_modal_help.open = False
        page.update()

    dlg_modal_help = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cómo descargo ?"),
        content=ft.Text(
            """1 - Hacer clic derecho en el video que estás reproduciendo.
2- Hacer clic en COPIAR URL, y finalmente pegarlo en el cuadro de arriba que dice Enlace.
(Para pegarlo presionar las teclas CTRL + V o clic con el botón derecho sobre el cuadro de texto y elegir pegar.)
3- Presionar el botón que dice Seleccionar la Carpeta de Descarga y elegir la ruta para guardar el archivo.
4- Elegir Descargar MP3 o Descargar MP4 según lo que se quiera hacer.
"""
        ),
        actions=[
            ft.TextButton("Cerrar Ayuda", on_click=close_dlg_help),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        #on_dismiss=lambda e: print("Decidió no salir de la aplicación."),
    )

    async def open_dlg_modal_help(e):
        #page.dialog = dlg_modal_help
        page.overlay.append(dlg_modal_help)
        dlg_modal_help.open = True
        page.update()

    def close(e):
        page.window.close()

    def close_dlg(e):
        dlg_modal.open = False
        page.update()

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirme por favor"),
        content=ft.Text("Realmente desea salir de la aplicación ?"),
        actions=[
            ft.TextButton("Si", on_click=close),
            ft.TextButton("No", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        #on_dismiss=lambda e: print("Decidió no salir de la aplicación."),
    )

    def open_dlg_modal_close(e):
        #page.dialog = dlg_modal
        page.overlay.append(dlg_modal)
        dlg_modal.open = True
        page.update()

    tb1 = ft.TextField(label="Enlace", hint_text="Pegar el enlace aquí")
    page.add(tb1)

    tb2 = ft.TextField(label="Ruta de Descarga", hint_text="Ruta de Descarga", read_only=True)
    page.add(tb2)

    page.add(
        ft.Row(
            [
                ft.FilledButton(
                    text="Seleccionar la Carpeta de Descarga",
                    icon="FOLDER_OPEN",
                    width=200,
                    tooltip="Seleccionar la Carpeta de Descarga",
                    on_click=lambda _: file_picker.get_directory_path(),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

    page.add(
        ft.Row(
            [
                ft.FilledButton(
                    text="Descargar MP3",
                    icon="QUEUE_MUSIC_SHARP",
                    width=200,
                    tooltip="Descargar música",
                    on_click=obtener_mp3,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )
    page.add(
        ft.Row(
            [
                ft.FilledButton(
                    text="Descargar MP4",
                    icon="MUSIC_VIDEO",
                    width=200,
                    tooltip="Descargar Video",
                    on_click=obtener_mp4,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )
    page.add(
        ft.Row(
            [
                ft.FilledButton(
                    text="Cómo descargo ?",
                    icon="HELP_ROUNDED",
                    width=200,
                    tooltip="Ayuda explicativa",
                    on_click=open_dlg_modal_help,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )
    page.add(
        ft.Row(
            [
                ft.ElevatedButton(
                    text="Cerrar",
                    icon="EXIT_TO_APP",
                    width=200,
                    tooltip="Cerrar aplicación",
                    on_click=open_dlg_modal_close,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

    #tb2 = ft.TextField(label="Ruta de Descarga", hint_text="Ruta de Descarga", read_only=True)
    #page.add(tb2)

    class MyLogger:
        def debug(self, msg):
            if msg.startswith('[debug] '):
                pass
            else:
                self.info(msg)

        def info(self, msg):
            run_async(mostrar_snackbar(msg))

        def warning(self, msg):
            run_async(mostrar_snackbar(f"Advertencia: {msg}"))

        def error(self, msg):
            run_async(mostrar_snackbar(f"Error: {msg}"))

    async def my_hook(d):
        if d['status'] == 'finished':
            await mostrar_snackbar('Descarga completada, procesando ...', duration=2000)
            await mostrar_snackbar('Descarga Finalizada')
        elif d['status'] == 'downloading':
            progress = d.get('_percent_str', '0%')
            await mostrar_snackbar(f"Progreso: {progress}")

    async def descargar_mp3(url):
        try:
            await mostrar_snackbar("Descarga en proceso, espere un momento por favor ...")
            ydl_opts = {
                'format': 'm4a/bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
                'outtmpl': f'{selected_folder.value}/%(title)s.%(ext)s',
                'logger': MyLogger(),
                'progress_hooks': [my_hook],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            await mostrar_snackbar("Se completó el proceso de descarga.")
        except Exception as e:
            await mostrar_snackbar(str(e))

    async def descargar_mp4(url):
        try:
            await mostrar_snackbar("Descarga en proceso, espere un momento por favor ...")
            ydl_opts = {
                'format': "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b",
                'outtmpl': f'{selected_folder.value}/%(title)s.%(ext)s',
                'logger': MyLogger(),
                'progress_hooks': [my_hook],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            await mostrar_snackbar(str(e))

    def validate_url(url):
        url_pattern = re.compile(
            r"^(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+",
            re.IGNORECASE,
        )
        return re.match(url_pattern, url) is not None

ft.app(target=main)
