import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import threading
import re
import os
import sys
import subprocess
import platform

# ---------------------------
# Ruta de recursos (para PyInstaller)
# ---------------------------

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ---------------------------
# Configuración yt-dlp
# ---------------------------

YDL_BASE = {
    "js_runtimes": {"node": {}},
    "remote_components": ["ejs:github"]
}

# ---------------------------
# Ventana principal
# ---------------------------

root = tk.Tk()
root.title("Descargar MP3 y MP4")
root.geometry("500x640")
root.resizable(False, False)
root.configure(bg="#f0f0f0")  # Fondo más claro y moderno

# Estilo para ttk
style = ttk.Style()
style.theme_use('clam')

# Configuración de estilos personalizados
style.configure("TProgressbar", 
                thickness=25, 
                troughcolor='#E0E0E0', 
                background='#4CAF50', 
                bordercolor='#f0f0f0', 
                lightcolor='#4CAF50', 
                darkcolor='#4CAF50')

style.configure("Custom.TButton", 
                padding=10, 
                font=("Arial", 10, "bold"))

style.configure("Action.TButton", 
                background="#2196F3", 
                foreground="white", 
                font=("Arial", 10, "bold"))

style.map("Action.TButton",
          background=[('active', '#1976D2')])

# icono
icon_path = resource_path("assets/icon.png")
try:
    root.iconphoto(True, tk.PhotoImage(file=icon_path))
except:
    pass

selected_folder = ""
last_downloaded_file = ""

# ---------------------------
# Abrir archivos/carpetas
# ---------------------------

def open_path(path):
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "No se encontró el archivo o carpeta")
        return
        
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir: {str(e)}")

def abrir_carpeta_descarga():
    if selected_folder:
        open_path(selected_folder)

def abrir_archivo_descargado():
    if last_downloaded_file:
        open_path(last_downloaded_file)

# ---------------------------
# Progress Hook
# ---------------------------

def progress_hook(d):
    if d['status'] == 'downloading':
        try:
            p_raw = d.get('_percent_str', '0%').strip()
            # Limpiar caracteres de control ANSI que a veces añade yt-dlp
            p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p_raw).replace('%', '')
            val = float(p_clean)
            
            root.after(0, lambda v=val: progress_bar.config(value=v))
            
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            status_text = f"Descargando: {val:.1f}% | {speed} | ETA: {eta}"
            root.after(0, lambda t=status_text: label_status.config(text=t, fg="#2E7D32"))
            root.update_idletasks() # Forzar actualización de la UI
        except Exception as e:
            print(f"Error en progress_hook: {e}")
            pass
    elif d['status'] == 'finished':
        root.after(0, lambda: progress_bar.config(value=100))
        root.after(0, lambda: label_status.config(text="Procesando archivo... Espere por favor", fg="#1976D2"))
        root.update_idletasks()

# ---------------------------
# Sanitizar nombre
# ---------------------------

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*\[\]]+', '', filename)

# ---------------------------
# Seleccionar carpeta
# ---------------------------

def seleccionar_carpeta():
    global selected_folder

    folder = filedialog.askdirectory()

    if folder:
        selected_folder = folder
        tb2.config(state="normal")
        tb2.delete(0, tk.END)
        tb2.insert(0, folder)
        tb2.config(state="readonly")

# ---------------------------
# Obtener nombre del video
# ---------------------------

