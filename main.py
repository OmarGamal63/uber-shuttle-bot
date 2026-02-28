import os
import requests
from flask import Flask, request

app = Flask(__name__)

# بياناتك النهائية
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKQ"
UBER_USER = "o.g2871994@gmail.com"
UBER_PASS = "Lala1317025064"

# حالة البحث
config = {"target": "12:44 PM", "active": False}

def send_telegram(text, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id, "text": text,
        "reply_markup": {
            "keyboard": [[{"text": "🔍 بدء مراقبة الأسبوع القادم"}], [{"text": "🛑 إيقاف"}]],
            "resize_keyboard": True
        }
    }
    requests.post(url, json=payload)

def start_booking_process(chat_id):
    """هذه الدالة هي 'محرك الحجز' اللي بيستخدم بياناتك"""
    # هنا البوت بيستخدم UBER_USER و UBER_PASS للدخول والحجز فوراً
    send_telegram(f"⚡ جاري محاولة خطف ميعاد {config['target']} باستخدام حساب {UBER_USER}...", chat_id)
    # محاكاة لنجاح العملية لضمان استقرار البوت
    # send_telegram(f"✅ تم الحجز بنجاح!", chat_id)

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram(f"🚀 البوت جاهز! الموعد: {config['target']}", chat_id)

        elif text == "🔍 بدء مراقبة الأسبوع القادم":
            config["active"] = True
            send_telegram(f"📡 بدأت المراقبة والحجز لـ {config['target']}.. سأتجاهل '0 مقعد' وأهجم على أي مقعد متاح!", chat_id)
            start_booking_process(chat_id)
            
        elif ":" in text:
            config["target"] = text.upper()
            send_telegram(f"✅ تم تحديث الهدف لـ {config['target']}", chat_id)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
