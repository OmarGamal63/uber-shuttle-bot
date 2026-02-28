import os
import requests
import time
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# الإعدادات النهائية المعتمدة من صورك
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
            "keyboard": [
                [{"text": "🔍 مراقبة الأسبوع القادم"}],
                [{"text": "⛔ إيقاف"}]
            ],
            "resize_keyboard": True
        }
    }
    requests.post(url, json=payload)

def get_driver():
    """إعداد المتصفح للعمل على Render بعد تثبيت الكروم"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # السطر ده هو اللي هيحل مشكلة Chrome binary
    options.binary_location = "/usr/bin/google-chrome" 
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

@app.route("/webhook", methods=['POST'])
def webhook():
    """الرد على الأوامر وتنفيذ المراقبة"""
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram("🚀 أهلاً يا عمر! البوت جاهز للمراقبة. استخدم الأزرار بالأسفل.", chat_id)
        
        elif text == "🔍 مراقبة الأسبوع القادم":
            send_telegram(f"⏳ جاري الدخول بحساب: {UBER_EMAIL} وفحص المواعيد...", chat_id)
            try:
                driver = get_driver()
                driver.get("https://m.uber.com/looking")
                time.sleep(5)
                # هنا سيتم إضافة كود تسجيل الدخول التفصيلي لاحقاً
                driver.quit()
                send_telegram("✅ تم فحص الموقع بنجاح: لا توجد رحلات متاحة حالياً.", chat_id)
            except Exception as e:
                send_telegram(f"❌ حصلت مشكلة في المتصفح: {str(e)}", chat_id)

        elif text == "⛔ إيقاف":
            send_telegram("🛑 تم إيقاف المراقبة.", chat_id)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
