import json
import os
import random
import string
import time

import requests

# ==============================================================================
# --- الإعدادات النهائية (وضع التشغيل الذكي) ---
# ==============================================================================
API_BASE_URL = "https://freefollower.net/api"
ACCOUNTS_FILE = "accounts.txt"
FREE_SERVICE_ID = 196
TIKTOK_PROFILE_LINK = "https://www.tiktok.com/@shahd.store.2?_t=ZS-8zKejIixJeT&_r=1"

# فترة انتظار عشوائية بين كل دورة (بالثواني )
MIN_WAIT_SECONDS = 5
MAX_WAIT_SECONDS = 10

# ==============================================================================
# --- مولّد البيانات البشرية المدمج ---
# ==============================================================================


def generate_ultimate_human_credentials():
    vowels = "aeiou"
    consonants = "bcdfghjklmnprstvwxyz"
    name_part1 = "".join(random.choices(consonants, k=2)) + random.choice(vowels)
    name_part2 = random.choice(consonants) + random.choice(vowels)
    base_name = (name_part1 + name_part2).capitalize()

    birth_year = random.randint(1988, 2005)
    username_style = random.choice(["year", "suffix_number"])
    if username_style == "year":
        username = f"{base_name.lower()}{birth_year}"
    else:
        username = f"{base_name.lower()}_{random.randint(10, 99)}"

    email_domains = ["gmail.com", "outlook.com", "yahoo.com"]
    email = f"{username}@{random.choice(email_domains)}"

    pass_part = "".join(random.choices(string.ascii_lowercase, k=5))
    password_base = pass_part.capitalize()
    password_symbol = random.choice("!@#$*")
    password = f"{password_base}{birth_year}{password_symbol}"

    log(
        f"تم إنشاء بيانات مدمجة: Username='{username}', Password='{password}', Email='{email}'",
        "DEBUG",
    )
    return username, email, password


# ==============================================================================
# --- دوال البوت (مُحسّنة للتشغيل الذكي) ---
# ==============================================================================


def log(message, level="INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "DEBUG": "\033[95m",
        "RESET": "\033[0m",
    }
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"{colors.get(level, colors['INFO'])}[{level:<7}] {timestamp} -> {message}{colors['RESET']}"
    )


def create_new_account():
    log("بدء عملية إنشاء حساب جديد...")
    username, email, password = generate_ultimate_human_credentials()
    payload = {"login": username, "email": email, "password": password}

    try:
        response = requests.post(f"{API_BASE_URL}/register", json=payload, timeout=20)
        log(f"إرسال طلب التسجيل... Status: {response.status_code}", "DEBUG")

        if response.status_code == 201:
            data = response.json()
            api_token = data.get("api_token")
            if api_token:
                log(f"نجاح! تم إنشاء الحساب '{username}'.", "SUCCESS")
                account_info = {
                    "token": api_token,
                    "username": username,
                    "password": password,
                }
                with open(ACCOUNTS_FILE, "a") as f:
                    f.write(json.dumps(account_info) + "\n")
                return account_info

        log(f"فشل إنشاء الحساب. الرد: {response.text}", "ERROR")
        return None
    except requests.exceptions.RequestException as e:
        log(f"خطأ في الشبكة أثناء إنشاء الحساب: {e}", "ERROR")
        return None


def place_order_v2(api_token):
    log(f"بدء إرسال طلب المتابعين...")
    payload = {
        "key": api_token,
        "action": "add",
        "service": FREE_SERVICE_ID,
        "link": TIKTOK_PROFILE_LINK,
        "quantity": 10,
    }

    try:
        response = requests.post(f"{API_BASE_URL}/v2", json=payload, timeout=20)
        log(f"إرسال طلب الخدمة... Status: {response.status_code}", "DEBUG")

        if response.status_code == 200:
            data = response.json()
            if "order" in data:
                log(f"نجاح! تم إرسال الطلب بنجاح. Order ID: {data['order']}", "SUCCESS")
                return True
            elif "error" in data:
                log(f"فشل إرسال الطلب. خطأ من الموقع: {data['error']}", "ERROR")
                return False

        log(f"فشل إرسال الطلب. الرد الكامل: {response.text}", "ERROR")
        return False
    except requests.exceptions.RequestException as e:
        log(f"خطأ في الشبكة أثناء إرسال الطلب: {e}", "ERROR")
        return False


# ==============================================================================
# --- الحلقة الرئيسية (وضع التشغيل الذكي) ---
# ==============================================================================


def main_loop():
    """
    الحلقة الرئيسية التي تعمل بشكل مستمر مع فترة انتظار عشوائية وذكية.
    """
    log("===== بدء تشغيل البوت في [وضع التشغيل الذكي] =====", "SUCCESS")

    while True:
        try:
            log("بدء دورة جديدة...", "INFO")
            active_account = create_new_account()

            if active_account:
                api_token = active_account.get("token")
                if api_token:
                    place_order_v2(api_token)

            # الانتظار العشوائي بعد كل محاولة (ناجحة أو فاشلة)
            wait_time = random.uniform(MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)
            log(f"اكتملت الدورة، سيتم الانتظار لمدة {wait_time:.2f} ثانية...", "INFO")
            time.sleep(wait_time)

        except Exception as e:
            log(f"حدث خطأ غير متوقع: {e}", "ERROR")
            # حتى بعد الخطأ، انتظر فترة عشوائية
            wait_time = random.uniform(MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)
            log(f"سيتم إعادة المحاولة بعد {wait_time:.2f} ثانية...", "WARNING")
            time.sleep(wait_time)


if __name__ == "__main__":
    main_loop()
