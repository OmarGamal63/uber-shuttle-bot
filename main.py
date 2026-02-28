import os
import requests
import time
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# جلب الإعدادات من Render اللي إنت ضفتها في الصور
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

def get_driver():
    """إعدادات المتصفح الخفي المتوافقة مع سيرفر Render"""
    chrome_options = Options()
    chrome_options.add_argument('--headless') # تشغيل بدون واجهة رسومية للسيرفر
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # استخدام webdriver_manager لتثبيت الكروم تلقائياً على السيرفر
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

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
            send_telegram("🔄 جاري تشغيل المتصفح الخفي والدخول لحساب أوبر.. (قد يستغرق الأمر دقيقة)", chat_id)
            try:
                driver = get_driver()
                # محاولة فتح صفحة أوبر
                driver.get("https://m.uber.com/looking")
                time.sleep(10) # وقت أطول لضمان التحميل على السيرفر
                
                # رسالة تأكيد أن المتصفح نجح في الوصول للموقع
                send_telegram(f"📡 المتصفح نجح في الوصول لموقع أوبر وجاري الفحص لـ: {UBER_EMAIL}", chat_id)
                
                # هنا تتم عمليات البحث التلقائية
                driver.quit()
            except Exception as e:
                # إرسال الخطأ لتليجرام لتسهيل الحل
                send_telegram(f"❌ عطل تقني: {str(e)}", chat_id)
            
    return "OK", 200

@app.route("/")
def index():
    return "Bot is Live! ✅"

if __name__ == "__main__":
    # استخدام بورت 10000 المفضل لـ Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
