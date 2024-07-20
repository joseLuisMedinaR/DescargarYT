import flet as ft
import re
import yt_dlp
import asyncio
import threading

# Función principal de la aplicación
def main(page: ft.Page):
    # Configuración inicial de la ventana
    page.title = "Descargar MP3 y MP4"
    page.window.width = 500
    page.window.height = 500
    page.window.maximizable = False
    page.window.bgcolor = ft.colors.TRANSPARENT
    page.bgcolor = ft.colors.BLUE_500

    selected_folder = ft.Text()

    # Función que se ejecuta cuando se selecciona una carpeta de descarga
    def on_folder_result(e: ft.FilePickerResultEvent):
        if e.path:
            selected_folder.value = e.path
            tb2.value = e.path  # Actualizar tb2 con la ruta seleccionada
            page.update()

    file_picker = ft.FilePicker(on_result=on_folder_result)
    page.overlay.append(file_picker)

    # Función asincrónica para mostrar un mensaje temporal (snackbar)
    async def mostrar_snackbar(mensaje, duration=6000):
        snackbar = ft.SnackBar(ft.Text(mensaje), duration=duration)
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()
        await asyncio.sleep(duration / 1000)
        snackbar.open = False
        page.update()

    # Función para ejecutar corutinas de forma asincrónica
    def run_async(coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            asyncio.create_task(coro)
        else:
            asyncio.run(coro)

    # Función para iniciar la descarga de un archivo MP3
    def obtener_mp3(e):
        url = tb1.value
        if not url:
            run_async(mostrar_snackbar("Ingrese una URL para poder descargar el audio."))
            return
        #elif not validate_url(url):
        #    run_async(mostrar_snackbar("La URL ingresada no es válida."))
        #    return
        if not selected_folder.value:
            run_async(mostrar_snackbar("Seleccione una carpeta de descarga."))
            return
        threading.Thread(target=lambda: run_async(descargar_mp3(url))).start()

    # Función para iniciar la descarga de un archivo MP4
    def obtener_mp4(e):
        url = tb1.value
        if not url:
            run_async(mostrar_snackbar("Ingrese una URL para poder descargar el video."))
            return
        #elif not validate_url(url):
        #    run_async(mostrar_snackbar("La URL ingresada no es válida."))
        #    return
        if not selected_folder.value:
            run_async(mostrar_snackbar("Seleccione una carpeta de descarga."))
            return
        threading.Thread(target=lambda: run_async(descargar_mp4(url))).start()

    # Función para cerrar el diálogo de ayuda
    def close_dlg_help(e):
        dlg_modal_help.open = False
        page.update()

    # Diálogo modal de ayuda
    dlg_modal_help = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cómo descargo ?"),
        content=ft.Text(
            """1 - Hacer clic derecho en el video que estás reproduciendo.
2- Hacer clic en COPIAR URL, y finalmente pegarlo en el cuadro de arriba que dice Enlace.
(Para pegarlo presionar las teclas CTRL + V o clic con el botón derecho sobre el cuadro de texto y elegir pegar.)
3- Presionar el botón que dice Seleccionar la Carpeta de Descarga y elegir la ruta para guardar el archivo.
4- Elegir Descargar MP3 o Descargar MP4 según lo que se quiera hacer.

IMPORTANTE: No cerrar el programa hasta ver el archivo en la carpeta seleccionada.
"""
        ),
        actions=[
            ft.TextButton("Cerrar Ayuda", on_click=close_dlg_help),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Función asincrónica para abrir el diálogo de ayuda
    async def open_dlg_modal_help(e):
        page.overlay.append(dlg_modal_help)
        dlg_modal_help.open = True
        page.update()

    # Función para cerrar la aplicación
    def close(e):
        page.window.close()

    # Función para cerrar el diálogo de confirmación de cierre
    def close_dlg(e):
        dlg_modal.open = False
        page.update()

    # Diálogo modal de confirmación de cierre
    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirme por favor"),
        content=ft.Text("Realmente desea salir de la aplicación ?"),
        actions=[
            ft.TextButton("Si", on_click=close),
            ft.TextButton("No", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Función para abrir el diálogo de confirmación de cierre
    def open_dlg_modal_close(e):
        page.overlay.append(dlg_modal)
        dlg_modal.open = True
        page.update()

    # Campo de texto para la URL
    tb1 = ft.TextField(label="Enlace", hint_text="Pegar el enlace aquí")
    page.add(tb1)

    # Campo de texto para la ruta de descarga, solo lectura
    tb2 = ft.TextField(label="Ruta de Descarga", hint_text="Ruta de Descarga", read_only=True)
    page.add(tb2)

    # Campo para saber el nombre del archivo
    tb3 = ft.TextField(label="Nombre de Archivo", hint_text=".................", read_only=True)
    page.add(tb3)

    # Botón para seleccionar la carpeta de descarga
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

    # Botón para descargar MP3
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

    # Botón para descargar MP4
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

    # Botón para mostrar el diálogo de ayuda
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

    # Botón para cerrar la aplicación
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

    # Clase para manejar los mensajes de log de yt-dlp
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

    # Función para manejar el progreso de la descarga
    async def my_hook(d):
        if d['status'] == 'finished':
            await mostrar_snackbar('Descarga completada, procesando ...', duration=2000)
            await mostrar_snackbar('Descarga Finalizada')
        elif d['status'] == 'downloading':
            progress = d.get('_percent_str', '0%')
            await mostrar_snackbar(f"Progreso: {progress}")

    # Función para sanitizar el nombre de los archivos
    def sanitize_filename(filename):
        return re.sub(r'[<>:"/\\|?*\[\]]+', '', filename)

    # Función asincrónica para descargar MP3
    async def descargar_mp3(url):
        try:
            await mostrar_snackbar("Descarga en proceso, espere un momento por favor ...")
            ydl_opts = {
                'format': 'm4a/bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
                'outtmpl': f'{selected_folder.value}/%(title)s.%(ext)s',
                'logger': MyLogger(),
                'progress_hooks': [lambda d: run_async(my_hook(d))],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                title = sanitize_filename(info_dict['title'])
                ydl_opts['outtmpl'] = f'{selected_folder.value}/{title}.%(ext)s'
                # Mostramos el nombre del archivo a descargar
                tb3.value = f'{title}.mp3'  # Actualizar tb3 con el nombre del archivo
                page.update()
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            await mostrar_snackbar("Se completó el proceso de descarga.")
        except Exception as e:
            await mostrar_snackbar(str(e))

    # Función asincrónica para descargar MP4
    async def descargar_mp4(url):
        try:
            await mostrar_snackbar("Descarga en proceso, espere un momento por favor ...")
            ydl_opts = {
                'format': "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b",
                'outtmpl': f'{selected_folder.value}/%(title)s.%(ext)s',
                'logger': MyLogger(),
                'progress_hooks': [lambda d: run_async(my_hook(d))],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                title = sanitize_filename(info_dict['title'])
                ydl_opts['outtmpl'] = f'{selected_folder.value}/{title}.%(ext)s'
                # Mostramos el nombre del archivo a descargar
                tb3.value = f'{title}.mp4'  # Actualizar tb3 con el nombre del archivo
                page.update()
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            await mostrar_snackbar("Se completó el proceso de descarga.")
        except Exception as e:
            await mostrar_snackbar(str(e))

    # No vamos a controlar que sea una dirección de YouTube ya que se puede descargar cualquier video de internet
    #def validate_url(url):
    #    url_pattern = re.compile(
    #        r"^(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+",
    #        re.IGNORECASE,
    #    )
    #    return re.match(url_pattern, url) is not None

# Iniciamos la aplicación
ft.app(target=main)