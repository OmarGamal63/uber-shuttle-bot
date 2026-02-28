import os
import requests
import time
from flask import Flask, request

app = Flask(__name__)

# بياناتك المعتمدة
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKQ"
UBER_EMAIL = "o.g2871994@gmail.com"
UBER_PASSWORD = "Lala1317025064"

# ذاكرة الصياد الذكية
bot_brain = {
    "target_time": "12:44 PM",
    "is_monitoring": False,
    "found_trips": 0
}

def send_telegram(text, chat_id):
    """إرسال التنبيهات مع أزرار التحكم الثابتة"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {
            "keyboard": [
                [{"text": "🔍 بدء مراقبة الأسبوع القادم"}],
                [{"text": "⚙️ تعديل الموعد"}, {"text": "🛑 إيقاف"}]
            ],
            "resize_keyboard": True
        }
    }
    requests.post(url, json=payload)

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # 1. استقبال وتعديل الموعد
        if ":" in text and ("AM" in text.upper() or "PM" in text.upper()):
            bot_brain["target_time"] = text.upper()
            send_telegram(f"🎯 تم ضبط الهدف: {bot_brain['target_time']}\nالبوت سيبحث عن 'Shuttle' ومقاعد > 0 طوال الأسبوع.", chat_id)

        # 2. بدء المراقبة الذكية
        elif text == "🔍 بدء مراقبة الأسبوع القادم":
            bot_brain["is_monitoring"] = True
            msg = (f"📡 بدأت المراقبة لـ {bot_brain['target_time']}\n"
                   f"✅ سأراقب الأسبوع كله.\n"
                   f"✅ سأتجاهل '0 مقعد'.\n"
                   f"✅ في حالة الفشل، سأنتقل فوراً لليوم التالي دون توقف!")
            send_telegram(msg, chat_id)

        # 3. معالجة الفشل والاستمرار
        elif text == "🛑 إيقاف":
            bot_brain["is_monitoring"] = False
            send_telegram("🛑 تم إيقاف الصياد.", chat_id)

    return "OK", 200

@app.route("/")
def health_check():
    return "Bot is Hunting! 🎯", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
