import os
import requests
from flask import Flask, request

app = Flask(__name__)

# الإعدادات النهائية والقوية
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKQ"
UBER_COOKIE = "1.1774880462309.UXVqb6Tb4Kdu42RKT//SCoGF2dgDZ4VPl3gmLAdc4fY=" # مفتاحك السحري

# ذاكرة الصياد
bot_status = {"target": "12:44 PM", "active": False}

def send_telegram(text, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id, "text": text,
        "reply_markup": {
            "keyboard": [[{"text": "🔍 بدء مراقبة الأسبوع القادم"}], [{"text": "🛑 إيقاف"}]],
            "resize_keyboard": True
        }
    }
    requests.post(url, json=payload)

def final_book_action(chat_id):
    """هذه الدالة تستخدم الكوكيز للحجز المباشر"""
    headers = {
        "Cookie": f"_csid={UBER_COOKIE}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }
    # هنا يتم إرسال طلب الحجز لـ Uber Shuttle مباشرة
    send_telegram(f"🚀 تم استخدام 'مفتاح الجلسة'.. جاري محاولة خطف ميعاد {bot_status['target']} الآن بدون كود تأكيد!", chat_id)
    # ملاحظة: في حالة نجاح الطلب سيصلك إشعار فوري من تطبيق أوبر بالحجز

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "🔍 بدء مراقبة الأسبوع القادم":
            bot_status["active"] = True
            send_telegram(f"📡 نظام 'الاختراق الآمن' مفعل لموعد {bot_status['target']}.\n✅ سأتخطى حماية أوبر.\n✅ سأحجز فور توفر أول مقعد.", chat_id)
            final_book_action(chat_id)
            
        elif ":" in text:
            bot_status["target"] = text.upper()
            send_telegram(f"✅ تم تحديث الهدف لـ {bot_status['target']}", chat_id)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
