import os
import tkinter as tk
from tkinter import messagebox
from ldap_auth import ldap_authenticate
from config_ini import BEJELENTKEZETT_FELHASZNALO  # globális változó a felhasználóhoz

# Alapértelmezett betűméret login ablakhoz
ALAP_BETUMERET = 12

def show_login_window(root):
    username_result = {"username": None, "password": None}

    login_window = tk.Toplevel(root)
    login_window.title("Bejelentkezés")

    # Minimum méretek
    min_szelesseg = 350
    min_magassag = 280

    # Ablak mérete alapértelmezett betűméret alapján
    ablak_szelesseg = max(int(ALAP_BETUMERET * 15), min_szelesseg)
    ablak_magassag = max(int(ALAP_BETUMERET * 12), min_magassag)

    # Képernyő mérete
    ws = login_window.winfo_screenwidth()
    hs = login_window.winfo_screenheight()

    # Pozíció középre
    x = (ws // 2) - (ablak_szelesseg // 2)
    y = (hs // 2) - (ablak_magassag // 2)
    login_window.geometry(f"{ablak_szelesseg}x{ablak_magassag}+{x}+{y}")

    # Ikon beállítása
    ico_path = os.path.join(os.path.dirname(__file__), "vihar.ico")
    try:
        login_window.iconbitmap(ico_path)
    except Exception as e:
        print(f"Nem sikerült ikon beállítása: {e}")

    login_window.grab_set()
    font_def = ('Segoe UI', ALAP_BETUMERET)

    tk.Label(login_window, text="Felhasználónév:", font=font_def).pack(pady=(10, 0))
    username_entry = tk.Entry(login_window, font=font_def)
    username_entry.pack()

    tk.Label(login_window, text="Jelszó:", font=font_def).pack(pady=(10, 0))
    password_entry = tk.Entry(login_window, show="*", font=font_def)
    password_entry.pack()

    # Ha az X gombot nyomja meg a felhasználó
    def on_close():
        username_result["username"] = None
        username_result["password"] = None
        login_window.destroy()
        
    login_window.protocol("WM_DELETE_WINDOW", on_close)

    def custom_message(title, message, icon_path):
        win = tk.Toplevel(login_window)
        win.title(title)
        win.geometry("300x200")
        win.iconbitmap(icon_path)
        win.transient(login_window)
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (300 // 2)
        y = (win.winfo_screenheight() // 2) - (200 // 2)
        win.geometry(f"+{x}+{y}")
        label = tk.Label(win, text=message, wraplength=280, font=font_def)
        label.pack(pady=20)
        btn = tk.Button(win, text="TOVÁBB", command=win.destroy, font=font_def)
        btn.pack(pady=10)
        try:
            win.grab_set()
        except tk.TclError:
            pass
        win.wait_window()

    # --- LOGIN függvény globális felhasználóval ---
    def login():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Hiányzó adatok", "Kérlek, add meg a felhasználónevet és jelszót.")
            return

        if ldap_authenticate(username, password):
            # Globális felhasználó beállítása sikeres login után
            global BEJELENTKEZETT_FELHASZNALO
            BEJELENTKEZETT_FELHASZNALO = username

            custom_message("Sikeres belépés", f"Üdvözlünk, {username}!", ico_path)
            username_result["username"] = username
            username_result["password"] = password
            login_window.grab_release()
            login_window.destroy()
        else:
            custom_message("Sikertelen belépés", "Hibás felhasználónév vagy jelszó.", ico_path)

    tk.Button(login_window, text="Bejelentkezés", command=login, font=font_def).pack(pady=20)

    root.wait_window(login_window)

    return username_result["username"], username_result["password"]