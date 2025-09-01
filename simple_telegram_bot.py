#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 بوت التليجرام البسيط - أوامر فقط بدون أزرار
👨‍💻 Developer: @zizo0022sasa
🇪🇬 النسخة المصرية - بدون أزرار نهائي
"""

import json
import os
import random
import string
import time
import threading
import asyncio
from datetime import datetime
import logging
import requests

# مكتبات التليجرام
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# ==============================================================================
# 🔐 الإعدادات الأساسية
# ==============================================================================
TELEGRAM_BOT_TOKEN = "7958170099:AAHsSsdd4WiE1MkZMSUQlm0QpzDYDL-rN5Y"
ADMIN_ID = 1124247595  # معرف الأدمن

# إعدادات API
API_BASE_URL = "https://freefollower.net/api"
ACCOUNTS_FILE = "accounts.json"
STATS_FILE = "stats.json"

# إعدادات الخدمة
FREE_SERVICE_ID = 196
DEFAULT_TIKTOK_PROFILE = "https://www.tiktok.com/@shahd.store.2?_t=ZS-8zKejIixJeT&_r=1"

# فترات الانتظار (5-10 ثواني)
MIN_WAIT = 5
MAX_WAIT = 10

# متغيرات عامة
auto_mode = False
stats = {"total_accounts": 0, "total_orders": 0, "active": False}

# ==============================================================================
# إعداد السجلات
# ==============================================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==============================================================================
# دوال مساعدة
# ==============================================================================
def load_stats():
    """تحميل الإحصائيات"""
    global stats
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                stats = json.load(f)
    except:
        pass
    return stats

def save_stats():
    """حفظ الإحصائيات"""
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except:
        pass

def generate_credentials():
    """توليد بيانات حساب عشوائية"""
    vowels = "aeiou"
    consonants = "bcdfghjklmnprstvwxyz"
    
    # توليد اسم عشوائي
    name_part1 = "".join(random.choices(consonants, k=2)) + random.choice(vowels)
    name_part2 = random.choice(consonants) + random.choice(vowels)
    base_name = (name_part1 + name_part2).capitalize()
    
    # سنة الميلاد
    birth_year = random.randint(1988, 2005)
    
    # اسم المستخدم
    username = f"{base_name.lower()}_{random.randint(10, 99)}"
    
    # البريد الإلكتروني
    domains = ["gmail.com", "outlook.com", "yahoo.com"]
    email = f"{username}@{random.choice(domains)}"
    
    # كلمة المرور
    pass_part = "".join(random.choices(string.ascii_lowercase, k=5))
    password = f"{pass_part.capitalize()}{birth_year}{random.choice('!@#$*')}"
    
    return username, email, password

def create_account():
    """إنشاء حساب جديد"""
    username, email, password = generate_credentials()
    
    payload = {
        "login": username,
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/register", json=payload, timeout=20)
        
        if response.status_code == 201:
            data = response.json()
            api_token = data.get("api_token")
            
            if api_token:
                account_info = {
                    "token": api_token,
                    "username": username,
                    "password": password,
                    "created_at": datetime.now().isoformat()
                }
                
                # حفظ الحساب
                accounts = []
                if os.path.exists(ACCOUNTS_FILE):
                    with open(ACCOUNTS_FILE, 'r') as f:
                        accounts = json.load(f)
                
                accounts.append(account_info)
                
                with open(ACCOUNTS_FILE, 'w') as f:
                    json.dump(accounts, f, indent=2)
                
                stats["total_accounts"] += 1
                save_stats()
                
                logger.info(f"✅ تم إنشاء حساب: {username}")
                return account_info
        
        logger.error(f"❌ فشل إنشاء الحساب")
        return None
        
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        return None

def place_order(api_token):
    """إرسال طلب متابعين"""
    payload = {
        "key": api_token,
        "action": "add",
        "service": FREE_SERVICE_ID,
        "link": DEFAULT_TIKTOK_PROFILE,
        "quantity": 10
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/v2", json=payload, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            if "order" in data:
                stats["total_orders"] += 1
                save_stats()
                logger.info(f"✅ تم إرسال الطلب: {data['order']}")
                return True
        
        logger.error(f"❌ فشل إرسال الطلب")
        return False
        
    except Exception as e:
        logger.error(f"❌ خطأ في الطلب: {e}")
        return False

def process_token_input(token_str):
    """معالجة إدخال التوكن من المستخدم"""
    try:
        # محاولة تحليل JSON
        data = json.loads(token_str)
        token = data.get("token")
        if token:
            # إرسال طلب بالتوكن
            success = place_order(token)
            return f"✅ تم استخدام التوكن وإرسال الطلب" if success else "❌ فشل إرسال الطلب بالتوكن"
    except:
        # ربما يكون توكن مباشر
        if len(token_str) > 20:
            success = place_order(token_str)
            return f"✅ تم استخدام التوكن وإرسال الطلب" if success else "❌ فشل إرسال الطلب بالتوكن"
    
    return "❌ صيغة التوكن غير صحيحة"

# ==============================================================================
# دالة التشغيل التلقائي
# ==============================================================================
def auto_worker():
    """عامل التشغيل التلقائي"""
    global auto_mode
    logger.info("🤖 بدء التشغيل التلقائي")
    
    while auto_mode:
        try:
            # إنشاء حساب
            account = create_account()
            
            if account:
                # إرسال طلب
                place_order(account['token'])
            
            # انتظار عشوائي 5-10 ثواني
            wait_time = random.uniform(MIN_WAIT, MAX_WAIT)
            logger.info(f"⏰ انتظار {wait_time:.1f} ثانية")
            time.sleep(wait_time)
            
        except Exception as e:
            logger.error(f"❌ خطأ في التشغيل التلقائي: {e}")
            time.sleep(5)
    
    logger.info("🛑 توقف التشغيل التلقائي")

# ==============================================================================
# أوامر البوت
# ==============================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البداية"""
    user = update.effective_user
    
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ عذراً، هذا البوت خاص بالأدمن فقط!")
        return
    
    load_stats()
    
    message = (
        "🔥 **أهلاً يا كبير!**\n"
        "ده البوت المصري البسيط\n\n"
        "**الأوامر المتاحة:**\n"
        "/start - بدء البوت\n"
        "/new - إنشاء حساب وطلب جديد\n"
        "/auto - تشغيل الوضع التلقائي\n"
        "/stop - إيقاف الوضع التلقائي\n"
        "/stats - عرض الإحصائيات\n"
        "/token {التوكن} - استخدام توكن موجود\n\n"
        "🇪🇬 صُنع في مصر"
    )
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إنشاء طلب جديد"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    await update.message.reply_text("⏳ جاري إنشاء حساب جديد...")
    
    # إنشاء حساب
    account = create_account()
    
    if account:
        # إرسال طلب
        success = place_order(account['token'])
        
        message = (
            f"✅ **تم إنشاء الحساب**\n"
            f"👤 المستخدم: `{account['username']}`\n"
            f"🔑 كلمة السر: `{account['password']}`\n"
            f"📦 الطلب: {'✅ تم الإرسال' if success else '❌ فشل'}"
        )
    else:
        message = "❌ فشل إنشاء الحساب"
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def auto_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تشغيل الوضع التلقائي"""
    global auto_mode
    
    if update.effective_user.id != ADMIN_ID:
        return
    
    if auto_mode:
        await update.message.reply_text("⚠️ التشغيل التلقائي شغال بالفعل!")
        return
    
    auto_mode = True
    stats["active"] = True
    save_stats()
    
    # بدء العامل في خيط منفصل
    thread = threading.Thread(target=auto_worker, daemon=True)
    thread.start()
    
    await update.message.reply_text(
        "🚀 **تم تشغيل الوضع التلقائي**\n"
        "سيتم إنشاء طلب كل 5-10 ثواني\n"
        "بدون حد أقصى للحسابات\n\n"
        "استخدم /stop للإيقاف"
    )

async def auto_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إيقاف الوضع التلقائي"""
    global auto_mode
    
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not auto_mode:
        await update.message.reply_text("⚠️ التشغيل التلقائي متوقف بالفعل!")
        return
    
    auto_mode = False
    stats["active"] = False
    save_stats()
    
    await update.message.reply_text("🛑 **تم إيقاف الوضع التلقائي**")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الإحصائيات"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    load_stats()
    
    status = "🟢 شغال" if stats.get("active", False) else "🔴 متوقف"
    
    message = (
        f"📊 **الإحصائيات**\n"
        f"{'='*20}\n"
        f"👥 الحسابات: {stats.get('total_accounts', 0)}\n"
        f"📦 الطلبات: {stats.get('total_orders', 0)}\n"
        f"🤖 الحالة: {status}\n"
        f"{'='*20}\n"
        f"⚡ بدون حد أقصى للحسابات"
    )
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def use_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استخدام توكن موجود"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    # الحصول على التوكن من الرسالة
    if context.args:
        token_input = " ".join(context.args)
        result = process_token_input(token_input)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text(
            "❌ استخدم الأمر كده:\n"
            "/token YOUR_TOKEN_HERE\n"
            "أو\n"
            '/token {"token": "YOUR_TOKEN", "username": "user", "password": "pass"}'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل العادية"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    text = update.message.text
    
    # التحقق من وجود توكن في الرسالة
    if "{" in text and "token" in text:
        result = process_token_input(text)
        await update.message.reply_text(result)
    elif len(text) > 30:  # ربما يكون توكن
        result = process_token_input(text)
        await update.message.reply_text(result)

# ==============================================================================
# التشغيل الرئيسي
# ==============================================================================
def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل البوت...")
    
    # إنشاء التطبيق
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("new", new_order))
    application.add_handler(CommandHandler("auto", auto_start))
    application.add_handler(CommandHandler("stop", auto_stop))
    application.add_handler(CommandHandler("stats", show_stats))
    application.add_handler(CommandHandler("token", use_token))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info(f"✅ البوت جاهز! Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    
    # بدء البوت
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()