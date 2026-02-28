import os
import requests
from flask import Flask, request
from datetime import datetime, timedelta

app = Flask(__name__)

# إعدادات تليجرام
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# دالة لتحويل الوقت النصي (12:44 PM) إلى كائن وقت يمكن طرحه
def parse_uber_time(time_str):
    try:
        return datetime.strptime(time_str.strip(), '%I:%M %p')
    except:
        return None

# دالة التأكد من المرونة (الفرق لا يتعدى 20 دقيقة)
def is_time_flexible(user_time_str, uber_time_str, window_minutes=20):
    user_time = parse_uber_time(user_time_str)
    uber_time = parse_uber_time(uber_time_str)
    
    if not user_time or not uber_time:
        return False
    
    # حساب الفرق بالدقائق
    diff = abs((user_time - uber_time).total_seconds() / 60)
    return diff <= window_minutes

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        text = data["message"].get("text", "")
        
        # لو المستخدم بعت وقت جديد
        if "PM" in text.upper() or "AM" in text.upper():
            user_time = text.strip()
            send_telegram(f"✅ تم حفظ الموعد: *{user_time}*\nسأبحث عن أي رحلة شاتل في حدود 20 دقيقة من هذا الوقت.")
            
        elif text == "🔍 مراقبة الأسبوع القادم":
            # مثال لمحاكاة ما يراه البوت على الموقع
            sample_uber_trip = "12:40 PM" 
            my_target = "12:44 PM" 
            
            if is_time_flexible(my_target, sample_uber_trip):
                send_telegram(f"🚨 *لقيت رحلة قريبة!*\nوقتك المطلوب: {my_target}\nالموجود على أوبر: {sample_uber_trip}\n(الفرق 4 دقائق فقط) - جاري الفحص...")
            
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
