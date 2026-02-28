import os, requests, pytz, threading, time
from datetime import datetime
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# الإعدادات الأساسية
TARGET_TIME = "12:44"

def check_uber():
    # الرابط اللي جربناه واشتغل معاك
    url = "https://m.uber.com/looking?action=setPickup&pickup=%7B%22latitude%22%3A30.029092%2C%22longitude%22%3A31.483103%7D&drop%5B0%5D=%7B%22latitude%22%3A29.989147%2C%22longitude%22%3A31.215272%7D"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        return "shuttle" in res.text.lower()
    except: return False

@app.route("/webhook", methods=['POST'])
def webhook():
    msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    if "عرض" in msg:
        resp.message(f"البوت شغال من Render ✅\nالموعد المراقب: {TARGET_TIME}")
    return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)