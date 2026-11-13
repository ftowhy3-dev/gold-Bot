import time, requests, yfinance as yf, threading, os
from flask import Flask, request

app = Flask(__name__)
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send(chat_id, msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": msg}, timeout=10)
    except Exception as e:
        print(e)

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
            send(chat_id, "✅ البوت شغال!")
        if text == "/test" and chat_id:
            send(chat_id, "✅ التست شغال، البوت حي وبيسمعك")
    except Exception as e:
        print(e)
    return "ok"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# رسالة اول ما البوت يشتغل عشان تعرف انو حي
send(CHAT_ID, "🚀 البوت اشتغل من جديد، بيراقب الذهب هسي")

def get_price(symbol):
    df = yf.download(symbol, period="1d", interval="5m", progress=False)
    if df.empty: return None, None
    # تصليح مشكلة الاعمدة الجديدة في yfinance
    if hasattr(df.columns, 'get_level_values'):
        try: df.columns = df.columns.get_level_values(0)
        except: pass
    close = df['Close']
    ema_fast = close.ewm(span=5).mean()
    ema_slow = close.ewm(span=13).mean()
    return float(close.iloc[-1]), (ema_fast.iloc[-1], ema_slow.iloc[-1], ema_fast.iloc[-2], ema_slow.iloc[-2])

last_signal = {"GOLD": "", "EUR": ""}

def check():
    for symbol, name, key in [("GC=F","XAUUSD GOLD","GOLD"), ("EURUSD=X","EURUSD","EUR")]:
        try:
            price, emas = get_price(symbol)
            if price is None: continue
            fast, slow, prev_fast, prev_slow = emas
            sig = ""
            if prev_fast < prev_slow and fast > slow: sig = "BUY"
            if prev_fast > prev_slow and fast < slow: sig = "SELL"
            if sig and last_signal[key] != sig:
                last_signal[key] = sig
                emoji = "🟢" if sig=="BUY" else "🔴"
                send(CHAT_ID, f"{emoji} {name} {sig} @ {price:.2f}\nفريم 5 دقائق - تقاطع EMA")
            print(f"{name} {price} fast={fast:.2f} slow={slow:.2f}")
        except Exception as e:
            print(f"Error {name}: {e}")

counter = 0
while True:
    check()
    counter += 1
    # كل ساعة يرسل سعر الذهب عشان تتأكد انو حي
    if counter % 12 == 0:
        try:
            p,_ = get_price("GC=F")
            if p: send(CHAT_ID, f"📊 الذهب هسي: {p:.2f} $ - البوت شغال ومراقب")
        except: pass
    time.sleep(300) # كل 5 دقائق
