import configparser
import os

ALAP_FRISSITESI_IDO = 60  # másodperc
ALAP_TEMA = "flatly"
ALAP_BETUMERET = 12

# Globális változó a bejelentkezett felhasználóhoz
BEJELENTKEZETT_FELHASZNALO = None  # login_window.py majd beállítja

def set_bejelentkezett_felhasznalo(username):
    global BEJELENTKEZETT_FELHASZNALO
    BEJELENTKEZETT_FELHASZNALO = username

def get_user_config_path(username=None):
    if username is None:
        username = BEJELENTKEZETT_FELHASZNALO
    if username is None:
        raise ValueError("A felhasználó neve nincs megadva.")
    
    root_path = os.path.dirname(os.path.abspath(__file__))
    user_dir = os.path.join(root_path, "user_config", username)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, "beallitasok.ini")

def betolt_beallitas(username=None):
    config = configparser.ConfigParser()
    config.optionxform = str
    ini_fajl = get_user_config_path(username)

    # Csak akkor hozzuk létre az alapértelmezett beállításokat, ha a fájl nem létezik
    if not os.path.exists(ini_fajl):
        config["Frissites"] = {"ido": str(ALAP_FRISSITESI_IDO)}
        config["Tema"] = {"nev": ALAP_TEMA, "betumeret": str(ALAP_BETUMERET)}
        config["Oszlopok"] = {k: "1" for k in [
            "id","szektor","cim","EOVX","EOVY","jelzes_datuma","tipus",
            "rovid_leiras","bejelento","fokozat","mit_veszelyeztetett",
            "eletveszely","szervezet","feltolto","riasztasiszam",
            "kategoria1","kategoria2","kategoria3","kategoria4",
            "statusz","megjegyzes","locked_by","locked_at","modified_by"
        ]}
        with open(ini_fajl, "w") as f:
            config.write(f)

    # Mindig olvassuk be a fájlt
    config.read(ini_fajl)

    # Biztosítsuk, hogy minden kulcs ott legyen
    if "Frissites" not in config:
        config["Frissites"] = {"ido": str(ALAP_FRISSITESI_IDO)}
    if "Tema" not in config:
        config["Tema"] = {"nev": ALAP_TEMA, "betumeret": str(ALAP_BETUMERET)}
    if "Oszlopok" not in config:
        config["Oszlopok"] = {}

    if "betumeret" not in config["Tema"]:
        config["Tema"]["betumeret"] = str(ALAP_BETUMERET)

    # Ne írjuk felül, csak ha új kulcsot adunk hozzá
    with open(ini_fajl, "w") as f:
        config.write(f)

    ido = int(config["Frissites"].get("ido", ALAP_FRISSITESI_IDO))
    tema = config["Tema"].get("nev", ALAP_TEMA)
    betumeret = int(config["Tema"].get("betumeret", ALAP_BETUMERET))
    return ido * 1000, tema, betumeret

def mentes_beallitas(uj_ido=None, uj_tema=None, uj_betumeret=None):
    config = configparser.ConfigParser()
    config.optionxform = str
    ini_fajl = get_user_config_path()
    if os.path.exists(ini_fajl):
        config.read(ini_fajl)

    if "Frissites" not in config:
        config["Frissites"] = {}
    if "Tema" not in config:
        config["Tema"] = {"nev": ALAP_TEMA, "betumeret": str(ALAP_BETUMERET)}
    if "Oszlopok" not in config:
        config["Oszlopok"] = {}

    if uj_ido is not None:
        config["Frissites"]["ido"] = str(uj_ido)
    if uj_tema is not None:
        config["Tema"]["nev"] = uj_tema
    if uj_betumeret is not None:
        config["Tema"]["betumeret"] = str(uj_betumeret)

    with open(ini_fajl, "w") as f:
        config.write(f)

def mentes_oszlop_allapot(oszlop_allapotok: dict):
    config = configparser.ConfigParser()
    config.optionxform = str
    ini_fajl = get_user_config_path()
    if os.path.exists(ini_fajl):
        config.read(ini_fajl)

    if "Oszlopok" not in config:
        config["Oszlopok"] = {}

    for oszlop, ertek in oszlop_allapotok.items():
        config["Oszlopok"][oszlop] = "1" if ertek else "0"

    with open(ini_fajl, "w") as f:
        config.write(f)

def betolt_oszlop_allapot():
    ini_fajl = get_user_config_path()
    if not os.path.exists(ini_fajl):
        return {}

    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(ini_fajl)

    if "Oszlopok" not in config:
        return {}

    return {k: v == "1" for k, v in config["Oszlopok"].items()}