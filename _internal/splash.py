# splash.py
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import colorsys
import sys
import os

def resource_path(relative_path):
    """Absolute path to resource, works for dev and PyInstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class SplashScreen(tk.Toplevel):
    def __init__(self, parent, gif_relative_path="kepek/loading.gif", img_size=(160,160), min_size=(320,220)):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(bg='white')

        # belső keret, hogy mindig legyen kontrasztos háttér és látható szegély
        self.frame = tk.Frame(self, bg='white', bd=2, relief='solid')
        self.frame.pack(padx=10, pady=10)
        self.frame.pack_propagate(False)  # ne hagyjuk, hogy a tartalom összezsugorítsa

        # GIF label (ha nincs gif, marad helyőrző)
        self.label = tk.Label(self.frame, bg='white')
        self.label.place(relx=0.5, rely=0.22, anchor="center")

        # Százalék és felirat
        self.percent_label = tk.Label(self.frame, text="0%", font=("Segoe UI", 14, "bold"),
                                      bg='white', fg="#333333")
        self.percent_label.place(relx=0.5, rely=0.62, anchor="center")

        self.text_label = tk.Label(self.frame, text="Betöltés...", font=("Segoe UI", 16, "bold"),
                                   bg='white', fg="#2a2a2a")
        self.text_label.place(relx=0.5, rely=0.74, anchor="center")

        # Progress bar canvas
        self.progress_canvas = tk.Canvas(self.frame, width=250, height=18, bg="#e0e0e0", highlightthickness=0)
        self.progress_canvas.place(relx=0.5, rely=0.86, anchor="center")

        # állapotok
        self.frames = []
        self.idx = 0
        self._after_id = None
        self.hue_shift = 0.0
        self.current_percent = 0
        self._running = True

        # GIF betöltése (PyInstaller kompatibilis útvonal)
        try:
            gif_path = resource_path(gif_relative_path)
            im = Image.open(gif_path)
            for frame in ImageSequence.Iterator(im):
                f = frame.convert("RGBA").resize(img_size, Image.Resampling.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(f))
        except Exception:
            # ha nincs GIF vagy hiba, akkor üres frames, nem dobunk kivételt
            self.frames = []

        # számoljuk ki a kívánt méretet (képpel vagy minimummal)
        min_w, min_h = min_size
        if self.frames:
            img_w, img_h = img_size
            content_w = max(min_w, img_w + 60)
            content_h = max(min_h, img_h + 120)
        else:
            content_w, content_h = min_w, min_h

        # beállítjuk a frame méretét és megjelenítjük
        self.frame.configure(width=content_w, height=content_h)

        # update majd középre pozícionálás
        self.update_idletasks()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws - content_w) // 2
        y = (hs - content_h) // 2
        self.geometry(f"{content_w}x{content_h}+{x}+{y}")
        self.resizable(False, False)

        # elindítjuk az animációt (saját after-ciklus)
        self._animate()

    def _animate(self):
        if not self.winfo_exists() or not getattr(self, "_running", True):
            return

        # GIF frame váltás
        if self.frames:
            try:
                self.label.config(image=self.frames[self.idx])
            except tk.TclError:
                return
            self.idx = (self.idx + 1) % len(self.frames)

        # progress vizuál frissítése
        self._animate_progress_color()

        # ütemezés
        try:
            self._after_id = self.after(60, self._animate)
        except tk.TclError:
            self._after_id = None

    def set_percentage(self, percent: int):
        """Thread-safe hívás: root.after(0, lambda: splash.set_percentage(x))"""
        self.current_percent = max(0, min(100, int(percent)))
        try:
            if self.percent_label.winfo_exists():
                self.percent_label.config(text=f"{self.current_percent}%")
        except tk.TclError:
            pass

    def _animate_progress_color(self):
        percent = getattr(self, 'current_percent', 0)
        self.progress_canvas.delete("bar")
        width = int(250 * percent / 100)
        radius = 8
        for i in range(width):
            t = i / 250
            hue = (self.hue_shift + t) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
            color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
            self.progress_canvas.create_line(i, 0, i, 18, fill=color, tags="bar")
        self.hue_shift = (self.hue_shift + 0.008) % 1.0

    def destroy(self):
        # leállítjuk az ütemezett after hívást, hogy ne fusson törölt ablakra
        self._running = False
        try:
            if self._after_id is not None:
                self.after_cancel(self._after_id)
        except Exception:
            pass
        try:
            super().destroy()
        except Exception:
            pass

def show_splash(root, gif_relative_path="kepek/loading.gif", duration_ms=0):
    """
    Létrehozza a SplashScreen objektumot és visszaadja.
    duration_ms: ha >0, akkor automatikusan bezáródik duration_ms múlva (root.after használva),
                 ha 0, akkor kézzel kell destroy()-al bezárni.
    """
    splash = SplashScreen(root, gif_relative_path)
    root.update()  # biztos, hogy megjelenjen
    if duration_ms and duration_ms > 0:
        def _close():
            if splash.winfo_exists():
                try:
                    splash.destroy()
                except Exception:
                    pass
        try:
            root.after(duration_ms, _close)
        except Exception:
            pass
    return splash