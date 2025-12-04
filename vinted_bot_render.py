import time
import os
import re
import requests

# ========= CONFIG =========

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
PROXY_URL = os.getenv("PROXY_URL", "").strip()

VINTED_SEARCH_URLS = [
    "https://www.vinted.fr/catalog?search_text=asics%20kayano%2014&price_to=25.0&currency=EUR&size_ids[]=776&size_ids[]=777&size_ids[]=778&size_ids[]=779&size_ids[]=780&size_ids[]=781&size_ids[]=782&size_ids[]=783&size_ids[]=784&size_ids[]=785&size_ids[]=786&size_ids[]=787&size_ids[]=788&size_ids[]=789&size_ids[]=790&size_ids[]=791&size_ids[]=792&size_ids[]=1196&size_ids[]=57&size_ids[]=1197&size_ids[]=58&size_ids[]=1198&size_ids[]=59&size_ids[]=1199&size_ids[]=60&size_ids[]=1200&size_ids[]=61&size_ids[]=62&size_ids[]=1201&size_ids[]=1579&size_ids[]=63&size_ids[]=1573&size_ids[]=1574&size_ids[]=1575&size_ids[]=1576&size_ids[]=1577&size_ids[]=1578&search_id=29150743476&order=newest_first&search_by_image_uuid=&page=1&time=1764806022",
    "https://www.vinted.fr/catalog?search_text=nike%20shox&price_to=25.0&currency=EUR&size_ids[]=776&size_ids[]=777&size_ids[]=778&size_ids[]=779&size_ids[]=780&size_ids[]=781&size_ids[]=782&size_ids[]=783&size_ids[]=784&size_ids[]=785&size_ids[]=786&size_ids[]=787&size_ids[]=788&size_ids[]=789&size_ids[]=790&size_ids[]=791&size_ids[]=792&size_ids[]=1196&size_ids[]=57&size_ids[]=1197&size_ids[]=58&size_ids[]=1198&size_ids[]=59&size_ids[]=1199&size_ids[]=60&size_ids[]=1200&size_ids[]=61&size_ids[]=62&size_ids[]=1201&size_ids[]=1579&size_ids[]=63&size_ids[]=1573&size_ids[]=1574&size_ids[]=1575&size_ids[]=1576&size_ids[]=1577&size_ids[]=1578&search_id=29137787530&order=newest_first&search_by_image_uuid=&page=1&time=1764806062",
    "https://www.vinted.fr/catalog?search_text=nike%20p6000&price_to=25.0&currency=EUR&size_ids[]=776&size_ids[]=777&size_ids[]=778&size_ids[]=779&size_ids[]=780&size_ids[]=781&size_ids[]=782&size_ids[]=783&size_ids[]=784&size_ids[]=785&size_ids[]=786&size_ids[]=787&size_ids[]=788&size_ids[]=789&size_ids[]=790&size_ids[]=791&size_ids[]=792&size_ids[]=1196&size_ids[]=57&size_ids[]=1197&size_ids[]=58&size_ids[]=1198&size_ids[]=59&size_ids[]=1199&size_ids[]=60&size_ids[]=1200&size_ids[]=61&size_ids[]=62&size_ids[]=1201&size_ids[]=1579&size_ids[]=63&size_ids[]=1573&size_ids[]=1574&size_ids[]=1575&size_ids[]=1576&size_ids[]=1577&size_ids[]=1578&search_id=29150760868&order=newest_first&search_by_image_uuid=&page=1&time=1764806098",
    "https://www.vinted.fr/catalog?search_text=nike%20dn&price_to=25.0&currency=EUR&size_ids[]=776&size_ids[]=777&size_ids[]=778&size_ids[]=779&size_ids[]=780&size_ids[]=781&size_ids[]=782&size_ids[]=783&size_ids[]=784&size_ids[]=785&size_ids[]=786&size_ids[]=787&size_ids[]=788&size_ids[]=789&size_ids[]=790&size_ids[]=791&size_ids[]=792&size_ids[]=1196&size_ids[]=57&size_ids[]=1197&size_ids[]=58&size_ids[]=1198&size_ids[]=59&size_ids[]=1199&size_ids[]=60&size_ids[]=1200&size_ids[]=61&size_ids[]=62&size_ids[]=1201&size_ids[]=1579&size_ids[]=63&size_ids[]=1573&size_ids[]=1574&size_ids[]=1575&size_ids[]=1576&size_ids[]=1577&size_ids[]=1578&search_id=29150771110&order=newest_first&search_by_image_uuid=&page=1&time=1764806143",
    "https://www.vinted.fr/catalog?search_text=nike%20vomero%205&price_to=25.0&currency=EUR&size_ids[]=776&size_ids[]=777&size_ids[]=778&size_ids[]=779&size_ids[]=780&size_ids[]=781&size_ids[]=782&size_ids[]=783&size_ids[]=784&size_ids[]=785&size_ids[]=786&size_ids[]=787&size_ids[]=788&size_ids[]=789&size_ids[]=790&size_ids[]=791&size_ids[]=792&size_ids[]=1196&size_ids[]=57&size_ids[]=1197&size_ids[]=58&size_ids[]=1198&size_ids[]=59&size_ids[]=1199&size_ids[]=60&size_ids[]=1200&size_ids[]=61&size_ids[]=62&size_ids[]=1201&size_ids[]=1579&size_ids[]=63&size_ids[]=1573&size_ids[]=1574&size_ids[]=1575&size_ids[]=1576&size_ids[]=1577&size_ids[]=1578&search_id=29150786218&order=newest_first&search_by_image_uuid=&page=1&time=1764806210",
]

