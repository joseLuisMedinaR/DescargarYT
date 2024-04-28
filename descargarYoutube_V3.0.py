import flet as ft
from pytube import YouTube
import re
from tkinter import messagebox, simpledialog, filedialog
from tkinter import *

def main(page: ft.Page):
    page.title = "Descargar Audios y Videos de YouTube"
    page.window_width = 500
    page.window_height = 450
    page.window_maximizable = False
    page.window_bgcolor = ft.colors.TRANSPARENT
    page.bgcolor = ft.colors.BLUE_500

    def obtener_mp3(e):
        url = tb1.value
        if not url:
            mostrar_snackbar("Ingrese una URL para poder descargar el audio.")
            return
        elif not validate_url(url):
            mostrar_snackbar("La URL ingresada no es válida.")
            return
        show_quality_options(url, "mp3")

    def obtener_mp4(e):
        url = tb1.value
        if not url:
            mostrar_snackbar("Ingrese una URL para poder descargar el video.")
            return
        elif not validate_url(url):
            mostrar_snackbar("La URL ingresada no es válida.")
            return
        show_quality_options(url, "mp4")

    def close_dlg_help(e):
        dlg_modal_help.open = False
        page.update()

    dlg_modal_help = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cómo descargo ?"),
        content=ft.Text(
            "Primero debes hacer clic derecho en el video que estás reproduciendo; luego hacer clic en COPIAR URL, y finalmente pegarlo en el cuadro de arriba. Para pegarlo presionar las teclas CTRL + V o clic con el botón derecho sobre el cuadro de texto."
        ),
        actions=[
            ft.TextButton("Cerrar Ayuda", on_click=close_dlg_help),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Decidió no salir de la aplicación."),
    )

    def open_dlg_modal_help(e):
        page.dialog = dlg_modal_help
        dlg_modal_help.open = True
        page.update()

    def close(e):
            page.window_close()

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
        on_dismiss=lambda e: print("Decidió no salir de la aplicación."),
    )

    def open_dlg_modal_close(e):
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    def mostrar_snackbar(mensaje):        
        page.snack_bar = ft.SnackBar(ft.Text(mensaje))
        page.snack_bar.open = True
        page.snack_bar.duration = 5000        
        page.update()

    t = ft.Text()
    tb1 = ft.TextField(label="Enlace", hint_text="Pegar el enlace aquí")
    page.add(tb1, t)

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

    def show_quality_options(url, format):
        try:
            page.snack_bar = ft.SnackBar(ft.Text(f"Estamos buscando las distintas calidades de descarga. Aguarde por favor ..."))
            page.snack_bar.open = True
            page.snack_bar.duration = 15000
            page.update()
            
            yt = YouTube(url)
            if format == "mp3":
                streams = yt.streams.filter(only_audio=True)
                prompt = "Seleccione la calidad de audio:"
            else:
                streams = yt.streams.filter(file_extension='mp4')
                prompt = "Seleccione la calidad de vídeo:"

            if format =="mp3":
                available_qualities = sorted({stream.abr for stream in streams},
                                             key=lambda x: int(x[:-1]) if x[:-1].isdigit() else x, reverse=True)
            else:
                available_qualities = sorted(
                    {stream.resolution for stream in streams if stream.resolution is not None},
                    key=lambda x: int(x[:-1]) if x[:-1].isdigit() else x, reverse=True
                )

            if available_qualities:
                actions = [
                    ft.CupertinoActionSheetAction(
                        content=ft.Text(quality),
                        on_click=lambda e, quality=quality: show_download_dialog(url, format, quality),                        
                    )
                    for quality in available_qualities
                ]
                action_sheet = ft.CupertinoActionSheet(
                    title=ft.Text("Seleccione la calidad"), actions=actions,
                )
                bs = ft.BottomSheet(
                    ft.Container(action_sheet), on_dismiss=lambda e: None
                )
                page.show_bottom_sheet(bs)                
            else:
                mostrar_snackbar("No hay calidades disponibles para descargar.")
        except Exception as e:
            mostrar_snackbar(str(e))    

    def show_download_dialog(url, format, quality):
        page.close_bottom_sheet()  
        def button_clicked(e):
            t.value = download_video(url, format, quality,tb1.value)
            page.remove(tb1, b)
            page.update()

        #t = ft.Text()
        yt = YouTube(url)
        tb1 = ft.TextField(label="Nombre de Archivo", value=yt.author + " - " + yt.title, hint_text="nombre de archivo")
        b = ft.ElevatedButton(text="Continuar", on_click=button_clicked)
        page.add(tb1, b)        

    def download_video(url, format, quality, filename):
        page.snack_bar = ft.SnackBar(ft.Text(f"Abriendo explorador de archivos para que elijas dónde guardar la descarga."))
        page.snack_bar.open = True
        page.snack_bar.duration = 20000
        page.update()
        try:
            yt = YouTube(url)
            if format == "mp3":
                audio = yt.streams.filter(only_audio=True, abr=quality)
                ext = "mp3"
            else:
                video = yt.streams.filter(res=quality, file_extension="mp4")
                ext = "mp4"

            nombre_archivo = filename
            
            if nombre_archivo:                
                download_path = filedialog.askdirectory()
                if download_path:
                    download_thread(url, format, ext, nombre_archivo, download_path, quality)
        except Exception as e:
            mostrar_snackbar(str(e))

    def download_thread(url, format, ext, nombre_archivo, download_path, quality):
        # mostrar_snackbar("Descarga en proceso, espere un momento por favor ...")
        page.snack_bar = ft.SnackBar(ft.Text(f"Descarga en proceso, espere un momento por favor ..."))
        page.snack_bar.open = True
        page.snack_bar.duration = 60000
        page.update()
        try:
            yt = YouTube(url)
            if format == "mp3":
                    audio = yt.streams.filter(only_audio=True, abr=quality).first()
                    if audio:
                        out_file = audio.download(filename=nombre_archivo + ".mp3", output_path=download_path)
            else:
                    video = yt.streams.filter(file_extension="mp4", res=quality).first()
                    if video:
                        out_file = video.download(
                            filename=nombre_archivo + "." + ext, output_path=download_path
                        ) 
                        # Descargar audio simultáneamente si la calidad de video es superior a 720p
                        if int(quality[:-1]) > 720:
                            audio_quality = "128kbps"  # Calidad de audio por defecto si 128 kbps no está disponible
                            audio_streams = yt.streams.filter(only_audio=True, abr=audio_quality)
                            if audio_streams:
                                audio_stream = audio_streams.first()
                                audio_out_file = audio_stream.download(filename=nombre_archivo + ".mp3", output_path=download_path)
            mostrar_snackbar("Se completó el proceso de descarga.")
        except Exception as e:
            mostrar_snackbar(str(e))


    def validate_url(url):        
        url_pattern = re.compile(
            r"^(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}$",
            re.IGNORECASE,
        )
        return re.match(url_pattern, url) is not None

ft.app(target=main)