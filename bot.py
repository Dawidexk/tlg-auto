from flask import Flask
import threading
import os
import requests
from bs4 import BeautifulSoup
import time
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configurare logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Variabile de mediu
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = "https://www.cdep.ro/co/sedinte.calendar"

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Configurează sesiune cu retry-uri
session = requests.Session()
retries = Retry(total=5, backoff_factor=2, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# Funcție de verificare site
def check_calendar():
    try:
        r = session.get(URL, timeout=60)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.get_text().lower()

        if "jocuri de noroc" in content:
            send_telegram("📢 Proiectul privind jocurile de noroc apare în calendar!\n" + URL)
        else:
            logging.info("Nu a fost găsit în acest moment.")
    except Exception as e:
        logging.error(f"Eroare la accesarea paginii: {e}")
        send_telegram(f"⚠️ Eroare la accesarea site-ului: {e}")

# Funcție de trimitere Telegram
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code != 200:
            logging.error(f"Eroare la trimiterea mesajului: {r.text}")
        else:
            logging.info("Mesaj trimis cu succes ✅")
    except Exception as e:
        logging.error(f"Eroare la trimiterea pe Telegram: {e}")

# Thread principal pentru bot
def run_bot():
    while True:
        check_calendar()
        time.sleep(86400)  # Rulează o dată pe zi (86400 secunde)
        # Pentru test rapid: time.sleep(60)

if __name__ == "__main__":
    # pornește botul într-un thread separat
    threading.Thread(target=run_bot, daemon=True).start()
    # pornește serverul web pe portul dat de Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
