import tkinter as tk
from tkinter import filedialog
import pymysql
import pymysql.cursors
import pandas as pd
import os
from config import DB_CONFIG

# Saját üzenetablak ikon támogatással
def custom_messagebox(title, message, tipus="info"):
    import tkinter as tk
    import os

    # Hozz létre egy külön főablakot, de rejtsd el
    root = tk.Tk()
    root.withdraw()

    # Felugró ablak létrehozása
    win = tk.Toplevel(root)
    win.title(title)

    # Ikon beállítása
    ico_path = os.path.join(os.path.dirname(__file__), "vihar.ico")
    try:
        win.iconbitmap(ico_path)
    except Exception:
        pass

    # Szín kiválasztása típus szerint
    if tipus == "error":
        fg_color = "red"
    elif tipus == "warning":
        fg_color = "orange"
    else:
        fg_color = "green"

    # Szöveg
    tk.Label(
        win, text=message, wraplength=320,
        font=("Segoe UI", 11), fg=fg_color
    ).pack(pady=20)

    # OK gomb
    tk.Button(
        win, text="OK", command=win.destroy,
        font=("Segoe UI", 11), width=10
    ).pack(pady=10)

    # Modális viselkedés
    win.transient(root)
    win.grab_set()

    # **FONTOS: saját eseményciklus, amíg az ablak nyitva van**
    root.wait_window(win)

    # Ezután zárjuk a root-ot
    root.destroy()
def import_karesemenyek(parent):
    fajlnev = filedialog.askopenfilename(
        parent=parent.root,  # főablakhoz kötjük a dialógust
        title="Import fájl kiválasztása",
        filetypes=[
            ("Excel fájlok", "*.xlsx *.xls"),
            ("CSV fájlok", "*.csv"),
            ("Minden fájl", "*.*")
        ]
    )

    if not fajlnev:
        return

    try:
        # CSV / Excel betöltés
        if fajlnev.endswith(".csv"):
            df = pd.read_csv(fajlnev, sep=None, engine="python", encoding="utf-8")
        elif fajlnev.endswith(".xls") or fajlnev.endswith(".xlsx"):
            df = pd.read_excel(fajlnev)
        else:
            parent.custom_message("Hiba", "Nem támogatott fájltípus!", tipus="error")
            return

        df.columns = [c.strip() for c in df.columns]

        elvart_oszlopok = [
            "ID", "szektor", "cím", "EOVX", "EOVY", "jelzés dátuma", "típus", "rövid leírás",
            "bejelentő", "fokozat", "mit veszélyeztett?", "életveszély?", "szervezet", "feltöltő",
            "riasztásiszám", "kategória 1", "kategória 2", "kategória 3", "kategória 4"
        ]

        if not all(col in df.columns for col in elvart_oszlopok):
            hianyzo = [col for col in elvart_oszlopok if col not in df.columns]
            parent.custom_message("Hiba", f"Hiányzó oszlop(ok):\n{', '.join(hianyzo)}", tipus="error")
            return

        # Adatok tisztítása
        df = df.where(pd.notnull(df), None)
        df["jelzés dátuma"] = pd.to_datetime(df["jelzés dátuma"], errors='coerce')
        df["jelzés dátuma"] = df["jelzés dátuma"].dt.strftime("%Y-%m-%d %H:%M:%S")

        # Adatbázis kapcsolat
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        cur.execute("SELECT id, statusz FROM karesemeny")
        id_statusz_dict = {str(row["id"]): row["statusz"] for row in cur.fetchall()}

        sikeres_betoltes = 0
        kihagyott_sorok = 0

        for _, sor in df.iterrows():
            id_ertek = str(sor["ID"])

            if id_ertek in id_statusz_dict and id_statusz_dict[id_ertek] == "LEZÁRT":
                kihagyott_sorok += 1
                continue

            aktualis_statusz = id_statusz_dict.get(id_ertek, "FELDOLGOZANDÓ")
            if aktualis_statusz in [None, "", "AKTÍV"]:
                uj_statusz = "FELDOLGOZANDÓ"
            else:
                uj_statusz = aktualis_statusz

            cur.execute("""
                INSERT INTO karesemeny (
                    id, szektor, cim, eovx, eovy, jelzes_datuma, tipus,
                    rovid_leiras, bejelento, fokozat, mit_veszelyeztetett,
                    eletveszely, szervezet, feltolto, riasztasiszam,
                    kategoria1, kategoria2, kategoria3, kategoria4,
                    statusz, megjegyzes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    szektor = VALUES(szektor),
                    cim = VALUES(cim),
                    eovx = VALUES(eovx),
                    eovy = VALUES(eovy),
                    jelzes_datuma = VALUES(jelzes_datuma),
                    tipus = VALUES(tipus),
                    rovid_leiras = VALUES(rovid_leiras),
                    bejelento = VALUES(bejelento),
                    fokozat = VALUES(fokozat),
                    mit_veszelyeztetett = VALUES(mit_veszelyeztetett),
                    eletveszely = VALUES(eletveszely),
                    szervezet = VALUES(szervezet),
                    feltolto = VALUES(feltolto),
                    riasztasiszam = VALUES(riasztasiszam),
                    kategoria1 = VALUES(kategoria1),
                    kategoria2 = VALUES(kategoria2),
                    kategoria3 = VALUES(kategoria3),
                    kategoria4 = VALUES(kategoria4),
                    statusz = %s,
                    megjegyzes = VALUES(megjegyzes)
            """, (
                id_ertek,
                sor["szektor"],
                sor["cím"],
                str(sor["EOVX"]),
                str(sor["EOVY"]),
                sor["jelzés dátuma"],
                sor["típus"],
                sor["rövid leírás"],
                sor["bejelentő"],
                sor["fokozat"],
                sor["mit veszélyeztett?"],
                sor["életveszély?"],
                sor["szervezet"],
                sor["feltöltő"],
                sor["riasztásiszám"],
                sor["kategória 1"],
                sor["kategória 2"],
                sor["kategória 3"],
                sor["kategória 4"],
                uj_statusz,
                "",  # megjegyzes
                uj_statusz
            ))

            sikeres_betoltes += 1

        conn.commit()
        conn.close()

        # Siker üzenet
        uzenet = f"Sikeresen importált rekordok: {sikeres_betoltes}."
        if kihagyott_sorok > 0:
            uzenet += f"\nKihagyott rekordok (LEZÁRT státusz miatt): {kihagyott_sorok}."

        parent.custom_message("Import vége", uzenet, tipus="info")

    except Exception as e:
        parent.custom_message("Hiba", f"Hiba történt az import során:\n{str(e)}", tipus="error")