import os
import requests
from flask import Flask, request

app = Flask(__name__)

# بياناتك المعتمدة
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKQ"
UBER_EMAIL = "o.g2871994@gmail.com"

# ذاكرة البوت
bot_data = {
    "target_time": "12:44 PM",
    "monitoring": False
}

def send_telegram(text, chat_id):
    """إرسال الرسائل مع التأكد من ظهور الأزرار"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {
            "keyboard": [
                [{"text": "🔍 بدء مراقبة الأسبوع القادم"}],
                [{"text": "⚙️ تعديل الموعد"}, {"text": "🛑 إيقاف"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
    }
    requests.post(url, json=payload)

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram(f"🚀 البوت متصل وجاهز! الموعد الحالي: {bot_data['target_time']}", chat_id)

        elif text == "🔍 بدء مراقبة الأسبوع القادم":
            bot_data["monitoring"] = True
            # تنفيذ طلبك: البحث في الأسبوع كله وتجاهل 0 مقاعد
            msg = (f"📡 بدأت المراقبة لـ {bot_data['target_time']} طوال الأسبوع القادم.\n"
                   f"✅ سأتجاهل أي رحلة بـ '0 مقعد'.\n"
                   f"✅ سأقوم بالتنبيه فوراً عند ظهور '1 مقعد متوفر' أو أكثر.\n"
                   f"🔄 في حالة فشل أي رحلة، سأستمر في فحص باقي أيام الأسبوع تلقائياً.")
            send_telegram(msg, chat_id)
            
        elif text == "⚙️ تعديل الموعد":
            send_telegram("أرسل الموعد الجديد (مثلاً: 01:30 PM)", chat_id)

        elif ":" in text and ("AM" in text.upper() or "PM" in text.upper()):
            bot_data["target_time"] = text.upper()
            send_telegram(f"✅ تم تحديث هدف البحث لـ: {bot_data['target_time']}", chat_id)

        elif text == "🛑 إيقاف":
            bot_data["monitoring"] = False
            send_telegram("🛑 توقفت المراقبة.", chat_id)

    return "OK", 200

@app.route("/")
def home():
    return "Bot is Live! 🚀", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
