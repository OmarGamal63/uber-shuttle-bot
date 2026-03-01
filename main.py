import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKQ"

def send_urgent_alert(chat_id):
    """إرسال تنبيه فوري ومزعج"""
    msg = (
        "🚨🚨🚨🚨🚨🚨🚨🚨🚨\n"
        "عمرررررررررر! الرحلة فتحت فوراااا!\n"
        "🎯 الموعد: 12:44 PM\n"
        "🪑 فيه مقاعد متاحة دلوقتي!\n"
        "🏃‍♂️ افتح أوبر واحجز قبل ما حد يخطفها!\n"
        "🚨🚨🚨🚨🚨🚨🚨🚨🚨"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": msg})

@app.route("/test_alert", methods=['GET'])
def test_alert():
    """رابط يدوي لعمل تنبيه وهمي للتجربة"""
    chat_id = "6064560341" # ايدي تليجرام بتاعك
    send_urgent_alert(chat_id)
    return "✅ التنبيه اتبعت لتليجرام حالا!", 200

@app.route("/webhook", methods=['POST'])
def webhook():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
