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
UBER_EMAIL = os.environ.get('UBER_EMAIL')
UBER_PASSWORD = os.environ.get('UBER_PASSWORD')

def send_telegram(text, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    # إضافة الأزرار في كل رسالة عشان متختفيش
    payload["reply_markup"] = {
        "keyboard": [[{"text": "🔍 مراقبة الأسبوع القادم"}, {"text": "🕒 تعديل الموعد"}]],
        "resize_keyboard": True
    }
    requests.post(url, json=payload)

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu') # بيقلل استهلاك الرامات جداً
    chrome_options.add_argument('--remote-debugging-port=9222')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram("أهلاً يا عمر! البوت جاهز. ابعت الوقت (مثلاً 12:44pm) ثم اضغط مراقبة.", chat_id)
        
        elif "pm" in text.lower() or "am" in text.lower():
            send_telegram(f"✅ تم حفظ الموعد: {text}", chat_id)
        
        elif text == "🔍 مراقبة الأسبوع القادم":
            send_telegram("⏳ بحاول أفتح أوبر دلوقتي.. خليك متابع الـ Logs.", chat_id)
            try:
                driver = get_driver()
                driver.set_page_load_timeout(30) # عشان ميفضلش متعلق لو الموقع تقيل
                driver.get("https://m.uber.com/looking")
                time.sleep(5)
                # لو وصل لهنا، هيبعتلك تأكيد نجاح
                send_telegram(f"🔓 نجحت في فتح صفحة تسجيل الدخول لـ {UBER_EMAIL}", chat_id)
                driver.quit()
            except Exception as e:
                send_telegram(f"❌ المتصفح واجه مشكلة: {str(e)}", chat_id)
            
    return "OK", 200

@app.route("/")
def index():
    return "Bot is Live! ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
