import os
import requests
import time
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# التوكن الصحيح مكتوب يدوياً لضمان الربط
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKq"

def send_telegram(text, chat_id):
    """إرسال رد مباشر وتنبيه في الـ Logs لحالة الإرسال"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {
            "keyboard": [[{"text": "🔍 مراقبة الأسبوع القادم"}], [{"text": "⛔ إيقاف"}]],
            "resize_keyboard": True
        }
    }
    try:
        response = requests.post(url, json=payload)
        # السطر ده هيخلينا نشوف في الـ Logs لو تليجرام رفض الرسالة
        print(f"Telegram Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Send Error: {e}")

def get_driver():
    """إعدادات المتصفح الخفيف لمنع تهنيج السيرفر"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # منع الصور لتسريع فتح أوبر
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

@app.route("/webhook", methods=['POST'])
def webhook():
    """استقبال الرسائل والرد عليها فوراً"""
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start" or text == "فحص":
            send_telegram("✅ البوت شغال والربط سليم! دوس على الزرار عشان أبدأ أراقب أوبر.", chat_id)
        
        elif text == "🔍 مراقبة الأسبوع القادم":
            send_telegram("⏳ ثواني.. بفتح صفحة أوبر دلوقتي.", chat_id)
            try:
                driver = get_driver()
                driver.get("https://m.uber.com/looking")
                time.sleep(5)
                send_telegram("🔓 وصلت للموقع بنجاح! جاري البحث عن الرحلات...", chat_id)
                driver.quit()
            except Exception as e:
                send_telegram(f"❌ حصلت مشكلة في فتح الموقع: {str(e)}", chat_id)
                
    return "OK", 200

@app.route("/")
def home():
    return "Bot is running! 🚀"

if __name__ == "__main__":
    # استخدام بورت Render التلقائي
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
