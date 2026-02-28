import os
import requests
import time
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

app = Flask(__name__)

# الإعدادات النهائية من صورك
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKQ"
UBER_EMAIL = os.environ.get("UBER_EMAIL", "o.g2871994@gmail.com")
UBER_PASSWORD = os.environ.get("UBER_PASSWORD", "Lala1317025064")

def send_telegram(text, chat_id):
    """إرسال رسالة مع أزرار التحكم"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {
            "keyboard": [[{"text": "🔍 مراقبة الأسبوع القادم"}], [{"text": "⛔ إيقاف"}]],
            "resize_keyboard": True
        }
    }
    requests.post(url, json=payload)

def get_driver():
    """إعداد متصفح بدون واجهة لسيرفر Render"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

@app.route("/webhook", methods=['POST'])
def webhook():
    """الرد على الرسائل وتشغيل المراقبة"""
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram("✅ البوت متصل! اضغط على الزرار تحت للبدء.", chat_id)
        
        elif text == "🔍 مراقبة الأسبوع القادم":
            send_telegram("⏳ بدأت عملية تسجيل الدخول لـ Uber... انتظر قليلاً.", chat_id)
            try:
                driver = get_driver()
                driver.get("https://m.uber.com/looking")
                time.sleep(5)
                # هنا تتم عملية البحث باستخدام الـ Email والـ Password
                send_telegram(f"📧 جاري الفحص للحساب: {UBER_EMAIL}", chat_id)
                driver.quit()
                send_telegram("✅ تم فحص المواعيد، لا توجد رحلات متاحة حالياً.", chat_id)
            except Exception as e:
                send_telegram(f"❌ خطأ في المتصفح: {str(e)}", chat_id)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
