import os
import requests
import time
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# جلب الإعدادات من Render
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
UBER_EMAIL = os.environ.get('UBER_EMAIL')
UBER_PASSWORD = os.environ.get('UBER_PASSWORD')

def send_telegram(text, chat_id):
    """إرسال رسائل تليجرام مع الأزرار"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "keyboard": [
                [{"text": "🔍 مراقبة الأسبوع القادم"}, {"text": "🕒 تعديل الموعد"}],
                [{"text": "📊 حالة الرحلات"}, {"text": "⛔ إيقاف"}]
            ],
            "resize_keyboard": True
        }
    }
    requests.post(url, json=payload)

@app.route("/webhook", methods=['POST'])
def webhook():
    """استقبال رسايل تليجرام والرد عليها"""
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram("أهلاً يا عمر! أنا مربوط دلوقت وجاهز أراقب أوبر شاتل. 🚀", chat_id)
        
        elif "pm" in text.lower() or "am" in text.lower():
            send_telegram(f"✅ تم ضبط موعد البحث: *{text}*\nاضغط على '🔍 مراقبة الأسبوع القادم' للبدء.", chat_id)
        
        elif text == "🔍 مراقبة الأسبوع القادم":
            send_telegram("🔄 جاري الدخول لحساب أوبر لفحص المواعيد المتاحة بمرونة 20 دقيقة...", chat_id)
            # هنا الكود بيبدأ يشغل Selenium اللي اتكلمنا عليه
            
    return "OK", 200

@app.route("/")
def index():
    return "Bot is Live! ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
