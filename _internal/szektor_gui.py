import os
import pymysql
import tkinter as tk
from tkinter import ttk, messagebox
from config import DB_CONFIG
from config_ini import betolt_beallitas  # betűméret beállításhoz

class SzektorGUI:
    def __init__(self, root):
        # Betűméret betöltése
        _, _, betumeret = betolt_beallitas()
        self.font_def = ('Segoe UI', betumeret)

        # Dinamikus ablakméret
        ablak_szelesseg = max(int(betumeret * 37), 700)
        ablak_magassag = max(int(betumeret * 25), 500)

        self.root = tk.Toplevel(root)
        self.root.title("Szektorlista kezelése")
        self.root.geometry(f"{ablak_szelesseg}x{ablak_magassag}")
        # Menü betűméret globális beállítása erre az ablakra:
        self.root.option_add('*Menu.font', self.font_def)
        # Ikon beállítása
        self.ico_path = os.path.join(os.path.dirname(__file__), "vihar.ico")
        try:
            self.root.iconbitmap(self.ico_path)
        except Exception as e:
            print(f"Nem sikerült ikon beállítása: {e}")

        self.setup_menu()
        self.setup_widgets()
        self.load_szektorok()

    # --- Egyedi üzenetablak vihar.ico ikonnal ---
    def custom_message(self, title, message):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.iconbitmap(self.ico_path)

        # Méret és középre helyezés
        win.geometry("300x200")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text=message, font=self.font_def, wraplength=280).pack(pady=20)
        tk.Button(win, text="OK", command=win.destroy, font=self.font_def).pack(pady=10)

        win.wait_window()

    # --- Menü ---
    def setup_menu(self):
        menubar = tk.Menu(self.root, font=self.font_def)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0, font=self.font_def)
        file_menu.add_command(label="Kilépés", command=self.root.destroy)
        menubar.add_cascade(label="Fájl", menu=file_menu)

        segitseg_menu = tk.Menu(menubar, tearoff=0, font=self.font_def)
        segitseg_menu.add_command(
            label="Névjegy",
            command=lambda: self.custom_message("Névjegy", "Szektorlista kezelő modul\nVerzió 1.2")
        )
        menubar.add_cascade(label="Súgó", menu=segitseg_menu)

    # --- Widgetek (lista + mezők + gombok) ---
    def setup_widgets(self):
        # TreeView
        self.tree = ttk.Treeview(self.root, columns=("Szektor", "Csoport"), show="headings")
        self.tree.heading("Szektor", text="Szektor")
        self.tree.heading("Csoport", text="Szektorcsoport")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Beviteli mezők
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Label(frame, text="Szektor:", font=self.font_def).grid(row=0, column=0)
        self.entry_szektor = tk.Entry(frame, width=30, font=self.font_def)
        self.entry_szektor.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Szektorcsoport:", font=self.font_def).grid(row=0, column=2)
        self.entry_csoport = tk.Entry(frame, width=20, font=self.font_def)
        self.entry_csoport.grid(row=0, column=3, padx=5)

        # Gombok keret
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=int(self.font_def[1] * 0.5))

        # Dinamikus méretezés
        padx = int(self.font_def[1] * 0.4)
        pady = int(self.font_def[1] * 0.3)
        ipadx = int(self.font_def[1] * 0.5)
        ipady = int(self.font_def[1] * 0.3)

        tk.Button(
            btn_frame, text="➕ Hozzáadás",
            command=self.hozzaad_szektor,
            font=self.font_def, padx=padx, pady=pady
        ).pack(side=tk.LEFT, padx=5, ipadx=ipadx, ipady=ipady)

        tk.Button(
            btn_frame, text="🗑️ Törlés",
            command=self.torol_kijelolt_szektor,
            font=self.font_def, padx=padx, pady=pady
        ).pack(side=tk.LEFT, padx=5, ipadx=ipadx, ipady=ipady)

        tk.Button(
            btn_frame, text="🔁 Frissítés",
            command=self.load_szektorok,
            font=self.font_def, padx=padx, pady=pady
        ).pack(side=tk.LEFT, padx=5, ipadx=ipadx, ipady=ipady)

    # --- Adatok betöltése ---
    def load_szektorok(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            conn = pymysql.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute("SELECT szektor, szektorcsoport FROM szektor ORDER BY szektorcsoport, szektor")
                rows = cur.fetchall()
                for row in rows:
                    self.tree.insert("", tk.END, values=row)
            conn.close()
        except pymysql.MySQLError as e:
            messagebox.showerror("Hiba", str(e))

    # --- Hozzáadás ---
    def hozzaad_szektor(self):
        szektor = self.entry_szektor.get().strip()
        csoport = self.entry_csoport.get().strip()
        if not szektor or not csoport:
            messagebox.showwarning("Hiányzó mező", "Tölts ki minden mezőt.")
            return
        try:
            conn = pymysql.connect(**DB_CONFIG)
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO szektor (szektor, szektorcsoport)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE szektorcsoport = VALUES(szektorcsoport)
                """, (szektor, csoport))
            conn.commit()
            conn.close()

            self.load_szektorok()
            self.entry_szektor.delete(0, tk.END)
            self.entry_csoport.delete(0, tk.END)
        except pymysql.MySQLError as e:
            messagebox.showerror("Hiba", str(e))

    # --- Törlés ---
    def torol_kijelolt_szektor(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Nincs kijelölve", "Jelölj ki egy szektort a törléshez.")
            return
        szektor = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Megerősítés", f"Biztosan törlöd a(z) '{szektor}' szektort?"):
            try:
                conn = pymysql.connect(**DB_CONFIG)
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM szektor WHERE szektor = %s", (szektor,))
                conn.commit()
                conn.close()
                self.load_szektorok()
            except pymysql.MySQLError as e:
                messagebox.showerror("Hiba", str(e))