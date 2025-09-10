import requests
from bs4 import BeautifulSoup
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = "https://www.cdep.ro/co/sedinte.calendar"

def check_calendar():
    try:
        r = requests.get(URL, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.get_text().lower()

        if "jocuri de noroc" in content:
            send_telegram("📢 Proiectul privind jocurile de noroc apare în calendar!\n" + URL)
        else:
            print("Nu a fost găsit în acest moment.")
    except Exception as e:
        print(f"Eroare la accesarea paginii: {e}")
        send_telegram(f"⚠️ Eroare la accesarea site-ului: {e}")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code != 200:
            print("Eroare la trimiterea mesajului:", r.text)
    except Exception as e:
        print("Eroare la trimiterea pe Telegram:", e)

if __name__ == "__main__":
    while True:
        check_calendar()
        time.sleep(60)  # rulează zilnic
