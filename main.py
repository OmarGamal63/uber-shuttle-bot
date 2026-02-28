import os
import requests
from flask import Flask, request

app = Flask(__name__)

# الإعدادات النهائية المعتمدة
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKQ"
monitor_config = {
    "target_time": "12:44 PM", 
    "is_active": False,
    "last_chat_id": None
}

def send_telegram(text, chat_id, keyboard=True):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if keyboard:
        payload["reply_markup"] = {
            "keyboard": [
                [{"text": "🔍 بدء مراقبة الأسبوع القادم"}],
                [{"text": "⚙️ تعديل الموعد"}, {"text": "🛑 إيقاف"}]
            ],
            "resize_keyboard": True
        }
    requests.post(url, json=payload)

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        monitor_config["last_chat_id"] = chat_id

        if text == "/start":
            send_telegram(f"🚀 البوت شغال! الموعد الحالي: {monitor_config['target_time']}", chat_id)
        
        elif text == "🔍 بدء مراقبة الأسبوع القادم":
            monitor_config["is_active"] = True
            send_telegram(f"📡 بدأت المراقبة لموعد {monitor_config['target_time']} طوال الأسبوع. \n⚠️ سأتجاهل '0 مقاعد' وأرسل تنبيه فوراً عند وجود '1 مقعد متوفر'!", chat_id)
            
        elif text == "⚙️ تعديل الموعد":
            send_telegram("أرسل الموعد الجديد (مثلاً: 01:30 PM)", chat_id, keyboard=False)

        elif ":" in text and ("AM" in text.upper() or "PM" in text.upper()):
            monitor_config["target_time"] = text.upper()
            send_telegram(f"✅ تم تحديث موعد البحث إلى: {monitor_config['target_time']}", chat_id)

        elif text == "🛑 إيقاف":
            monitor_config["is_active"] = False
            send_telegram("🛑 توقفت المراقبة.", chat_id)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