POLL_INTERVAL_SECONDS = 60  # 1 minute entre deux scans

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.vinted.fr/"
}

session = requests.Session()
session.headers.update(HEADERS)

if PROXY_URL:
    session.proxies = {
        "http": PROXY_URL,
        "https": PROXY_URL,
    }

# ========= TELEGRAM =========

def send_telegram_photo(title, url, photo_url):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[WARN] TELEGRAM_BOT_* non configuré, envoi ignoré.")
        return

    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

    caption = (
        f"*Nouvel article détecté !*\n\n"
        f"*{title}*\n"
        f"[🔗 Voir l'annonce]({url})"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": caption,
        "photo": photo_url,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(api_url, data=payload, timeout=20)
    except Exception as e:
        print(f"[ERREUR Telegram] {e}")

# ========= SCRAPING =========

def fetch_all_item_ids():
    all_ids = set()
    for url in VINTED_SEARCH_URLS:
        try:
            resp = session.get(url, timeout=20)
            if resp.status_code == 403:
                print(f"[403] Accès refusé pour {url}")
                continue
            resp.raise_for_status()
            html = resp.text
            ids = re.findall(r"/items/(\d+)", html)
            all_ids.update(ids)
        except Exception as e:
            print(f"[ERREUR] en récupérant {url} : {e}")
    return sorted(all_ids)

def fetch_item_preview(item_id):
    url = f"https://www.vinted.fr/items/{item_id}"

    resp = session.get(url, timeout=20)
    if resp.status_code == 429:
        raise RuntimeError("429")
    if resp.status_code == 403:
        raise RuntimeError("403")
    resp.raise_for_status()
    html = resp.text

    m_title = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    title = m_title.group(1) if m_title else f"Article {item_id}"

    m_img = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    image = m_img.group(1) if m_img else ""

    return title, url, image

# ========= MAIN =========

def main():
    print("Bot multi-filtres démarré sur Render.")
    known_ids = set()
    first_cycle = True

    while True:
        try:
            ids = fetch_all_item_ids()

            if first_cycle:
                # PREMIER TOUR : on enregistre juste les annonces existantes
                known_ids = set(ids)
                print(f"Premier cycle : {len(known_ids)} annonces connues, aucune envoyée.")
                first_cycle = False
            else:
                new_ids = [i for i in ids if i not in known_ids]

                if new_ids:
                    print(f"{len(new_ids)} nouveaux articles trouvés.")
                for item_id in new_ids:
                    try:
                        title, url, image = fetch_item_preview(item_id)
                        send_telegram_photo(title, url, image)
                        known_ids.add(item_id)
                        time.sleep(3)
                    except RuntimeError as e:
                        if str(e) == "429":
                            print("[WARN] 429 Too Many Requests — pause 60s")
                            time.sleep(60)
                            continue
                        if str(e) == "403":
                            print("[WARN] 403 Forbidden sur l'item, je passe.")
                            continue
                        print(f"[ERREUR inconnue sur {item_id}] {e}")
                    except Exception as e:
                        print(f"[ERREUR article {item_id}] {e}")

        except Exception as e:
            print(f"[ERREUR générale] {e}")

        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
