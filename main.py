# -*- coding: utf-8 -*-
"""
Uber watcher (Flask + APScheduler + Playwright)
- يشيّك على صفحة مواعيد Uber كل فترة
- أول ما يلاقي الوقت المطلوب → يبعث لك إشعار تيليجرام
- مفيش أي أسرار داخل الكود؛ كله من Environment Variables على Render
"""

import os
import time
from datetime import datetime, timedelta

import requests
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.sync_api import sync_playwright

# ========= قراءات من البيئة =========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
CHECK_URL = os.getenv("CHECK_URL", "").strip()
TARGET_TIME = os.getenv("TARGET_TIME", "12:44 PM").strip().upper()
CHECK_INTERVAL_SEC = int(os.getenv("CHECK_INTERVAL_SEC", "60"))
NOTIFY_COOLDOWN_MIN = int(os.getenv("NOTIFY_COOLDOWN_MIN", "10"))
AUTH_KEY = os.getenv("AUTH_KEY", "")  # مفتاح اختياري لنداء اختبار الإشعار عبر /test

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or not CHECK_URL:
    # هنسيب السيرفر يشتغل لكن هنطبع تحذير واضح في اللوج
    print("⚠️ مفقود TELEGRAM_TOKEN أو TELEGRAM_CHAT_ID أو CHECK_URL في بيئة التشغيل.")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ========= حالة بسيطة في الذاكرة =========
last_notified_at = datetime.min

# ========= ويب سيرفر بسيط =========
app = Flask(__name__)

@app.get("/")
def root():
    return "Uber watcher is running.", 200

@app.get("/health")
def health():
    return jsonify(ok=True, now=datetime.utcnow().isoformat() + "Z")

@app.post("/test")
def test_notify():
    """نداء اختباري آمن: لازم ترسل JSON فيه {"key":"AUTH_KEY"}"""
    body = request.get_json(silent=True) or {}
    if AUTH_KEY and body.get("key") != AUTH_KEY:
        return jsonify(ok=False, error="unauthorized"), 401
    _send_telegram("✅ اختبار: الإشعارات شغالة.")
    return jsonify(ok=True)

# ========= أدوات مساعدة =========
def _send_telegram(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ مش قادر أبعت تيليجرام: المتغيرات ناقصة.")
        return False
    try:
        resp = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=15,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        print("⚠️ فشل إرسال تيليجرام:", e)
        return False

def check_once():
    """يفتح الصفحة بمتصفح Playwright، يقرا النص، ويدوّر على TARGET_TIME"""
    global last_notified_at
    try:
        print(f"[{datetime.utcnow().isoformat()}Z] Checking… target={TARGET_TIME}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = browser.new_context(
                user_agent=("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/120 Safari/537.36")
            )
            page = context.new_page()
            page.goto(CHECK_URL, wait_until="networkidle", timeout=45_000)

            # لو عندك سيلكتور أدق لاحقًا ممكن نستبدل inner_text("body")
            body_text = page.inner_text("body").upper()

            found = TARGET_TIME in body_text
            print(f"target_found={found}")

            if found:
                # تبريد حتى لا تتكرر الرسالة كثيرًا
                if datetime.utcnow() - last_notified_at >= timedelta(minutes=NOTIFY_COOLDOWN_MIN):
                    _send_telegram(f"🎉 الميعاد المطلوب ظهر: {TARGET_TIME}\n🔗 {CHECK_URL}")
                    last_notified_at = datetime.utcnow()

            context.close()
            browser.close()
    except Exception as e:
        print("❌ خطأ أثناء الفحص:", e)

# ========= تشغيل المجدول =========
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(check_once, "interval", seconds=CHECK_INTERVAL_SEC, id="uber_check", max_instances=1)
scheduler.start()

# أول فحص عند الإقلاع
try:
    check_once()
except Exception as e:
    print("Startup check error:", e)

# ========= نقطة دخول Render/Gunicorn =========
if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    # تشغيل Flask مباشر محليًا (Render هيشغّل Gunicorn من أمر البداية)
    app.run(host="0.0.0.0", port=port)
