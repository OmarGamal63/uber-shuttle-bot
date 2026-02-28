import os
import requests
import time
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# التوكن الصحيح (تم تصحيح حرف q الصغير في الآخر)
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKq"

def send_telegram(text, chat_id):
    """إرسال رسالة تليجرام مع أزرار التحكم"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "keyboard": [
                [{"text": "🔍 مراقبة الأسبوع القادم"}],
                [{"text": "⛔ إيقاف"}]
            ],
            "resize_keyboard": True
        }
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending telegram: {e}")

def get_driver():
    """إعدادات المتصفح الخفيف لسيرفر Render"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    # منع تحميل الصور لتسريع الدخول وتوفير الرامات
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

@app.route("/webhook", methods=['POST'])
def webhook():
    """استقبال الرسائل والرد التلقائي"""
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram("أهلاً يا عمر! أنا مربوط دلوقت وجاهز أراقب أوبر شاتل. 🚀", chat_id)
        
        elif text == "🔍 مراقبة الأسبوع القادم":
            send_telegram("⏳ جاري تشغيل المتصفح وفتح موقع أوبر.. انتظر دقيقة.", chat_id)
            try:
                driver = get_driver()
                driver.set_page_load_timeout(30)
                driver.get("https://m.uber.com/looking")
                time.sleep(5)
                
                # رسالة تأكيد الوصول للموقع
                send_telegram("✅ وصلت لصفحة أوبر بنجاح! جاري فحص المواعيد...", chat_id)
                driver.quit()
            except Exception as e:
                send_telegram(f"❌ عطل في المتصفح: {str(e)}", chat_id)
            
    return "OK", 200

@app.route("/")
def index():
    return "Bot is Live! ✅"

if __name__ == "__main__":
    # البورت الصحيح لسيرفر Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
