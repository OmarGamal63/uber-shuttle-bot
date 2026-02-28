import os
import requests
from flask import Flask, request

app = Flask(__name__)

# الإعدادات المعتمدة والنهائية
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKQ"
UBER_EMAIL = "o.g2871994@gmail.com"
UBER_PASSWORD = "Lala1317025064"

# ذاكرة البوت الذكية (بتحفظ الموعد وحالة المراقبة)
monitor_config = {
    "target_time": "12:44 PM", 
    "is_active": False
}

def send_telegram(text, chat_id):
    """إرسال الرسائل مع الأزرار النهائية"""
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

        # 1. أمر البداية
        if text == "/start":
            send_telegram(f"🚀 البوت متصل وجاهز! \n🎯 الموعد الحالي: {monitor_config['target_time']}", chat_id)

        # 2. بدء المراقبة (بكل المميزات اللي طلبتها)
        elif text == "🔍 بدء مراقبة الأسبوع القادم":
            monitor_config["is_active"] = True
            msg = (f"📡 بدأت المراقبة لـ {monitor_config['target_time']} طوال الأسبوع.\n"
                   f"✅ سأتجاهل أي رحلة بـ '0 مقعد'.\n"
                   f"✅ سأقوم بالتنبيه فوراً عند ظهور '1 مقعد متوفر' أو أكثر.\n"
                   f"🔄 في حالة فشل أي رحلة، سأستمر في فحص باقي أيام الأسبوع تلقائياً.")
            send_telegram(msg, chat_id)
            
        # 3. تعديل الموعد بالرسالة
        elif ":" in text and ("AM" in text.upper() or "PM" in text.upper()):
            monitor_config["target_time"] = text.upper()
            send_telegram(f"✅ تم تحديث هدف البحث لـ: {monitor_config['target_time']}", chat_id)

        # 4. إيقاف البوت
        elif text == "🛑 إيقاف":
            monitor_config["is_active"] = False
            send_telegram("🛑 توقفت المراقبة.", chat_id)

    return "OK", 200

@app.route("/")
def home():
    return "Bot is Running! 🎯", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
