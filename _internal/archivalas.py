import os
import pymysql
import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import subprocess
from config import DB_CONFIG

# === Egyedi üzenetablakok vihar.ico-val ===

def custom_message(parent, title, message, tipus="info"):
    """Egyedi üzenetablak ikon támogatással (OK gomb), középre helyezve"""
    ico_path = os.path.join(os.path.dirname(__file__), "vihar.ico")

    win = tk.Toplevel(parent)
    win.title(title)
    try:
        win.iconbitmap(ico_path)
    except:
        pass

    # Ablak mérete
    ablak_szelesseg = 300
    ablak_magassag = 200

    # Középre helyezés a parent-hez képest
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (ablak_szelesseg // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (ablak_magassag // 2)
    win.geometry(f"{ablak_szelesseg}x{ablak_magassag}+{x}+{y}")

    win.transient(parent)
    win.grab_set()

    tk.Label(win, text=message, wraplength=280, font=("Segoe UI", 11)).pack(pady=20)

    tk.Button(win, text="OK", command=win.destroy, font=("Segoe UI", 11)).pack(pady=10)

    win.wait_window()


def custom_yesno(parent, title, message):
    """Igen/Nem kérdés egyedi ikon ablakban, középre helyezve"""
    ico_path = os.path.join(os.path.dirname(__file__), "vihar.ico")
    result = [False]

    win = tk.Toplevel(parent)
    win.title(title)
    try:
        win.iconbitmap(ico_path)
    except:
        pass

    # Ablak mérete
    ablak_szelesseg = 320
    ablak_magassag = 180

    # Középre helyezés a parent-hez képest
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (ablak_szelesseg // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (ablak_magassag // 2)
    win.geometry(f"{ablak_szelesseg}x{ablak_magassag}+{x}+{y}")

    win.transient(parent)
    win.grab_set()

    tk.Label(win, text=message, wraplength=300, font=("Segoe UI", 11)).pack(pady=20)

    def yes():
        result[0] = True
        win.destroy()

    def no():
        result[0] = False
        win.destroy()

    frame = tk.Frame(win)
    frame.pack(pady=10)

    tk.Button(frame, text="Igen", width=8, command=yes, font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)
    tk.Button(frame, text="Nem", width=8, command=no, font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=5)

    win.wait_window()
    return result[0]


# === Adatbázis mentés ===

def adatbazis_mentes(sql_dump_file):
    try:
        mysqldump_path = r"c:\xampp\mysql\bin\mysqldump.exe"
        parancs = [
            mysqldump_path,
            "-h", DB_CONFIG["host"],
            "-u", DB_CONFIG["user"],
            f"-p{DB_CONFIG['password']}",
            DB_CONFIG["database"]
        ]
        with open(sql_dump_file, "w", encoding="utf-8") as f:
            subprocess.run(parancs, stdout=f, check=True)
        return True, None
    except Exception as e:
        return False, str(e)


# === Archiválás és kiürítés ===

def archiválás_es_kiurites(parent):
    if not custom_yesno(parent, "Megerősítés", "Biztosan archiválod és kiüríted a jelenlegi adatbázist és eseményeket?"):
        return

    try:
        # 1. Adatbázis mentés
        mentesi_fajl = filedialog.asksaveasfilename(
            title="Adatbázis mentés mentése",
            defaultextension=".sql",
            filetypes=[("SQL fájl (*.sql)", "*.sql")],
            initialfile="karesemeny_backup.sql"
        )
        if not mentesi_fajl:
            return

        sikeres, hiba = adatbazis_mentes(mentesi_fajl)
        if not sikeres:
            custom_message(parent, "Hiba", f"Adatbázis mentése sikertelen:\n{hiba}", tipus="error")
            return

        # 2. Excel/CSV export
        conn = pymysql.connect(**DB_CONFIG)
        df = pd.read_sql("SELECT * FROM karesemeny", conn)

        if df.empty:
            custom_message(parent, "Archiválás", "Nincs archiválható adat.")
            conn.close()
            return

        export_file = filedialog.asksaveasfilename(
            title="Archivált adatok mentése",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel fájl (*.xlsx)", "*.xlsx"),
                ("CSV fájl (*.csv)", "*.csv")
            ],
            initialfile="archivalt_karesemenyek"
        )
        if not export_file:
            conn.close()
            return

        if export_file.endswith(".csv"):
            df.to_csv(export_file, sep=";", index=False, encoding="utf-8-sig")
        else:
            df.to_excel(export_file, index=False)

        # 3. Adatbázis kiürítése
        with conn.cursor() as cur:
            cur.execute("DELETE FROM karesemeny")
            conn.commit()
        conn.close()

        custom_message(parent, "Archiválás kész", f"Adatbázis mentve: {mentesi_fajl}\nArchivált fájl: {export_file}")

    except Exception as e:
        custom_message(parent, "Hiba", f"Archiválás közben hiba történt:\n{str(e)}", tipus="error")


# === Archivált adatok megjelenítése ===

def archivalt_adatok_megjelenitese(parent):
    fajl_path = filedialog.askopenfilename(
        title="Archivált Excel, XLS vagy CSV kiválasztása",
        filetypes=[
            ("Minden támogatott fájl", "*.xlsx *.xls *.csv"),
            ("Excel fájlok", "*.xlsx *.xls"),
            ("CSV fájlok", "*.csv")
        ]
    )
    if not fajl_path:
        return

    try:
        if fajl_path.endswith(".csv"):
            df = pd.read_csv(fajl_path, sep=";", encoding="utf-8-sig")
        else:
            df = pd.read_excel(fajl_path)

        ablak = tk.Toplevel(parent)
        ablak.title("Archivált adatok megjelenítése")
        ico_path = os.path.join(os.path.dirname(__file__), "vihar.ico")
        try:
            ablak.iconbitmap(ico_path)
        except:
            pass
        ablak.geometry("1100x700")

        # Keresőmező
        keres_frame = tk.Frame(ablak)
        keres_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(keres_frame, text="Keresés:").pack(side=tk.LEFT)
        keres_valtozo = tk.StringVar()
        keres_entry = ttk.Entry(keres_frame, textvariable=keres_valtozo, width=40)
        keres_entry.pack(side=tk.LEFT, padx=5)

        # Táblázat
        tabla_frame = tk.Frame(ablak)
        tabla_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        oszlopok = df.columns.tolist()
        tabla = ttk.Treeview(tabla_frame, columns=oszlopok, show="headings")
        tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tabla_frame, orient=tk.VERTICAL, command=tabla.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tabla.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(ablak, orient=tk.HORIZONTAL, command=tabla.xview)
        hsb.pack(fill=tk.X)
        tabla.configure(xscrollcommand=hsb.set)

        for col in oszlopok:
            tabla.heading(col, text=col)
            tabla.column(col, width=120, anchor=tk.W)

        # Szűrés
        def frissit_tabla():
            kulcs = keres_valtozo.get().lower()
            tabla.delete(*tabla.get_children())
            for _, sor in df.iterrows():
                if any(kulcs in str(ertek).lower() for ertek in sor.values):
                    tabla.insert("", "end", values=list(sor.values))

        keres_entry.bind("<KeyRelease>", lambda e: frissit_tabla())
        frissit_tabla()

        # Exportálás gomb
        def exportal():
            export_path = filedialog.asksaveasfilename(
                title="Adatok exportálása",
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel fájlok", "*.xlsx"),
                    ("CSV fájlok", "*.csv")
                ],
                initialfile="archivalt_export"
            )
            if not export_path:
                return
            try:
                adatok = []
                for gyerek in tabla.get_children():
                    adatok.append(tabla.item(gyerek)['values'])
                export_df = pd.DataFrame(adatok, columns=oszlopok)

                if export_path.endswith(".csv"):
                    export_df.to_csv(export_path, sep=";", index=False, encoding="utf-8-sig")
                else:
                    export_df.to_excel(export_path, index=False)

                custom_message(parent, "Sikeres exportálás", f"Az adatok mentve lettek ide:\n{export_path}")
            except Exception as e:
                custom_message(parent, "Hiba", f"Exportálási hiba:\n{e}", tipus="error")

        ttk.Button(ablak, text="Exportálás Excel/CSV fájlba", command=exportal).pack(pady=10)

    except Exception as e:
        custom_message(parent, "Hiba", f"Nem sikerült betölteni a fájlt:\n{str(e)}", tipus="error")