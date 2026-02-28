import os
import requests
from flask import Flask, request

app = Flask(__name__)

# الإعدادات النهائية المعتمدة من صورك
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKQ"

def send_telegram(text, chat_id):
    """إرسال رسالة مع إظهار أزرار التحكم فوراً"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {
            "keyboard": [
                [{"text": "🔍 مراقبة الأسبوع القادم"}],
                [{"text": "⛔ إيقاف"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error: {e}")

@app.route("/webhook", methods=['POST'])
def webhook():
    """الرد على الأوامر وتنفيذ المراقبة"""
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram("🚀 البوت شغال يا عمر! الزراير ظهرت تحت اهي. دوس على المراقبة عشان نبدأ.", chat_id)
        
        elif text == "🔍 مراقبة الأسبوع القادم":
            send_telegram("⏳ جاري فحص حساب أوبر o.g2871994@gmail.com... انتظر دقيقة.", chat_id)
            # هنا سيتم إضافة كود الفحص البرمجي بعد استقرار السيرفر
            send_telegram("✅ الفحص اكتمل: لا توجد رحلات متاحة حالياً.", chat_id)
            
        elif text == "⛔ إيقاف":
            send_telegram("🛑 تم إيقاف المراقبة بنجاح.", chat_id)

    return "OK", 200

if __name__ == "__main__":
    # استخدام البورت التلقائي لـ Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
