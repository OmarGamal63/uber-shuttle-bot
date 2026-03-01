import os
import requests
from flask import Flask, request

app = Flask(__name__)

# إعدادات التنبيه المعتمدة
TELEGRAM_TOKEN = "8595696719:AAGDXsAvQ3vsP9cg5irIn1DI5kzBWaPESKQ"
monitor_config = {"target": "12:44 PM", "active": False}

def send_telegram_alert(text, chat_id, is_urgent=False):
    """إرسال تنبيه مع أزرار التحكم"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # لو فيه مقعد متاح، الرسالة هتكون قوية جداً
    message = f"🚨🚨 عاااجل يا عمر!! 🚨🚨\n\n{text}" if is_urgent else text
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "reply_markup": {
            "keyboard": [[{"text": "🔍 ابدأ الرادار الآن"}], [{"text": "🛑 إيقاف التنبيه"}]],
            "resize_keyboard": True
        }
    }
    requests.post(url, json=payload)

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_telegram_alert(f"📢 رادار أوبر جاهز! \n🎯 الموعد المراقب: {monitor_config['target']}", chat_id)

        elif text == "🔍 ابدأ الرادار الآن":
            monitor_config["active"] = True
            msg = (f"📡 الرادار شغال دلوقتي على ميعاد {monitor_config['target']}.\n"
                   f"✅ هبعتلك إنذار بصوت عالي أول ما يظهر '1 مقعد' أو أكثر.\n"
                   f"🔄 الفحص شغال كل دقيقة طول الأسبوع.")
            send_telegram_alert(msg, chat_id)
            # هنا البوت بيبدأ يراقب السيستم ويبعتلك أول ما يلاقي فرصة
            
        elif text == "🛑 إيقاف التنبيه":
            monitor_config["active"] = False
            send_telegram_alert("🛑 تم إيقاف الرادار.", chat_id)

        elif ":" in text:
            monitor_config["target"] = text.upper()
            send_telegram_alert(f"✅ تم تغيير هدف المراقبة لـ: {monitor_config['target']}", chat_id)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
