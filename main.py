import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from yt_dlp import YoutubeDL


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("650x550")
        self.root.resizable(False, False)

        # Configurar el evento de tecla Enter
        self.root.bind('<Return>', self.handle_enter_key)

        # Variables
        self.downloading = False
        self.paused = False
        self.cancelled = False
        self.process = None
        self.current_stage = ""
        self.formats = []
        self.selected_format = None
        self.current_focused_button = None
        # Nueva variable para control de listas
        self.playlist_mode = False
        self.current_download_index = 0
        self.total_downloads = 0

        # GUI Elements
        self.create_widgets()

    def handle_enter_key(self, event):
        if self.current_focused_button and self.current_focused_button['state'] == tk.NORMAL:
            self.current_focused_button.invoke()

    def track_focus(self, widget):
        def focus_in(event):
            self.current_focused_button = widget

        widget.bind('<FocusIn>', focus_in)

    def create_widgets(self):
        # Main container frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # URL Section
        url_frame = tk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 5))  # Reducir padding

        # Añadir checkbox para modo lista
        self.playlist_check = tk.Checkbutton(url_frame, text="Es lista de reproducción",
                                             command=self.toggle_playlist_mode)
        self.playlist_check.pack(anchor=tk.W, pady=(0, 5))

        # Frame para opciones de lista (inicialmente oculto)
        self.playlist_options_frame = tk.Frame(url_frame)

        tk.Label(self.playlist_options_frame, text="Rango de videos (ej. 1-5):").pack(side=tk.LEFT)
        self.playlist_range_entry = tk.Entry(self.playlist_options_frame, width=15)
        self.playlist_range_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(url_frame, text="YouTube URL:").pack(anchor=tk.W)
        self.url_entry = tk.Entry(url_frame)
        self.url_entry.pack(fill=tk.X, pady=(0, 5))
        self.url_entry.focus_set()

        # Download Location Section
        location_frame = tk.Frame(main_frame)
        location_frame.pack(fill=tk.X, pady=(0, 5))  # Reducir padding

        tk.Label(location_frame, text="Download Location:").pack(anchor=tk.W)

        loc_entry_frame = tk.Frame(location_frame)
        loc_entry_frame.pack(fill=tk.X)

        self.location_entry = tk.Entry(loc_entry_frame)
        self.location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.location_entry.insert(0, os.path.expanduser("~\\Downloads"))

        self.browse_btn = tk.Button(loc_entry_frame, text="Browse", command=self.browse_location, width=10)
        self.browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        self.track_focus(self.browse_btn)

        # Quality Selection Section - Ajustar altura máxima
        self.quality_frame = tk.Frame(main_frame)
        self.quality_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))  # Reducir padding y permitir expansión

        tk.Label(self.quality_frame, text="Available Formats:").pack(anchor=tk.W)

        # Configurar el Treeview con altura fija
        self.format_tree = ttk.Treeview(self.quality_frame, columns=('resolution', 'fps', 'ext', 'size'),
                                        show='headings', height=6)  # Altura reducida a 6 filas
        self.format_tree.pack(fill=tk.BOTH, expand=True)

        self.format_tree.heading('resolution', text='Resolution')
        self.format_tree.heading('fps', text='FPS')
        self.format_tree.heading('ext', text='Type')
        self.format_tree.heading('size', text='Size')

        self.format_tree.column('resolution', width=120)
        self.format_tree.column('fps', width=60)
        self.format_tree.column('ext', width=60)
        self.format_tree.column('size', width=80)

        # Progress Section - Reducir padding
        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 5))

        self.stage_label = tk.Label(progress_frame, text="", fg="blue")
        self.stage_label.pack(anchor=tk.W)

        self.progress_label = tk.Label(progress_frame, text="Ready")
        self.progress_label.pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        # Console Section - Reducir altura
        console_frame = tk.Frame(main_frame)
        console_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        tk.Label(console_frame, text="Download Log:").pack(anchor=tk.W)

        self.console = tk.Text(console_frame, height=4, state='disabled')  # Altura reducida a 4 líneas
        self.console.pack(fill=tk.BOTH, expand=True)

        # Button Frame - Asegurar que esté en la parte inferior
        button_frame = tk.Frame(self.root, height=40)
        button_frame.pack_propagate(False)  # Esto evita que el frame cambie de tamaño
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

        # Botones con un poco más de espacio entre ellos
        self.fetch_btn = tk.Button(button_frame, text="Get Formats", command=self.fetch_formats, width=12)
        self.fetch_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.download_btn = tk.Button(button_frame, text="Download", command=self.start_download, width=12,
                                      state=tk.DISABLED)
        self.download_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.pause_btn = tk.Button(button_frame, text="Pause", command=self.toggle_pause, width=12, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5, expand=True)

        self.cancel_btn = tk.Button(button_frame, text="Cancel", command=self.cancel_download, width=12,
                                    state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5, expand=True)

        # Make sure the button frame stays at the bottom
        button_frame.pack_propagate(False)
        button_frame.config(height=40)

    def toggle_playlist_mode(self):
        self.playlist_mode = not self.playlist_mode
        if self.playlist_mode:
            self.playlist_options_frame.pack(fill=tk.X, pady=(0, 5))
        else:
            self.playlist_options_frame.pack_forget()

    def browse_location(self):
        directory = filedialog.askdirectory()
        if directory:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, directory)

    def log_to_console(self, message):
        self.console.config(state='normal')
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.console.config(state='disabled')

    def fetch_formats(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        if self.playlist_mode:
            self.log_to_console(f"Fetching playlist information: {url}")
        else:
            self.log_to_console(f"Fetching available formats for: {url}")

        self.fetch_btn.config(state=tk.DISABLED)
        self.download_btn.config(state=tk.DISABLED)

        for item in self.format_tree.get_children():
            self.format_tree.delete(item)

        fetch_thread = threading.Thread(target=self._fetch_formats_thread, args=(url,), daemon=True)
        fetch_thread.start()

    def _fetch_formats_thread(self, url):
        try:
            with YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)

                if self.playlist_mode:
                    if 'entries' not in info:
                        raise Exception("This doesn't appear to be a playlist")

                    playlist_range = self.playlist_range_entry.get().strip()
                    entries = info['entries']

                    if playlist_range:
                        try:
                            start, end = map(int, playlist_range.split('-'))
                            entries = entries[start - 1:end]
                        except:
                            raise Exception("Invalid range format. Use like: 1-5")

                    if not entries:
                        raise Exception("No videos found in the specified range")

                    # Obtener el primer video que tenga información válida
                    first_video = None
                    for entry in entries:
                        if entry and 'formats' in entry:
                            first_video = entry
                            break

                    if not first_video:
                        raise Exception("No valid videos found in playlist")

                    self.root.after(0, lambda: self.log_to_console(
                        f"Playlist detected with {len(entries)} videos. Showing formats for first available video."))

                    # Guardar información de la lista para la descarga
                    self.playlist_info = {
                        'entries': entries,
                        'total': len(entries)
                    }

                    # Mostrar formatos del primer video
                    formats = []
                    for f in first_video['formats']:
                        has_video = f.get('vcodec') != 'none'
                        has_audio = f.get('acodec') != 'none'

                        if has_video or has_audio:
                            resolution = f.get('resolution', 'unknown')
                            if resolution == 'unknown' and has_video:
                                resolution = f"{f.get('width', '?')}x{f.get('height', '?')}"
                            elif not has_video:
                                resolution = "Audio Only"

                            formats.append({
                                'id': f['format_id'],
                                'resolution': resolution,
                                'fps': f.get('fps', 0) or 0,
                                'ext': f.get('ext', 'unknown'),
                                'filesize': f.get('filesize', 0) or 0,
                                'format_note': f.get('format_note', ''),
                                'vcodec': f.get('vcodec', 'none'),
                                'acodec': f.get('acodec', 'none'),
                                'has_video': has_video,
                                'has_audio': has_audio
                            })
                else:
                    # Procesamiento normal para video individual
                    if 'formats' not in info:
                        raise Exception("No formats found for this video")

                    formats = []
                    for f in info['formats']:
                        has_video = f.get('vcodec') != 'none'
                        has_audio = f.get('acodec') != 'none'

                        if has_video or has_audio:
                            resolution = f.get('resolution', 'unknown')
                            if resolution == 'unknown' and has_video:
                                resolution = f"{f.get('width', '?')}x{f.get('height', '?')}"
                            elif not has_video:
                                resolution = "Audio Only"

                            formats.append({
                                'id': f['format_id'],
                                'resolution': resolution,
                                'fps': f.get('fps', 0) or 0,
                                'ext': f.get('ext', 'unknown'),
                                'filesize': f.get('filesize', 0) or 0,
                                'format_note': f.get('format_note', ''),
                                'vcodec': f.get('vcodec', 'none'),
                                'acodec': f.get('acodec', 'none'),
                                'has_video': has_video,
                                'has_audio': has_audio
                            })

                # Ordenar formatos (común para ambos modos)
                def sort_key(x):
                    if not x['has_video']:  # Audio only al final
                        return (1, 0, 0, 0)

                    try:
                        res_height = int(x['resolution'].split('x')[1]) if 'x' in x['resolution'] else 0
                    except:
                        res_height = 0

                    return (
                        0,  # Videos primero
                        -res_height,  # Mayor resolución primero
                        -x['fps'],  # Mayor FPS primero
                        -x['filesize']  # Mayor tamaño primero
                    )

                formats.sort(key=sort_key)

                self.root.after(0, self._display_formats, formats)
                self.root.after(0, lambda: self.log_to_console(f"Found {len(formats)} available formats"))

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Error", f"Failed to fetch formats: {msg}"))
            self.root.after(0, lambda msg=error_msg: self.log_to_console(f"Error fetching formats: {msg}"))
        finally:
            self.root.after(0, lambda: self.fetch_btn.config(state=tk.NORMAL))

    def _display_formats(self, formats):
        self.formats = formats

        # Limpiar el Treeview primero
        for item in self.format_tree.get_children():
            self.format_tree.delete(item)

        # Mostrar todos los formatos
        for f in formats:
            resolution = f['resolution']
            fps = f['fps'] if f['has_video'] else ''  # Mostrar FPS solo para video
            ext = f['ext']

            # Calcular tamaño
            size_str = "unknown"
            if f['filesize'] > 0:
                size_mb = round(f['filesize'] / (1024 * 1024), 2)
                size_str = f"{size_mb} MB"

            # Mostrar tipo en la columna de resolución
            if not f['has_video']:
                resolution = "Audio Only"

            # Insertar en el Treeview
            self.format_tree.insert('', 'end',
                                    values=(resolution, fps, ext, size_str),
                                    tags=('video' if f['has_video'] else 'audio'))

        # Configurar estilo para diferenciar video/audio
        self.format_tree.tag_configure('video', background='#f0f0ff')
        self.format_tree.tag_configure('audio', background='#fff0f0')

        # Habilitar selección
        self.format_tree.bind('<<TreeviewSelect>>', self._on_format_select)

    def _on_format_select(self, event):
        selected_item = self.format_tree.selection()
        if selected_item:
            index = self.format_tree.index(selected_item[0])
            self.selected_format = self.formats[index]
            self.download_btn.config(state=tk.NORMAL)
            self.log_to_console(f"Selected format: {self.selected_format['resolution']} {self.selected_format['ext']}")
            self.download_btn.focus_set()

    def start_download(self):
        if not self.selected_format:
            messagebox.showerror("Error", "Please select a format first")
            return

        location = self.location_entry.get()
        if not os.path.isdir(location):
            messagebox.showerror("Error", "Invalid download location")
            return

        self.downloading = True
        self.paused = False
        self.cancelled = False

        if self.playlist_mode:
            self.current_download_index = 0
            self.total_downloads = self.playlist_info['total']
            self.log_to_console(f"Starting download of {self.total_downloads} videos...")

        self.fetch_btn.config(state=tk.DISABLED)
        self.download_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.NORMAL)

        self.progress_label.config(text="Preparing download...")
        self.progress_bar["value"] = 0

        download_thread = threading.Thread(target=self.download_video_or_playlist, daemon=True)
        download_thread.start()
        self.pause_btn.focus_set()

    # Nuevo método para manejar descarga de listas
    def download_video_or_playlist(self):
        if self.playlist_mode:
            for i, entry in enumerate(self.playlist_info['entries']):
                if self.cancelled:
                    break

                if not entry:  # Saltar entradas vacías
                    continue

                self.current_download_index = i + 1
                self.root.after(0, lambda: self.log_to_console(
                    f"\nDownloading video {self.current_download_index} of {self.total_downloads}"))

                # Obtener la URL del video de la entrada de la lista
                video_url = entry.get('webpage_url') or entry.get('url')
                if not video_url:
                    self.root.after(0, lambda: self.log_to_console(
                        f"Skipping video {self.current_download_index} - no URL found"))
                    continue

                # Descargar el video actual
                self.download_video(self.selected_format['id'], video_url)
        else:
            self.download_video(self.selected_format['id'])

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            self.pause_btn.config(text="Pause")
            self.log_to_console("Download resumed")
            self.progress_label.config(text=f"{self.current_stage} - Resumed")
        else:
            self.paused = True
            self.pause_btn.config(text="Resume")
            self.log_to_console("Download paused")
            self.progress_label.config(text=f"{self.current_stage} - Paused")

    def cancel_download(self):
        self.cancelled = True
        if self.process:
            self.process.terminate()
        self.reset_ui()
        self.log_to_console("Download cancelled by user")
        self.progress_label.config(text="Download cancelled")
        self.fetch_btn.focus_set()

    def reset_ui(self):
        self.downloading = False
        self.paused = False
        self.cancelled = False

        self.fetch_btn.config(state=tk.NORMAL)
        self.download_btn.config(state=tk.NORMAL if self.selected_format else tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)
        self.pause_btn.config(text="Pause")

    def download_video(self, format_id, url=None):
        if url is None:
            url = self.url_entry.get()

        location = self.location_entry.get()
        selected_format = next((f for f in self.formats if f['id'] == format_id), None)

        if not selected_format:
            self.root.after(0, lambda: messagebox.showerror("Error", "Selected format not found"))
            return

        # Configurar formato para descarga
        if selected_format['has_video'] and selected_format['has_audio']:
            # Formato ya tiene video+audio
            format_spec = format_id
        elif selected_format['has_video']:
            # Solo video - combinar con mejor audio
            format_spec = f"{format_id}+bestaudio"
        else:
            # Solo audio
            format_spec = format_id

        ydl_opts = {
            'format': format_spec,
            'outtmpl': os.path.join(location, '%(title)s.%(ext)s'),
            'progress_hooks': [self.update_progress_hook],
            'noprogress': True,
            'quiet': True,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                self.process = ydl
                info_dict = ydl.extract_info(url, download=False)
                video_title = info_dict.get('title', 'video')
                self.root.after(0, lambda: self.log_to_console(f"Downloading: {video_title}"))

                # Mostrar información sobre lo que se está descargando
                if selected_format['has_video'] and not selected_format['has_audio']:
                    self.root.after(0, lambda: self.log_to_console(
                        f"Downloading video ({selected_format['resolution']}) and combining with best audio"))
                elif selected_format['has_audio'] and not selected_format['has_video']:
                    self.root.after(0, lambda: self.log_to_console("Downloading audio only"))
                else:
                    self.root.after(0, lambda: self.log_to_console(
                        f"Downloading: {selected_format['resolution']} (with audio)"))

                ydl.download([url])

                if not self.cancelled:
                    self.root.after(0, self.update_progress_complete)
                    self.root.after(0, lambda: self.log_to_console("Download completed successfully!"))
        except Exception as e:
            if not self.cancelled:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
                self.root.after(0, lambda: self.log_to_console(f"Error: {str(e)}"))
        finally:
            self.root.after(0, self.reset_ui)
            self.process = None

    def update_progress_hook(self, d):
        if self.cancelled:
            raise Exception("Download cancelled")

        while self.paused and not self.cancelled:
            pass

        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)

            if total_bytes and downloaded_bytes:
                percent = min(100, (downloaded_bytes / total_bytes) * 100)
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')

                if '_percent_str' in d:
                    stage = "Merging streams"
                    percent = float(d['_percent_str'].strip('%'))
                else:
                    if 'video' in d.get('info_dict', {}).get('format_id', ''):
                        stage = "Downloading video"
                    elif 'audio' in d.get('info_dict', {}).get('format_id', ''):
                        stage = "Downloading audio"
                    else:
                        stage = "Downloading"

                # Añadir información de progreso de lista si es aplicable
                if self.playlist_mode:
                    stage = f"Video {self.current_download_index}/{self.total_downloads} - {stage}"
                    overall_percent = ((self.current_download_index - 1) / self.total_downloads) * 100 + (
                                percent / self.total_downloads)
                    self.root.after(0, lambda: self.update_progress(overall_percent, speed, eta, stage))
                else:
                    self.root.after(0, lambda: self.update_progress(percent, speed, eta, stage))

                self.root.after(0, lambda: self.log_to_console(
                    f"{stage}: {percent:.1f}% | Speed: {speed} | ETA: {eta}"))

        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.update_progress(100, "0B/s", "00:00", "Finalizing"))
            self.root.after(0, lambda: self.log_to_console("Finalizing video file..."))

    def update_progress(self, percent, speed, eta, stage):
        self.progress_bar["value"] = percent
        self.progress_label.config(text=f"{speed} - ETA: {eta}")
        self.stage_label.config(text=stage)
        self.current_stage = stage

    def update_progress_complete(self):
        self.progress_label.config(text="Download complete!")
        self.progress_bar["value"] = 100
        self.stage_label.config(text="Completed", fg="green")


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()