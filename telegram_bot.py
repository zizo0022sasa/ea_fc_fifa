#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 بوت التليجرام المصري النهائي - نسخة محسنة
👨‍💻 Developer: @zizo0022sasa
🇪🇬 صُنع في مصر
"""

import asyncio
import json
import logging
import os
import random
import re
import string
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ==============================================================================
# 🔐 الإعدادات
# ==============================================================================
TELEGRAM_BOT_TOKEN = "7958170099:AAG-aAVxqOTQmsvrP7viKIo0-KP0AzJUGDE"  # التوكن الجديد
ADMIN_ID = 1124247595

# API Settings
API_BASE_URL = "https://freefollower.net/api"
TOKENS_FILE = "tokens.json"
ACCOUNTS_FILE = "accounts.json"
STATS_FILE = "stats.json"

# Service Settings
FREE_SERVICE_ID = 196

# Account Creation Settings
TOKEN_COOLDOWN_HOURS = 25  # فترة الانتظار بين استخدامات التوكن
MIN_WAIT_SECONDS = 5       # أقل وقت انتظار بين الطلبات
MAX_WAIT_SECONDS = 10      # أكبر وقت انتظار بين الطلبات
MAX_ACCOUNT_CREATION_ATTEMPTS = 3  # محاولات إنشاء الحساب قبل الاستسلام

# ==============================================================================
# إعداد السجلات
# ==============================================================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ==============================================================================
# 🛠️ مولد الحسابات (من pro_bot.py بالظبط)
# ==============================================================================

def generate_ultimate_human_credentials():
    """توليد بيانات حساب بشرية واقعية - نفس الكود من pro_bot.py"""
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

    email_domains = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com", "icloud.com"]
    email = f"{username}@{random.choice(email_domains)}"

    pass_part = "".join(random.choices(string.ascii_lowercase, k=5))
    password_base = pass_part.capitalize()
    password_symbol = random.choice("!@#$*")
    password = f"{password_base}{birth_year}{password_symbol}"

    logger.info(
        f"تم إنشاء بيانات: Username='{username}', Password='{password}', Email='{email}'"
    )
    return username, email, password

# ==============================================================================
# 🔑 مدير التوكنات المتقدم
# ==============================================================================

class TokenManager:
    """مدير التوكنات مع إنشاء حسابات تلقائي وإدارة الكابتشا"""

    def __init__(self):
        self.tokens = self.load_tokens()
        self.accounts = self.load_accounts()
        self.captcha_cooldown = {}  # تتبع محاولات الكابتشا

    def load_tokens(self) -> List[Dict]:
        """تحميل التوكنات من الملف"""
        try:
            if os.path.exists(TOKENS_FILE):
                with open(TOKENS_FILE, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    return []
        except Exception as e:
            logger.error(f"خطأ في تحميل التوكنات: {e}")
        return []

    def load_accounts(self) -> List[Dict]:
        """تحميل الحسابات من الملف"""
        try:
            if os.path.exists(ACCOUNTS_FILE):
                with open(ACCOUNTS_FILE, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    return []
        except Exception as e:
            logger.error(f"خطأ في تحميل الحسابات: {e}")
        return []

    def save_tokens(self):
        """حفظ التوكنات في سطر واحد لكل توكن"""
        try:
            with open(TOKENS_FILE, "w") as f:
                # حفظ كل توكن في سطر واحد
                f.write("[\n")
                for i, token in enumerate(self.tokens):
                    json_str = json.dumps(token, ensure_ascii=False)
                    if i < len(self.tokens) - 1:
                        f.write(f"  {json_str},\n")
                    else:
                        f.write(f"  {json_str}\n")
                f.write("]")
        except Exception as e:
            logger.error(f"خطأ في حفظ التوكنات: {e}")

    def save_accounts(self):
        """حفظ الحسابات في سطر واحد لكل حساب"""
        try:
            with open(ACCOUNTS_FILE, "w") as f:
                # حفظ كل حساب في سطر واحد
                f.write("[\n")
                for i, account in enumerate(self.accounts):
                    json_str = json.dumps(account, ensure_ascii=False)
                    if i < len(self.accounts) - 1:
                        f.write(f"  {json_str},\n")
                    else:
                        f.write(f"  {json_str}\n")
                f.write("]")
        except Exception as e:
            logger.error(f"خطأ في حفظ الحسابات: {e}")

    def validate_token_format(self, token: str) -> bool:
        """التحقق من صيغة التوكن - 50-70 حرف alphanumeric"""
        if not token:
            return False
        if not re.match(r'^[a-zA-Z0-9]{50,70}$', token):
            return False
        return True

    def should_retry_account_creation(self) -> bool:
        """التحقق من إمكانية إعادة محاولة إنشاء الحساب"""
        now = datetime.now()
        
        # التحقق من آخر محاولة فاشلة
        last_captcha = self.captcha_cooldown.get("last_captcha_error")
        if last_captcha:
            last_captcha_time = datetime.fromisoformat(last_captcha)
            time_diff = (now - last_captcha_time).total_seconds()
            
            # الانتظار 60 ثانية بعد كل خطأ كابتشا
            if time_diff < 60:
                return False
        
        return True

    def create_new_account(self) -> Optional[Dict]:
        """إنشاء حساب جديد تلقائياً مع التعامل مع الكابتشا"""
        
        # التحقق من إمكانية المحاولة
        if not self.should_retry_account_creation():
            logger.warning("⏰ الانتظار قبل محاولة إنشاء حساب جديد...")
            return None
        
        for attempt in range(MAX_ACCOUNT_CREATION_ATTEMPTS):
            logger.info(f"🔄 محاولة إنشاء حساب رقم {attempt + 1}/{MAX_ACCOUNT_CREATION_ATTEMPTS}...")
            
            username, email, password = generate_ultimate_human_credentials()
            
            payload = {
                "login": username,
                "email": email,
                "password": password
            }

            try:
                # إضافة تأخير عشوائي قبل الطلب
                time.sleep(random.uniform(2, 5))
                
                response = requests.post(
                    f"{API_BASE_URL}/register",
                    json=payload,
                    timeout=20,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    }
                )
                
                logger.info(f"إرسال طلب التسجيل... Status: {response.status_code}")

                if response.status_code == 201:
                    data = response.json()
                    api_token = data.get("api_token")
                    if api_token:
                        logger.info(f"✅ نجاح! تم إنشاء الحساب '{username}'.")
                        
                        # حفظ التوكن في سطر واحد
                        new_token = {"token": api_token, "username": username, "email": email, "password": password, "created_at": datetime.now().isoformat(), "last_used": None, "use_count": 0, "auto_created": True}
                        
                        self.tokens.append(new_token)
                        self.save_tokens()
                        
                        # حفظ معلومات الحساب في سطر واحد
                        account_info = {"token": api_token, "username": username, "email": email, "password": password, "created_at": datetime.now().isoformat()}
                        
                        self.accounts.append(account_info)
                        self.save_accounts()
                        
                        # مسح سجل الكابتشا عند النجاح
                        self.captcha_cooldown = {}
                        
                        return new_token
                
                elif response.status_code == 429:
                    # خطأ كابتشا أو rate limit
                    error_data = response.json()
                    if "need_captcha" in str(error_data):
                        logger.warning(f"⚠️ الموقع يطلب كابتشا - محاولة {attempt + 1}")
                        self.captcha_cooldown["last_captcha_error"] = datetime.now().isoformat()
                        
                        # الانتظار قبل المحاولة التالية
                        wait_time = random.uniform(10, 20)
                        logger.info(f"⏰ الانتظار {wait_time:.1f} ثانية...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"❌ Rate limit: {error_data}")
                        time.sleep(30)
                else:
                    logger.error(f"فشل إنشاء الحساب. الرد: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"خطأ في الشبكة: {e}")
                time.sleep(5)
        
        logger.error("❌ فشلت جميع محاولات إنشاء الحساب")
        return None

    def add_token(self, token_data: str) -> str:
        """إضافة توكن جديد"""
        try:
            # محاولة تحليل JSON
            if token_data.startswith("{"):
                data = json.loads(token_data)
                token = data.get("token", "")
                username = data.get("username", "unknown")
                email = data.get("email", "")
                password = data.get("password", "")
            else:
                # توكن مباشر
                token = token_data.strip()
                username = "imported"
                email = ""
                password = ""

            # التحقق من صيغة التوكن
            if not self.validate_token_format(token):
                return (
                    "❌ صيغة التوكن غير صحيحة!\n"
                    "التوكن لازم يكون حوالي 60 حرف وأرقام بس"
                )

            # التحقق من التكرار
            for existing in self.tokens:
                if existing.get("token") == token:
                    return "⚠️ التوكن موجود بالفعل!"

            # إضافة التوكن في سطر واحد
            new_token = {"token": token, "username": username, "email": email, "password": password, "created_at": datetime.now().isoformat(), "last_used": None, "use_count": 0, "auto_created": False}

            self.tokens.append(new_token)
            self.save_tokens()

            # حفظ معلومات الحساب إذا كانت متوفرة
            if email and password:
                account = {"username": username, "email": email, "password": password, "token": token, "created_at": datetime.now().isoformat()}
                self.accounts.append(account)
                self.save_accounts()

            return f"✅ تم إضافة التوكن بنجاح!\n👤 المستخدم: {username}\n📊 إجمالي التوكنات: {len(self.tokens)}"

        except json.JSONDecodeError:
            return "❌ صيغة JSON غير صحيحة!"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"

    def get_available_token(self) -> Optional[Dict]:
        """الحصول على توكن متاح أو إنشاء حساب جديد"""
        now = datetime.now()
        
        # البحث عن توكن متاح (لم يستخدم منذ 25 ساعة)
        for token_data in self.tokens:
            last_used = token_data.get("last_used")
            
            if last_used is None:
                # توكن جديد لم يستخدم بعد
                logger.info(f"✅ استخدام توكن جديد: {token_data.get('username')}")
                return token_data
            
            try:
                last_used_time = datetime.fromisoformat(last_used)
                time_diff = now - last_used_time
                
                if time_diff.total_seconds() >= (TOKEN_COOLDOWN_HOURS * 3600):
                    # التوكن متاح للاستخدام
                    logger.info(f"✅ استخدام توكن متاح: {token_data.get('username')}")
                    return token_data
            except:
                continue
        
        # لا يوجد توكن متاح، نحاول إنشاء حساب جديد
        logger.info("⚠️ لا توجد توكنات متاحة، جاري محاولة إنشاء حساب جديد...")
        
        # المحاولة مع تأخير للتغلب على الكابتشا
        new_token = self.create_new_account()
        
        if not new_token:
            logger.warning("⚠️ تعذر إنشاء حساب جديد - قد يكون بسبب الكابتشا")
        
        return new_token

    def mark_used(self, token: str):
        """تحديد التوكن كمستخدم"""
        for t in self.tokens:
            if t["token"] == token:
                t["last_used"] = datetime.now().isoformat()
                t["use_count"] = t.get("use_count", 0) + 1
        self.save_tokens()

    def get_stats(self) -> Dict:
        """إحصائيات التوكنات"""
        total = len(self.tokens)
        now = datetime.now()
        
        available = 0
        for token in self.tokens:
            last_used = token.get("last_used")
            if last_used is None:
                available += 1
            else:
                try:
                    last_used_time = datetime.fromisoformat(last_used)
                    if (now - last_used_time).total_seconds() >= (TOKEN_COOLDOWN_HOURS * 3600):
                        available += 1
                except:
                    pass
        
        auto_created = sum(1 for t in self.tokens if t.get("auto_created", False))
        
        return {
            "total": total,
            "available": available,
            "on_cooldown": total - available,
            "auto_created": auto_created,
            "total_accounts": len(self.accounts)
        }

# ==============================================================================
# 🚀 معالج الطلبات (نفس نظام pro_bot.py)
# ==============================================================================

class OrderProcessor:
    """معالج الطلبات مع نظام الانتظار الذكي من pro_bot.py"""

    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager
        self.stats = self.load_stats()

    def load_stats(self) -> Dict:
        """تحميل الإحصائيات"""
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, "r") as f:
                    return json.load(f)
        except:
            pass
        return {
            "total_orders": 0,
            "successful": 0,
            "failed": 0,
            "auto_accounts_created": 0
        }

    def save_stats(self):
        """حفظ الإحصائيات"""
        try:
            with open(STATS_FILE, "w") as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass

    def validate_tiktok_link(self, link: str) -> bool:
        """التحقق من صحة رابط TikTok"""
        patterns = [
            r"https?://(?:www\.)?tiktok\.com/@[\w\.-]+",
            r"https?://(?:www\.)?tiktok\.com/[\w\.-]+",
            r"https?://vm\.tiktok\.com/[\w]+",
            r"@[\w\.-]+",
        ]

        for pattern in patterns:
            if re.match(pattern, link):
                return True
        return False

    def calculate_accounts_needed(self, followers: int) -> int:
        """حساب عدد الحسابات المطلوبة"""
        accounts = followers // 10
        if followers % 10 > 0:
            accounts += 1
        return accounts

    def place_order_v2(self, api_token: str, link: str, quantity: int = 10) -> bool:
        """إرسال طلب واحد - نفس الكود من pro_bot.py"""
        logger.info(f"📤 بدء إرسال طلب المتابعين...")
        
        payload = {
            "key": api_token,
            "action": "add",
            "service": FREE_SERVICE_ID,
            "link": link,
            "quantity": quantity,
        }

        try:
            response = requests.post(
                f"{API_BASE_URL}/v2",
                json=payload,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            
            logger.info(f"إرسال طلب الخدمة... Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if "order" in data:
                    logger.info(f"✅ نجاح! تم إرسال الطلب. Order ID: {data['order']}")
                    return True
                elif "error" in data:
                    logger.error(f"❌ فشل: {data['error']}")
                    return False

            logger.error(f"❌ فشل الطلب. الرد: {response.text}")
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ خطأ في الشبكة: {e}")
            return False

    async def process_bulk_order_async(self, link: str, total_followers: int, update_callback=None) -> Dict:
        """معالجة طلب كبير - العدّاد يتقدم فقط عند النجاح"""
        accounts_needed = self.calculate_accounts_needed(total_followers)

        results = {
            "requested": total_followers,
            "accounts_needed": accounts_needed,
            "successful": 0,
            "failed": 0,
            "tokens_used": [],
            "auto_accounts_created": 0,
            "no_tokens_available": 0
        }

        # العداد الفعلي للطلبات الناجحة فقط
        successful_count = 0
        attempt_count = 0
        
        while successful_count < accounts_needed:
            attempt_count += 1
            
            # حماية من الحلقة اللانهائية
            if attempt_count > accounts_needed * 3:
                logger.warning("⚠️ تجاوزنا الحد الأقصى للمحاولات")
                break
            
            logger.info(f"🔄 محاولة رقم {attempt_count} - نجح حتى الآن: {successful_count}/{accounts_needed}")
            
            # الحصول على توكن أو إنشاء حساب جديد
            token_data = self.token_manager.get_available_token()

            if not token_data:
                results["no_tokens_available"] += 1
                logger.warning("❌ لا توجد توكنات متاحة!")
                
                if update_callback:
                    await update_callback(
                        f"⚠️ المحاولة {attempt_count}\n"
                        f"❌ لا توجد توكنات متاحة\n"
                        f"✅ نجح حتى الآن: {successful_count}/{accounts_needed}\n"
                        f"جاري المحاولة مرة أخرى..."
                    )
                
                # الانتظار قبل المحاولة التالية
                wait_time = random.uniform(MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)
                await asyncio.sleep(wait_time)
                continue

            # تتبع الحسابات المُنشأة تلقائياً
            if token_data.get("auto_created", False):
                results["auto_accounts_created"] += 1
                self.stats["auto_accounts_created"] = self.stats.get("auto_accounts_created", 0) + 1

            token = token_data["token"]
            username = token_data.get("username", "unknown")
            
            # إرسال تحديث قبل الطلب
            if update_callback:
                await update_callback(
                    f"⏳ المحاولة {attempt_count}\n"
                    f"✅ التقدم: {successful_count}/{accounts_needed}\n"
                    f"👤 الحساب: {username}\n"
                    f"{'🆕 حساب جديد' if token_data.get('auto_created') else '📱 حساب موجود'}\n"
                    f"⏰ جاري الإرسال..."
                )
            
            # إرسال الطلب
            success = self.place_order_v2(token, link, 10)

            if success:
                # نجح الطلب - نزيد العداد
                successful_count += 1
                results["successful"] += 1
                results["tokens_used"].append(username)
                self.token_manager.mark_used(token)
                self.stats["successful"] += 1
                
                if update_callback:
                    await update_callback(
                        f"✅ نجح الطلب!\n"
                        f"📊 التقدم: {successful_count}/{accounts_needed}\n"
                        f"👤 الحساب: {username}\n"
                        f"👥 المتابعين المرسلين: {successful_count * 10}"
                    )
            else:
                # فشل الطلب - لا نزيد العداد
                results["failed"] += 1
                self.stats["failed"] += 1
                
                if update_callback:
                    await update_callback(
                        f"❌ فشل الطلب\n"
                        f"📊 التقدم: {successful_count}/{accounts_needed} (لم يتغير)\n"
                        f"👤 الحساب: {username}\n"
                        f"🔄 سيتم المحاولة مع حساب آخر..."
                    )

            self.stats["total_orders"] += 1

            # الانتظار العشوائي بين الطلبات
            if successful_count < accounts_needed:
                wait_time = random.uniform(MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)
                logger.info(f"⏰ انتظار {wait_time:.1f} ثانية...")
                
                if update_callback:
                    await update_callback(
                        f"⏰ انتظار {wait_time:.1f} ثانية...\n"
                        f"📊 التقدم الفعلي: {successful_count}/{accounts_needed}"
                    )
                
                await asyncio.sleep(wait_time)

        self.save_stats()
        return results

# ==============================================================================
# 🤖 البوت الرئيسي
# ==============================================================================

class TelegramBot:
    """البوت الرئيسي بدون أزرار"""

    def __init__(self):
        self.token_manager = TokenManager()
        self.order_processor = OrderProcessor(self.token_manager)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        user = update.effective_user

        if user.id != ADMIN_ID:
            await update.message.reply_text("❌ عذراً، هذا البوت خاص بالأدمن فقط!")
            return

        message = (
            "🔥 **أهلاً يا كبير!**\n"
            "ده البوت المصري النهائي\n\n"
            "**الأوامر المتاحة:**\n"
            "`/follow [لينك] [عدد]` - طلب متابعين\n"
            "`/token [توكن]` - إضافة توكن\n"
            "`/stats` - عرض الإحصائيات\n\n"
            "**الميزات الجديدة:**\n"
            "✅ العدّاد يتقدم فقط عند النجاح\n"
            "✅ بيانات التوكن في سطر واحد\n"
            "✅ إنشاء حسابات تلقائياً\n"
            "✅ انتظار 5-10 ثواني بين الطلبات\n"
            "✅ تحديثات مباشرة لكل طلب\n\n"
            "**مثال:**\n"
            "`/follow https://tiktok.com/@username 1000`\n\n"
            "🇪🇬 صُنع بكل حب في مصر"
        )

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    async def follow_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة طلب المتابعين - العداد يتقدم فقط عند النجاح"""
        if update.effective_user.id != ADMIN_ID:
            return

        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ **صيغة غلط!**\n\n"
                "الصيغة الصحيحة:\n"
                "`/follow [لينك] [عدد]`\n\n"
                "مثال:\n"
                "`/follow https://tiktok.com/@username 1000`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        link = context.args[0]
        
        try:
            quantity = int(context.args[1])
        except ValueError:
            await update.message.reply_text(
                "❌ العدد لازم يكون رقم!",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        if not self.order_processor.validate_tiktok_link(link):
            await update.message.reply_text("❌ اللينك غير صحيح!")
            return

        if quantity <= 0:
            await update.message.reply_text("❌ العدد لازم يكون أكبر من صفر!")
            return

        accounts_needed = self.order_processor.calculate_accounts_needed(quantity)
        token_stats = self.token_manager.get_stats()

        # رسالة البداية
        start_msg = await update.message.reply_text(
            f"🚀 **بدء المعالجة**\n\n"
            f"📱 اللينك: `{link}`\n"
            f"👥 المتابعين المطلوبين: {quantity}\n"
            f"📊 الحسابات المطلوبة: {accounts_needed}\n"
            f"🎫 التوكنات المتاحة: {token_stats['available']}\n\n"
            f"⚠️ **ملاحظة:** العدّاد يتقدم فقط عند النجاح\n"
            f"⏳ جاري المعالجة...",
            parse_mode=ParseMode.MARKDOWN,
        )

        # دالة لإرسال التحديثات
        async def send_update(msg: str):
            try:
                await start_msg.edit_text(
                    f"🔄 **التحديث المباشر**\n\n{msg}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass  # تجاهل أخطاء التحديث

        # معالجة الطلب مع التحديثات المباشرة
        results = await self.order_processor.process_bulk_order_async(
            link, 
            quantity,
            update_callback=send_update
        )

        # عرض النتائج النهائية
        success_rate = (
            (results["successful"] / accounts_needed * 100)
            if accounts_needed > 0
            else 0
        )

        final_message = (
            f"✅ **اكتمل الطلب!**\n"
            f"{'='*20}\n\n"
            f"📊 **النتائج النهائية:**\n"
            f"• طلبات ناجحة: {results['successful']}/{accounts_needed}\n"
            f"• محاولات فاشلة: {results['failed']}\n"
            f"• معدل النجاح: {success_rate:.1f}%\n"
            f"• متابعين تم إرسالهم: {results['successful'] * 10}\n"
        )

        if results["auto_accounts_created"] > 0:
            final_message += f"• حسابات جديدة: {results['auto_accounts_created']}\n"
        
        if results.get("no_tokens_available", 0) > 0:
            final_message += f"• محاولات بدون توكنات: {results['no_tokens_available']}\n"

        final_message += "\n"

        if results["tokens_used"]:
            final_message += "**📝 الحسابات الناجحة:**\n"
            for i, username in enumerate(results["tokens_used"][:10], 1):
                final_message += f"{i}. {username}\n"

            if len(results["tokens_used"]) > 10:
                remaining = len(results["tokens_used"]) - 10
                final_message += f"... و {remaining} آخرين\n"

        await start_msg.edit_text(final_message, parse_mode=ParseMode.MARKDOWN)

    async def add_tokens(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إضافة توكنات جديدة"""
        if update.effective_user.id != ADMIN_ID:
            return

        if not context.args:
            await update.message.reply_text(
                "📝 **طريقة إضافة التوكنات:**\n\n"
                "**طريقة 1 - توكن مباشر:**\n"
                "`/token YOUR_TOKEN_HERE`\n\n"
                "**طريقة 2 - JSON كامل (سطر واحد):**\n"
                '`/token {"token":"TOKEN","username":"user","email":"email@domain.com","password":"pass"}`\n\n'
                "التوكن لازم يكون حوالي 60 حرف وأرقام",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        token_data = " ".join(context.args)
        result = self.token_manager.add_token(token_data)
        await update.message.reply_text(result)

    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإحصائيات"""
        if update.effective_user.id != ADMIN_ID:
            return

        token_stats = self.token_manager.get_stats()
        order_stats = self.order_processor.stats

        message = (
            f"📊 **الإحصائيات الكاملة**\n"
            f"{'='*25}\n\n"
            f"**🎫 التوكنات:**\n"
            f"• الإجمالي: {token_stats['total']}\n"
            f"• المتاح: {token_stats['available']}\n"
            f"• في فترة الانتظار: {token_stats['on_cooldown']}\n"
            f"• مُنشأة تلقائياً: {token_stats['auto_created']}\n\n"
            f"**👤 الحسابات:**\n"
            f"• إجمالي الحسابات: {token_stats['total_accounts']}\n\n"
            f"**📦 الطلبات:**\n"
            f"• الإجمالي: {order_stats['total_orders']}\n"
            f"• الناجح: {order_stats['successful']}\n"
            f"• الفاشل: {order_stats['failed']}\n"
            f"• حسابات تم إنشاؤها: {order_stats.get('auto_accounts_created', 0)}\n\n"
        )

        if order_stats["total_orders"] > 0:
            success_rate = (
                order_stats["successful"] / order_stats["total_orders"]
            ) * 100
            message += f"**📈 معدل النجاح:** {success_rate:.1f}%\n"

        message += "\n⚡ النظام يعمل بكامل طاقته"

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    async def handle_token_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """معالج رسائل التوكنات المباشرة"""
        if update.effective_user.id != ADMIN_ID:
            return

        text = update.message.text

        # التحقق من وجود توكن
        if "{" in text and "token" in text:
            result = self.token_manager.add_token(text)
            await update.message.reply_text(result)
        elif len(text) >= 50 and len(text) <= 70:
            # ربما يكون توكن
            if re.match(r'^[a-zA-Z0-9]+$', text.strip()):
                result = self.token_manager.add_token(text)
                await update.message.reply_text(result)

# ==============================================================================
# 🚀 التشغيل الرئيسي
# ==============================================================================

def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل البوت المصري النهائي...")
    logger.info("📍 نظام pro_bot.py مفعّل")
    logger.info("⏰ انتظار 5-10 ثواني بين الطلبات")
    logger.info("✅ العدّاد يتقدم فقط عند النجاح")
    logger.info("📝 البيانات في سطر واحد")

    # إنشاء البوت
    bot = TelegramBot()

    # إنشاء التطبيق
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # إضافة المعالجات
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("follow", bot.follow_order))
    application.add_handler(CommandHandler("token", bot.add_tokens))
    application.add_handler(CommandHandler("stats", bot.show_stats))
    
    # معالج الرسائل المباشرة للتوكنات
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID),
            bot.handle_token_message,
        )
    )

    logger.info(f"✅ البوت جاهز!")
    logger.info("🇪🇬 صُنع بكل حب في مصر")

    # بدء البوت
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()