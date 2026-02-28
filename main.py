import os
import requests
import time
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# الإعدادات النهائية المعتمدة
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKQ"

def send_telegram(text, chat_id):
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
    """إعداد متصفح متوافق مع قيود Render"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # إزالة تحديد المسار اليدوي لتجنب الخطأ
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram("🚀 البوت جاهز! اضغط على زرار المراقبة.", chat_id)
        
        elif text == "🔍 مراقبة الأسبوع القادم":
            send_telegram("⏳ جاري محاولة فتح المتصفح وفحص المواعيد...", chat_id)
            try:
                driver = get_driver()
                driver.get("https://m.uber.com/looking")
                time.sleep(5)
                send_telegram("✅ تم الوصول لموقع أوبر بنجاح!", chat_id)
                driver.quit()
            except Exception as e:
                send_telegram(f"❌ خطأ: {str(e)}", chat_id)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