def obtener_nombre(url):
    try:

        ydl_opts = {
            **YDL_BASE,
            "quiet": True,
            "skip_download": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return sanitize_filename(info["title"])

    except Exception as e:
        root.after(0, lambda err=e: messagebox.showerror("Error", str(err)))
        return None

# ---------------------------
# Descargar MP3
# ---------------------------

def descargar_mp3():

    url = tb1.get().strip()

    if not url:
        messagebox.showwarning("Aviso", "Ingrese una URL")
        return

    if not selected_folder:
        messagebox.showwarning("Aviso", "Seleccione una carpeta de descarga")
        return

    threading.Thread(target=descargar_mp3_thread, args=(url,), daemon=True).start()


def descargar_mp3_thread(url):
    global last_downloaded_file

    try:
        bitrate = combo_audio_quality.get()
        title = obtener_nombre(url)

        if not title:
            return

        root.after(0, lambda: actualizar_nombre(f"{title}.mp3"))
        root.after(0, lambda: progress_bar.config(value=0))
        root.after(0, lambda: btn_open_folder.config(state="disabled"))
        root.after(0, lambda: btn_open_file.config(state="disabled"))

        salida = os.path.join(selected_folder, f"{title}.%(ext)s")

        ydl_opts = {
            **YDL_BASE,
            "format": "bestaudio/best",
            "outtmpl": salida,
            "progress_hooks": [progress_hook],
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": bitrate
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        last_downloaded_file = os.path.join(selected_folder, f"{title}.mp3")
        root.after(0, lambda: label_status.config(text="Completado!"))
        root.after(0, lambda: btn_open_folder.config(state="normal"))
        root.after(0, lambda: btn_open_file.config(state="normal"))
        root.after(0, lambda: messagebox.showinfo("OK", f"Descarga MP3 ({bitrate}k) finalizada"))

    except Exception as e:
        root.after(0, lambda err=e: messagebox.showerror("Error", str(err)))

# ---------------------------
# Descargar MP4
# ---------------------------

def descargar_mp4():

    url = tb1.get().strip()

    if not url:
        messagebox.showwarning("Aviso", "Ingrese una URL")
        return

    if not selected_folder:
        messagebox.showwarning("Aviso", "Seleccione una carpeta de descarga")
        return

    threading.Thread(target=descargar_mp4_thread, args=(url,), daemon=True).start()


def descargar_mp4_thread(url):
    global last_downloaded_file

    try:
        height = combo_video_quality.get().replace("p", "")
        title = obtener_nombre(url)

        if not title:
            return

        root.after(0, lambda: actualizar_nombre(f"{title}.mp4"))
        root.after(0, lambda: progress_bar.config(value=0))
        root.after(0, lambda: btn_open_folder.config(state="disabled"))
        root.after(0, lambda: btn_open_file.config(state="disabled"))

        salida = os.path.join(selected_folder, f"{title}.%(ext)s")

        # Formato mejorado para asegurar audio y video
        # 'bv*[height<=?height]+ba/b[height<=?height] / bv*+ba/b'
        format_str = f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best[ext=mp4]/best"

        ydl_opts = {
            **YDL_BASE,
            "format": format_str,
            "outtmpl": salida,
            "merge_output_format": "mp4",
            "progress_hooks": [progress_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        last_downloaded_file = os.path.join(selected_folder, f"{title}.mp4")
        root.after(0, lambda: label_status.config(text="Completado!"))
        root.after(0, lambda: btn_open_folder.config(state="normal"))
        root.after(0, lambda: btn_open_file.config(state="normal"))
        root.after(0, lambda: messagebox.showinfo("OK", f"Descarga MP4 ({height}p) finalizada"))

    except Exception as e:
        root.after(0, lambda err=e: messagebox.showerror("Error", str(err)))

# ---------------------------
# Actualizar nombre
# ---------------------------

def actualizar_nombre(nombre):
    tb3.config(state="normal")
    tb3.delete(0, tk.END)
    tb3.insert(0, nombre)
    tb3.config(state="readonly")

# ---------------------------
# Ayuda
# ---------------------------

def mostrar_ayuda():

    texto = """1 - Hacer clic derecho en el video.
2 - Copiar URL del video.

3 - Pegar la URL en el campo ENLACE DEL VIDEO.

4 - Seleccionar la carpeta donde se guardará el archivo.

5 - Elegir la calidad deseada para video o audio.

6 - Elegir Descargar MP3 o Descargar MP4.

IMPORTANTE:
No cerrar el programa hasta finalizar la descarga.
La barra de progreso te indicará el estado actual.
"""

    messagebox.showinfo("Cómo descargar", texto)

# ---------------------------
# Labels + Campos
# ---------------------------

label1 = tk.Label(root, text="Enlace del Video", bg="#f0f0f0", fg="#333333", font=("Arial", 11, "bold"))
label1.pack(pady=(20,0))

tb1 = tk.Entry(root, width=55, font=("Arial", 10), bd=2, relief="flat")
tb1.pack(pady=5, ipady=3)

label2 = tk.Label(root, text="Carpeta de Descarga", bg="#f0f0f0", fg="#333333", font=("Arial", 11, "bold"))
label2.pack(pady=(15,0))

# Frame para carpeta y botón de selección
frame_folder = tk.Frame(root, bg="#f0f0f0")
frame_folder.pack(pady=5)

tb2 = tk.Entry(frame_folder, width=40, state="readonly", font=("Arial", 9), bd=2, relief="flat")
tb2.grid(row=0, column=0, padx=(0, 5), ipady=3)

btn_folder = tk.Button(
    frame_folder,
    text="📁 Explorar",
    command=seleccionar_carpeta,
    bg="#607D8B",
    fg="white",
    font=("Arial", 9, "bold"),
    bd=0,
    padx=10,
    cursor="hand2"
)
btn_folder.grid(row=0, column=1)

label3 = tk.Label(root, text="Nombre del Archivo", bg="#f0f0f0", fg="#333333", font=("Arial", 11, "bold"))
label3.pack(pady=(15,0))

tb3 = tk.Entry(root, width=55, state="readonly", font=("Arial", 9), bd=2, relief="flat")
tb3.pack(pady=5, ipady=3)

# ---------------------------
# Selección de Calidad
# ---------------------------

frame_quality = tk.LabelFrame(root, text=" Opciones de Calidad ", bg="#f0f0f0", fg="#333333", font=("Arial", 10, "bold"), padx=10, pady=10)
frame_quality.pack(pady=15, padx=20, fill="x")

# Calidad Video
label_video_q = tk.Label(frame_quality, text="🎬 Video (MP4):", bg="#f0f0f0", fg="#555555", font=("Arial", 9, "bold"))
label_video_q.grid(row=0, column=0, padx=5, sticky="w")

combo_video_quality = ttk.Combobox(frame_quality, values=["1080p", "720p", "480p", "360p"], width=15, state="readonly")
combo_video_quality.set("720p")
combo_video_quality.grid(row=0, column=1, padx=20, pady=5)

# Calidad Audio
label_audio_q = tk.Label(frame_quality, text="🎵 Audio (MP3):", bg="#f0f0f0", fg="#555555", font=("Arial", 9, "bold"))
label_audio_q.grid(row=1, column=0, padx=5, sticky="w")

combo_audio_quality = ttk.Combobox(frame_quality, values=["320", "256", "192", "128"], width=15, state="readonly")
combo_audio_quality.set("192")
combo_audio_quality.grid(row=1, column=1, padx=20, pady=5)

# ---------------------------
# Progreso
# ---------------------------

label_status = tk.Label(root, text="Listo para descargar", bg="#f0f0f0", fg="#666666", font=("Arial", 9, "italic"))
label_status.pack(pady=(10,0))

progress_bar = ttk.Progressbar(root, orient="horizontal", length=420, mode="determinate", style="TProgressbar")
progress_bar.pack(pady=(5, 10))

# ---------------------------
# Botones Post-Descarga
# ---------------------------

frame_post_download = tk.Frame(root, bg="#f0f0f0")
frame_post_download.pack(pady=5)

btn_open_folder = tk.Button(
    frame_post_download,
    text="📂 Abrir Carpeta",
    command=abrir_carpeta_descarga,
    bg="#8BC34A",
    fg="white",
    font=("Arial", 9, "bold"),
    bd=0,
    padx=10,
    pady=5,
    state="disabled",
    cursor="hand2"
)
btn_open_folder.grid(row=0, column=0, padx=10)

btn_open_file = tk.Button(
    frame_post_download,
    text="📄 Abrir Archivo",
    command=abrir_archivo_descargado,
    bg="#CDDC39",
    fg="#333333",
    font=("Arial", 9, "bold"),
    bd=0,
    padx=10,
    pady=5,
    state="disabled",
    cursor="hand2"
)
btn_open_file.grid(row=0, column=1, padx=10)

# ---------------------------
# Botones de Acción
# ---------------------------

frame_actions = tk.Frame(root, bg="#f0f0f0")
frame_actions.pack(pady=5)

btn_mp3 = tk.Button(
    frame_actions,
    text="🎵 Descargar MP3",
    width=20,
    command=descargar_mp3,
    bg="#E91E63",
    fg="white",
    font=("Arial", 10, "bold"),
    bd=0,
    pady=8,
    cursor="hand2"
)
btn_mp3.grid(row=0, column=0, padx=10)

btn_mp4 = tk.Button(
    frame_actions,
    text="🎬 Descargar MP4",
    width=20,
    command=descargar_mp4,
    bg="#2196F3",
    fg="white",
    font=("Arial", 10, "bold"),
    bd=0,
    pady=8,
    cursor="hand2"
)
btn_mp4.grid(row=0, column=1, padx=10)

# Botones secundarios
frame_secondary = tk.Frame(root, bg="#f0f0f0")
frame_secondary.pack(pady=20)

btn_help = tk.Button(
    frame_secondary,
    text="❓ Ayuda",
    width=15,
    command=mostrar_ayuda,
    bg="#9E9E9E",
    fg="white",
    font=("Arial", 9, "bold"),
    bd=0,
    pady=5,
    cursor="hand2"
)
btn_help.grid(row=0, column=0, padx=10)

btn_exit = tk.Button(
    frame_secondary,
    text="❌ Salir",
    width=15,
    command=root.destroy,
    bg="#f44336",
    fg="white",
    font=("Arial", 9, "bold"),
    bd=0,
    pady=5,
    cursor="hand2"
)
btn_exit.grid(row=0, column=1, padx=10)

# ---------------------------
# Ejecutar app
# ---------------------------

root.mainloop()