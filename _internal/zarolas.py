import pymysql
from datetime import datetime, timedelta
def ellenoriz_zarolas(esemeny_id, felhasznalo, kapcsolat):
    with kapcsolat.cursor() as cursor:
        cursor.execute("SELECT locked_by, locked_at FROM karesemeny WHERE id = %s", (esemeny_id,))
        sor = cursor.fetchone()
        if sor:
            locked_by, locked_at = sor
            most = datetime.now()

            if locked_by and locked_by != felhasznalo:
                if locked_at:
                    if isinstance(locked_at, str):
                        try:
                            locked_ido = datetime.strptime(locked_at, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            locked_ido = datetime.strptime(locked_at, '%Y-%m-%d %H:%M:%S.%f')
                    else:
                        locked_ido = locked_at  # Már datetime típus

                    lejart = (most - locked_ido) > timedelta(minutes=5)
                    return "foglalt", locked_by, lejart
                else:
                    return "foglalt", locked_by, False
            else:
                cursor.execute("""
                    UPDATE karesemeny SET locked_by = %s, locked_at = %s WHERE id = %s
                """, (felhasznalo, most, esemeny_id))
                kapcsolat.commit()
                return "sikeres", None, None
        return "nem_letezik", None, None