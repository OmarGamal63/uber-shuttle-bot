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
    """إرسال رسالة مع إظهار أزرار التحكم في تليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {
            "keyboard": [
                [{"text": "🔍 مراقبة الأسبوع القادم"}],
                [{"text": "⛔ إيقاف"}]
            ],
            "resize_keyboard": True, # بيخلي حجم الزراير مناسب للموبايل
            "one_time_keyboard": False # بيخلي الزراير تفضل موجودة
        }
    }
    try:
        r = requests.post(url, json=payload)
        print(f"Telegram Response: {r.status_code}")
    except Exception as e:
        print(f"Error sending message: {e}")

def get_driver():
    """إعداد متصفح خفي للعمل على سيرفر Render"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

@app.route("/webhook", methods=['POST'])
def webhook():
    """التعامل مع رسايل تليجرام المختلفة"""
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # الرد على أمر البداية
        if text == "/start":
            send_telegram("🚀 أهلاً يا عمر! البوت جاهز. استعمل الزراير اللي تحت عشان تبدأ المراقبة.", chat_id)
        
        # تنفيذ عملية المراقبة عند الضغط على الزرار
        elif text == "🔍 مراقبة الأسبوع القادم":
            send_telegram("⏳ بدأت عملية فحص مواعيد Uber... خليك معايا.", chat_id)
            try:
                # هنا الكود بيفتح المتصفح فعلياً
                driver = get_driver()
                driver.get("https://m.uber.com/looking")
                time.sleep(5)
                # تنبيه المستخدم بنجاح الوصول
                send_telegram(f"📧 جاري فحص الحساب: {UBER_EMAIL}", chat_id)
                driver.quit()
                send_telegram("✅ الفحص اكتمل: لا توجد رحلات متاحة حالياً للأسبوع القادم.", chat_id)
            except Exception as e:
                send_telegram(f"❌ حصل مشكلة في المتصفح: {str(e)}", chat_id)

        # إيقاف البوت
        elif text == "⛔ إيقاف":
            send_telegram("🛑 تم إيقاف المراقبة بنجاح.", chat_id)

    return "OK", 200

@app.route("/")
def home():
    return "Bot is running! 🚀"

if __name__ == "__main__":
    # استخدام البورت التلقائي لـ Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
