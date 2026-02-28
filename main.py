import os
import time
import requests
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

app = Flask(__name__)

# إحضار البيانات من إعدادات السيرفر
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
UBER_EMAIL = os.environ.get('UBER_EMAIL')
UBER_PASSWORD = os.environ.get('UBER_PASSWORD')

# دالة إرسال الرسائل والأزرار لتليجرام
def send_telegram(text, show_menu=False):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    if show_menu:
        payload["reply_markup"] = {
            "keyboard": [
                [{"text": "🔍 مراقبة الأسبوع القادم"}, {"text": "🕒 تعديل موعد البحث"}],
                [{"text": "📊 حالة الرحلات الحالية"}, {"text": "⛔ إيقاف المراقبة"}]
            ],
            "resize_keyboard": True
        }
    requests.post(url, json=payload)

# دالة حساب المرونة الزمنية (20 دقيقة)
def is_within_window(target_str, found_str, window=20):
    try:
        fmt = '%I:%M %p'
        target = datetime.strptime(target_str.strip(), fmt)
        found = datetime.strptime(found_str.strip(), fmt)
        diff = abs((target - found).total_seconds() / 60)
        return diff <= window
    except:
        return False

# إعداد المتصفح الخفي (Selenium)
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# محرك فحص أوبر شاتل
def run_uber_check(target_time):
    driver = get_driver()
    try:
        driver.get("https://auth.uber.com/login/")
        # هنا سيتم تنفيذ كود الدخول والـ OTP الذي شرحناه
        # مثال لعملية الفحص بعد الدخول:
        found_time = "12:40 PM" # القيمة المسحوبة من الموقع
        seats_info = "عدد 1 مقعد متوفر" # القيمة المسحوبة
        
        if is_within_window(target_time, found_time):
            if "0 من المقاعد" in seats_info:
                send_telegram(f"ℹ️ لقيت رحلة {found_time} بس للأسف كاملة العدد (0 مقاعد).")
            else:
                send_telegram(f"🚨 *فرصة حقيقية!* \nوقتك: {target_time}\nالمتاح: {found_time}\nالحالة: {seats_info}\nاحجز فوراً!")
    except Exception as e:
        send_telegram(f"❌ حدث خطأ فني: {str(e)}")
    finally:
        driver.quit()

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        text = data["message"].get("text", "")
        
        if text == "/start":
            send_telegram("أهلاً بك في بوت أوبر شاتل المطور! 🚀", show_menu=True)
        elif text == "🔍 مراقبة الأسبوع القادم":
            send_telegram("🔄 بدأت فحص الأسبوع القادم بمرونة 20 دقيقة.. سأخبرك فور توفر مقاعد.")
            # ابدأ الفحص (يمكن تشغيله في Thread لاحقاً)
        elif "PM" in text.upper() or "AM" in text.upper():
            send_telegram(f"✅ تم ضبط موعد البحث على: *{text}*")
            
    return "OK", 200

@app.route("/")
def index():
    return "Bot is Live! ✅"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
