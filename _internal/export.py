import pymysql
import pandas as pd
from tkinter import filedialog, messagebox
from config import DB_CONFIG

conn = pymysql.connect(**DB_CONFIG)

def export_karesemenyek(treeview=None):
    fajlnev = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel fájl", "*.xlsx"), ("CSV fájl", "*.csv")],
        title="Mentés másként"
    )
    if not fajlnev:
        return

    try:
        conn = pymysql.connect(**DB_CONFIG)
        query = """
            SELECT id, szektor, cim, eovx, eovy, jelzes_datuma, tipus,
                   rovid_leiras, bejelento, fokozat, mit_veszelyeztetett,
                   eletveszely, szervezet, feltolto, riasztasiszam,
                   kategoria1, kategoria2, kategoria3, kategoria4,
                   statusz, megjegyzes, modified_by, modified_at
            FROM karesemeny
        """
        df = pd.read_sql(query, conn)
        conn.close()

        if fajlnev.endswith(".csv"):
            df.to_csv(fajlnev, index=False)
        else:
            df.to_excel(fajlnev, index=False)

        messagebox.showinfo("Sikeres mentés", f"Sikeresen elmentve ide:\n{fajlnev}")

    except Exception as e:
        messagebox.showerror("Hiba", f"Hiba történt az export során:\n{str(e)}")