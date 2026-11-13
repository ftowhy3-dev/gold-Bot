import time, requests, yfinance as yf, threading
from flask import Flask, request

app = Flask(__name__)

TOKEN = "9036640474:AAES3q0F2n2ck_mgAwzexuUTZcRbfZ-B3jU"
CHAT_ID = "1320938378"

def send(chat_id, msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

@app.route('/')
def home():
    return "Bot is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        msg = data.get("message", {})
        text = msg.get("text", "")
        chat_id = msg.get("chat", {}).get("id")
        if text == "/start" and chat_id:
            send(chat_id, "✅ البوت شغال!\nبيراقب GOLD و EURUSD 24 ساعة\nأول ما تحصل إشارة ح أرسلها ليك طوالي")
    except Exception as e:
        print(e)
    return "ok"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web, daemon=True).start()

def check(symbol, name):
    df = yf.download(symbol, period="1d", interval="1m", progress=False)
    if len(df) < 20: return
    df['EMA5'] = df['Close'].ewm(span=5).mean()
    df['EMA13'] = df['Close'].ewm(span=13).mean()
    last = df.iloc[-1]
    prev = df.iloc[-2]
    price = float(last['Close'])
    if prev['EMA5'] < prev['EMA13'] and last['EMA5'] > last['EMA13']:
        send(CHAT_ID, f"🟢 {name} BUY @ {price:.2f}")
    if prev['EMA5'] > prev['EMA13'] and last['EMA5'] < last['EMA13']:
        send(CHAT_ID, f"🔴 {name} SELL @ {price:.2f}")

while True:
    try:
        check("GC=F", "XAUUSD GOLD")
        check("EURUSD=X", "EURUSD")
    except Exception as e:
        print(e)
    time.sleep(60)
