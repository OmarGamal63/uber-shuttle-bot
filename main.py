import os
import time
import requests
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime

app = Flask(__name__)

# جلب البيانات من إعدادات Render
UBER_EMAIL = os.environ.get('UBER_EMAIL')
UBER_PASSWORD = os.environ.get('UBER_PASSWORD')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def start_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # تشغيل بدون شاشة للسيرفر
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def check_uber_shuttle(target_time):
    driver = start_browser()
    try:
        driver.get("https://www.uber.com/explore/shuttle") # رابط الاستكشاف
        time.sleep(5) 
        
        # هنا البوت بيبدأ يقرأ المواعيد المكتوبة زي 12:44 PM
        # ويقارنها بمرونة الـ 20 دقيقة اللي اتفقنا عليها
        
        found_shuttle = "12:40 PM" # مثال للي لاقاه
        seats_left = "1 مقعد متوفر" # مثال للحالة
        
        if "0 من المقاعد" in seats_left:
            print("الرحلة موجودة بس للاسف كاملة العدد")
        elif "مقعد متوفر" in seats_left:
            send_telegram(f"🚨 *لقيتلك رحلة!* \nوقتك: {target_time}\nالمتاح: {found_shuttle}\nالحالة: {seats_left}\nاحجز بسرعة!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

@app.route('/')
def home():
    return "Uber Selenium Bot is Running! 🚀"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
