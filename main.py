import os
import requests
import time
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

def send_telegram(text, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # أضفنا زر الإيقاف عشان لو السيرفر علق تعرف تقفله
    payload = {
        "chat_id": chat_id, 
        "text": text,
        "reply_markup": {"keyboard": [[{"text": "🔍 مراقبة الأسبوع القادم"}], [{"text": "⛔ إيقاف"}]], "resize_keyboard": True}
    }
    requests.post(url, json=payload)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # منع تحميل الصور لتوفير الرامات وتسريع الدخول
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "🔍 مراقبة الأسبوع القادم":
            send_telegram("⚡ جاري تشغيل المحرك السريع.. ثواني وهرد عليك.", chat_id)
            try:
                driver = get_driver()
                driver.set_page_load_timeout(20) 
                driver.get("https://m.uber.com/looking")
                
                # لو فتح الصفحة بنجاح
                send_telegram("✅ وصلت لصفحة أوبر بنجاح! جاري تسجيل الدخول الآن...", chat_id)
                driver.quit()
            except Exception as e:
                send_telegram(f"⚠️ السيرفر مضغوط حالياً، جرب تضغط الزرار كمان دقيقة.", chat_id)
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
