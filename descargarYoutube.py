from pytube import YouTube
from tkinter import *
from tkinter import messagebox, simpledialog, filedialog
import re
import threading
import time
import tkinter.font as font

class DownloadApp:
    def __init__(self, master):
        self.master = master
        master.title("Descargar Música de YouTube - By JoseLu")
        master.geometry("507x200")
        master.resizable(False, False)

        self.urlEn = StringVar()
        self.urlEntrada = Entry(master, textvariable=self.urlEn, width=60)
        self.urlEntrada.grid(column=0, row=1, padx=10, pady=10)

        self.create_buttons()

        

    def create_buttons(self):
        obtener_mp3 = Button(self.master, text="Descargar MP3", font="Arial 10", width=15,
                             command=self.show_mp3_quality_options)
        obtener_mp4 = Button(self.master, text="Descargar MP4", font="Arial 10", width=15,
                             command=self.show_mp4_quality_options)
        close_button = Button(self.master, text="Cerrar", font="Arial 10", width=14, command=self.master.destroy)
        help_button = Button(self.master, text="Cómo descargo ?", font="Arial 10", width=14, command=self.show_help)

        obtener_mp3.grid(column=0, row=2)
        obtener_mp4.grid(column=0, row=3)
        help_button.grid(column=0, row=4)
        close_button.grid(column=0, row=5)

    def show_help(self):
        messagebox.showinfo("Ayuda", "Primero debes hacer clic derecho en el video que estás reproduciendo; luego hacer clic en COPIAR URL, y finalmente pegarlo en el cuadro de arriba. Para pegarlo presionar las teclas CTRL + V")

    def validate_url(self, url):
        url_pattern = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(url_pattern, url) is not None

    def download(self, formato, calidad, nombre_archivo, download_path):
        try:
            yt = YouTube(self.urlEn.get())
            if formato == "mp3":
                audio = yt.streams.filter(only_audio=True, abr=calidad).first()
                ext = "mp3"
                out_file = audio.download(filename=nombre_archivo + "." + ext, output_path=download_path)
            elif formato == "mp4":
                video = yt.streams.filter(res=calidad, file_extension='mp4').first()
                ext = "mp4"
                out_file = video.download(filename=nombre_archivo + "." + ext, output_path=download_path)

            messagebox.showinfo("Descarga completa", "Descarga exitosa.")
            self.progress_window.destroy()  # Cerrar la ventana de progreso después de la descarga exitosa
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def animate_downloading_label(self):
        text = "Descargando...  "
        text_length = len(text)
        window_width = text_length * 8  # Cada caracter ocupa aproximadamente 8 píxeles
        window_height = 50
        self.progress_window.geometry(f"{window_width}x{window_height}")

        while getattr(self.progress_label, "active", True):
            if not self.progress_window.winfo_exists():
                break  # Salir del bucle si la ventana de progreso ya no existe
            self.progress_label.config(text=text)
            self.master.update()
            time.sleep(0.5)
            text = text[1:] + text[0]  # Rotar el texto

    def show_mp3_quality_options(self):
        url = self.urlEn.get()
        if not url:
            messagebox.showinfo("Falta la URL", "Ingrese una URL para poder descargar.")
            return
        elif not self.validate_url(url):
            messagebox.showinfo("URL no válida", "La URL ingresada no es válida.")
            return

        try:
            yt = YouTube(url)
            streams = yt.streams.filter(only_audio=True)
            prompt = "Seleccione la calidad de audio:"

            # Eliminar la calidad no deseada
            available_qualities = sorted({stream.abr for stream in streams if stream.abr != '160kbps'}, reverse=True)

            if available_qualities:
                quality_window = Toplevel(self.master)
                quality_window.title("Calidad MP3")
                quality_window.geometry("300x270")
                quality_window.resizable(False, False)

                # Centrar la ventana en el monitor principal
                self.center_window(quality_window)

                quality_label = Label(quality_window, text=prompt)
                quality_label.pack()

                quality_listbox = Listbox(quality_window, selectmode="single")
                for quality in available_qualities:
                    quality_listbox.insert(END, quality)
                quality_listbox.pack()

                def download_selected_quality():
                    selected_index = quality_listbox.curselection()
                    if selected_index:
                        calidad_seleccionada = quality_listbox.get(selected_index[0])
                        quality_window.destroy()
                        yt = YouTube(self.urlEn.get())
                        title = yt.title
                        nombre_archivo = simpledialog.askstring("Nombre de archivo", "Ingrese el nombre de archivo (sin extensión):", parent=self.master, initialvalue=title)
                        if nombre_archivo:
                            download_path = filedialog.askdirectory()
                            if download_path:
                                self.progress_window = Toplevel(self.master)
                                self.progress_window.title("Descarga en progreso")
                                self.progress_label = Label(self.progress_window, text="")
                                self.progress_label.pack()
                                threading.Thread(target=self.animate_downloading_label).start()
                                threading.Thread(target=self.download, args=("mp3", calidad_seleccionada, nombre_archivo, download_path)).start()

                download_button = Button(quality_window, text="Descargar", command=download_selected_quality)
                download_button.pack(pady=8)  # Agrega espacio vertical antes del botón
                download_button.pack()
            else:
                messagebox.showinfo("No hay calidades disponibles", "No hay calidades de audio disponibles para descargar.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def center_window(self, window):
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        window.geometry("+{}+{}".format(x, y))

    def show_mp4_quality_options(self):
        url = self.urlEn.get()
        if not url:
            messagebox.showinfo("Falta la URL", "Ingrese una URL para poder descargar.")
            return
        elif not self.validate_url(url):
            messagebox.showinfo("URL no válida", "La URL ingresada no es válida.")
            return

        try:
            yt = YouTube(url)
            streams = yt.streams.filter(file_extension='mp4')
            prompt = "Seleccione la calidad de vídeo:"

            # Eliminar la calidad no deseada
            available_qualities = sorted({stream.resolution for stream in streams if stream.resolution is not None and '1080' not in stream.resolution},
                                         key=lambda x: int(x[:-1]) if x[:-1].isdigit() else x, reverse=True)

            if available_qualities:
                quality_window = Toplevel(self.master)
                quality_window.title("Calidad MP4")
                quality_window.geometry("300x270")
                quality_window.resizable(False, False)

                # Centrar la ventana en el monitor principal
                self.center_window(quality_window)

                quality_label = Label(quality_window, text=prompt)
                quality_label.pack()

                quality_listbox = Listbox(quality_window, selectmode="single")
                for quality in available_qualities:
                    quality_listbox.insert(END, quality)
                quality_listbox.pack()

                def download_selected_quality():
                    selected_index = quality_listbox.curselection()
                    if selected_index:
                        calidad_seleccionada = quality_listbox.get(selected_index[0])
                        quality_window.destroy()
                        yt = YouTube(self.urlEn.get())
                        title = yt.title
                        nombre_archivo = simpledialog.askstring("Nombre de archivo", "Ingrese el nombre de archivo (sin extensión):", parent=self.master, initialvalue=title)
                        if nombre_archivo:
                            download_path = filedialog.askdirectory()
                            if download_path:
                                self.progress_window = Toplevel(self.master)
                                self.progress_window.title("Descarga en progreso")
                                self.progress_label = Label(self.progress_window, text="")
                                self.progress_label.pack()
                                threading.Thread(target=self.animate_downloading_label).start()
                                threading.Thread(target=self.download, args=("mp4", calidad_seleccionada, nombre_archivo, download_path)).start()

                download_button = Button(quality_window, text="Descargar", command=download_selected_quality)
                download_button.pack(pady=8)  # Agregar espacio vertical antes del botón
                download_button.pack()
            else:
                messagebox.showinfo("No hay calidades disponibles", "No hay calidades de audio disponibles para descargar.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def main():
    root = Tk()
    app = DownloadApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()