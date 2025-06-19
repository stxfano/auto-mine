# main.py
from flask import Flask
from threading import Thread
import requests
import time
from datetime import datetime
import os

# --- PRIENI DALLE VARIABILI D'AMBIENTE ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://nnc.ftwapps.lol/api/user/ack"
HEADERS = {
    "Authorization": os.getenv("MINING_TOKEN"),
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Origin": "https://nnc.ftwapps.lol"
}
DATA = {
    "clicks": 10,
    "tg_user_id": int(TELEGRAM_CHAT_ID)
}

app = Flask('')

@app.route('/')
def home():
    uptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"I'm alive! Bot uptime: {uptime}"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def log_to_file(msg):
    with open("mining_log.txt", "a") as f:
        f.write(f"{datetime.now()} - {msg}\n")

def salva_prossima_ora(timestamp):
    with open("next_run.txt", "w") as f:
        f.write(str(timestamp))

def leggi_prossima_ora():
    if not os.path.exists("next_run.txt"):
        return 0
    try:
        return float(open("next_run.txt").read())
    except:
        return 0

def tempo_prossima_ora():
    now = datetime.now()
    return (60 - now.minute) * 60 - now.second

def minare():
    counter = 1
    send_telegram_msg("🚀 Mining iniziato!")
    log_to_file("Mining iniziato")
    while True:
        now_ts = time.time()
        next_ts = leggi_prossima_ora()
        if now_ts < next_ts:
            secs = int(next_ts - now_ts)
            msg = f"🛌 In pausa intelligente: sleep {secs}s"
            print(msg); log_to_file(msg)
            time.sleep(secs)

        try:
            r = requests.post(URL, headers=HEADERS, json=DATA)
            if r.status_code == 200:
                msg = f"✅ {counter} - Mining ok"
            elif r.status_code == 400:
                att = tempo_prossima_ora()
                salva_prossima_ora(time.time() + att)
                msg = f"⚠️ Energia finita! Pausa {att}s"
            else:
                msg = f"❌ Error {r.status_code}: {r.text}"
            print(msg); log_to_file(msg); send_telegram_msg(msg)
        except Exception as e:
            msg = f"❌ Errore: {e}"
            print(msg); log_to_file(msg); send_telegram_msg(msg)

        counter += 1

if __name__ == "__main__":
    keep_alive()
    Thread(target=minare).start()
