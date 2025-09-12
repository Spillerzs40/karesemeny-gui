from ldap3 import Server, Connection, ALL, NTLM, SUBTREE

AD_SERVER = '10.254.4.252'
AD_DOMAIN = 'katvedd1.local'
AD_SEARCH_BASE = 'DC=katvedd1,DC=local'
ALLOWED_GROUP_DN = 'CN=FKI_OPTORZSRE_BERENDELTEK,OU=Groups,OU=Fovaros PVI,OU=Igazgatosagok,OU=OKF,DC=katvedd1,DC=local'

def ldap_authenticate(username, password):
    username = username.strip()
    user_dn = f'{AD_DOMAIN}\\{username}'
    server = Server(AD_SERVER, get_info=ALL)

    try:
        print(f"[DEBUG] Kapcsolódás: {user_dn}")
        conn = Connection(server, user=user_dn, password=password, authentication=NTLM)
        if not conn.bind():
            print(f"[DEBUG] Bind sikertelen: {conn.last_error}")
            return False
        print("[DEBUG] Sikeres bind")

        conn.search(
            search_base=AD_SEARCH_BASE,
            search_filter=f'(&(objectClass=user)(sAMAccountName={username})(memberOf={ALLOWED_GROUP_DN}))',
            search_scope=SUBTREE,
            attributes=['cn']
        )

        print(f"[DEBUG] Találatok száma: {len(conn.entries)}")
        return bool(conn.entries)

    except Exception as e:
        print("LDAP hiba:", e)
        return False
        
def get_display_name(username, password):
    username = username.strip()
    user_dn = f"{AD_DOMAIN}\\{username}"
    server = Server(AD_SERVER, get_info=ALL)
    
    try:
        # Hitelesített kapcsolódás a bejelentkezési adatokkal
        conn = Connection(server, user=user_dn, password=password, authentication=NTLM)
        if not conn.bind():
            print(f"[DEBUG] Bind sikertelen displayName lekérésnél: {conn.last_error}")
            return username  # fallback, ha nem sikerül

        conn.search(
            search_base=AD_SEARCH_BASE,
            search_filter=f'(sAMAccountName={username})',
            search_scope=SUBTREE,
            attributes=['cn']
        )

        if conn.entries:
            entry = conn.entries[0]
            print(f"[DEBUG] LDAP Entry: {entry}")
            if 'cn' in entry and entry.cn.value:
                return entry.cn.value  # Visszaadja a teljes nevet

        return username

    except Exception as e:
        print(f"[HIBA] DisplayName lekérdezés hiba: {e}")
        return username

def get_user_info(username):
    username = username.strip()
    server = Server(AD_SERVER, get_info=ALL)

    try:
        conn = Connection(server, user='', password='', authentication=NTLM)
        if not conn.bind():
            print(f"[DEBUG] Bind sikertelen user info lekérésnél: {conn.last_error}")
            return None

        conn.search(
            search_base=AD_SEARCH_BASE,
            search_filter=f'(sAMAccountName={username})',
            search_scope=SUBTREE,
            attributes=['cn', 'mail', 'title']
        )

        if conn.entries:
            entry = conn.entries[0]
            return {
                'cn': entry.cn.value if 'cn' in entry else None,
                'mail': entry.mail.value if 'mail' in entry else None,
                'title': entry.title.value if 'title' in entry else None,
            }
        return None

    except Exception as e:
        print(f"[HIBA] User info lekérdezés hiba: {e}")
        return None