from flask import Flask
import threading
import os
import requests
from bs4 import BeautifulSoup
import time
import logging

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

# Funcție de verificare site
def check_calendar():
    try:
        r = requests.get(URL, timeout=30)
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
        time.sleep(60)  # verifică la fiecare minut pentru test

if __name__ == "__main__":
    # pornește botul într-un thread separat
    threading.Thread(target=run_bot, daemon=True).start()
    # pornește serverul web pe portul dat de Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
