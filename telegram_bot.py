#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 بوت التليجرام المصري - نظام الطابور المتعدد المحدث والمصلح
👨‍💻 Developer: @zizo 
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
from typing import Dict, List, Optional, Tuple
from collections import deque
from colorama import init, Fore, Back, Style

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

# Initialize colorama for Windows compatibility
init(autoreset=True)

# ==============================================================================
# 🔐 الإعدادات
# ==============================================================================
TELEGRAM_BOT_TOKEN = "7958170099:AAHTcRK6S7WrG7XDbQMME-f9ns6et0T52m4"
ADMIN_ID = 1124247595

# API Settings
API_BASE_URL = "https://freefollower.net/api"
ACCOUNTS_FILE = "accounts.json"  # ملف واحد فقط للحسابات والتوكنات
STATS_FILE = "stats.json"
QUEUE_FILE = "queue.json"  # ملف الطابور

# Service Settings
FREE_SERVICE_ID = 196

# Account Creation Settings
TOKEN_COOLDOWN_HOURS = 25
MIN_WAIT_SECONDS = 5
MAX_WAIT_SECONDS = 10
MAX_ACCOUNT_CREATION_ATTEMPTS = 3

# ==============================================================================
# إعداد السجلات الملونة
# ==============================================================================
class ColoredFormatter(logging.Formatter):
    """Formatter with colors for terminal output"""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE,
        'SUCCESS': Fore.GREEN + Style.BRIGHT,
    }

    def format(self, record):
        # Add custom SUCCESS level
        if record.levelno == 25:  # Custom SUCCESS level
            record.levelname = 'SUCCESS'

        # Format the timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')

        # Get color for the level
        color = self.COLORS.get(record.levelname, '')
        reset = Style.RESET_ALL

        # Build the formatted message
        formatted = f"{Fore.WHITE}[{record.levelname:<7}] {Fore.BLUE}{timestamp} {color}-> {record.getMessage()}{reset}"
        return formatted

# Add custom SUCCESS level
logging.addLevelName(25, 'SUCCESS')

# Configure logging with colored output
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())

file_handler = logging.FileHandler("bot.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)
logger = logging.getLogger(__name__)

# Add success method to logger
def success(self, message, *args, **kwargs):
    if self.isEnabledFor(25):
        self._log(25, message, args, **kwargs)
logging.Logger.success = success

# ==============================================================================
# 🛠️ مولد الحسابات
# ==============================================================================
def generate_ultimate_human_credentials():
    """توليد بيانات حساب بشرية واقعية"""
    vowels = "aeiou"
    consonants = "bcdfghjklmnprstvwxyz"

    # Generate parts
    name_part1 = "".join(random.choices(consonants, k=1)) + random.choice(vowels)
    name_part2 = random.choice(consonants) + random.choice(vowels)
    name_part3 = random.choice(consonants) + random.choice(vowels)

    # Create username variations
    username_styles = [
        lambda: f"{name_part1}{name_part2}{name_part3}{random.randint(1990, 2005)}",
        lambda: f"{name_part1}{name_part2}{name_part3}_{random.randint(10, 99)}",
        lambda: f"{name_part1}{name_part2}_{random.randint(70, 99)}"
    ]

    username = random.choice(username_styles)()

    # Generate email
    email_domains = ["gmail.com", "outlook.com", "yahoo.com"]
    email = f"{username}@{random.choice(email_domains)}"

    # Generate password
    pass_letters = ''.join(random.choices(string.ascii_letters, k=5))
    password = f"{pass_letters.capitalize()}{random.randint(1990, 2005)}{random.choice('!@#$*')}"

    logger.debug(f"تم إنشاء بيانات مدمجة: Username='{username}', Password='{password}', Email='{email}'")
    return username, email, password

# ==============================================================================
# 📋 نظام الطابور المتعدد المحسن مع أرقام الطلبات
# ==============================================================================
class QueueManager:
    """مدير الطابور للعملاء المتعددين مع أرقام الطلبات"""

    def __init__(self):
        self.queues = {}  # طابور لكل عميل
        self.active_orders = []  # الطلبات النشطة
        self.order_counter = {}  # عداد رقم الطلب لكل عميل
        self.load_queue()

    def load_queue(self):
        """تحميل الطابور من الملف"""
        try:
            if os.path.exists(QUEUE_FILE):
                with open(QUEUE_FILE, "r") as f:
                    data = json.load(f)
                    self.queues = data.get("queues", {})
                    self.active_orders = data.get("active_orders", [])
                    self.order_counter = data.get("order_counter", {})
                    logger.info(f"📂 تم تحميل الطابور: {len(self.active_orders)} طلب نشط")
        except Exception as e:
            logger.error(f"خطأ في تحميل الطابور: {e}")
            self.queues = {}
            self.active_orders = []
            self.order_counter = {}

    def save_queue(self):
        """حفظ الطابور"""
        try:
            with open(QUEUE_FILE, "w") as f:
                json.dump(
                    {
                        "queues": self.queues,
                        "active_orders": self.active_orders,
                        "order_counter": self.order_counter
                    },
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except Exception as e:
            logger.error(f"خطأ في حفظ الطابور: {e}")

    def add_order(self, user_id: str, link: str, total_followers: int) -> Tuple[str, int]:
        """إضافة طلب جديد للطابور مع رقم الطلب"""
        # زيادة عداد الطلبات للعميل
        if user_id not in self.order_counter:
            self.order_counter[user_id] = 0
        self.order_counter[user_id] += 1
        order_number = self.order_counter[user_id]

        order_id = f"order_{user_id}_{int(time.time())}"
        order = {
            "order_id": order_id,
            "order_number": order_number,  # رقم الطلب للعميل
            "user_id": user_id,
            "link": link,
            "total_requested": total_followers,
            "completed": 0,
            "accounts_needed": (total_followers // 10) + (1 if total_followers % 10 > 0 else 0),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "tokens_used": []
        }

        if user_id not in self.queues:
            self.queues[user_id] = []
        self.queues[user_id].append(order)
        self.active_orders.append(order_id)
        self.save_queue()

        logger.info(f"📝 طلب جديد #{order_number} للعميل {user_id}")
        return order_id, order_number

    def get_next_order(self) -> Optional[Dict]:
        """الحصول على الطلب التالي بنظام الدوران"""
        if not self.active_orders:
            return None

        # نظام الدوران - كل عميل ياخد دوره
        for order_id in self.active_orders[:]:  # نسخة من القائمة
            for user_id, orders in self.queues.items():
                for order in orders:
                    if order["order_id"] == order_id and order["status"] == "pending":
                        if order["completed"] < order["accounts_needed"]:
                            # نقل الطلب لآخر القائمة (دوران)
                            self.active_orders.remove(order_id)
                            self.active_orders.append(order_id)
                            return order
        return None

    def update_order_progress(self, order_id: str, success: bool):
        """تحديث تقدم الطلب"""
        for user_id, orders in self.queues.items():
            for order in orders:
                if order["order_id"] == order_id:
                    if success:
                        order["completed"] += 1
                        order_num = order.get('order_number', 'N/A')
                        logger.success(f"✅ التقدم: {order['completed']}/{order['accounts_needed']} للطلب #{order_num}")
                        # التحقق من اكتمال الطلب
                        if order["completed"] >= order["accounts_needed"]:
                            order["status"] = "completed"
                            if order_id in self.active_orders:
                                self.active_orders.remove(order_id)
                            logger.success(f"🎉 اكتمل الطلب #{order_num} للعميل {user_id}")
                    self.save_queue()
                    return

    def get_queue_status(self) -> str:
        """الحصول على حالة الطابور مع أرقام الطلبات"""
        total_orders = sum(len(orders) for orders in self.queues.values())
        active = len([o for orders in self.queues.values() for o in orders if o["status"] == "pending"])
        completed = len([o for orders in self.queues.values() for o in orders if o["status"] == "completed"])

        status = f"📊 **حالة الطابور:**\n"
        status += f"• إجمالي الطلبات: {total_orders}\n"
        status += f"• طلبات نشطة: {active}\n"
        status += f"• طلبات مكتملة: {completed}\n\n"

        # تفاصيل كل عميل
        for user_id, orders in self.queues.items():
            if orders:
                status += f"**العميل {user_id}:**\n"
                for order in orders[-3:]:  # آخر 3 طلبات
                    order_num = order.get('order_number', 'N/A')
                    status += f"  • {order['completed']}/{order['accounts_needed']} - {order['status']} - طلب #{order_num}\n"
        return status

# ==============================================================================
# 🔑 مدير الحسابات الموحد
# ==============================================================================
class AccountManager:
    """مدير الحسابات والتوكنات في ملف واحد"""

    def __init__(self):
        self.accounts = self.load_accounts()
        self.captcha_cooldown = {}

    def load_accounts(self) -> List[Dict]:
        """تحميل الحسابات من الملف الموحد"""
        try:
            if os.path.exists(ACCOUNTS_FILE):
                with open(ACCOUNTS_FILE, "r") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        if isinstance(data, list):
                            logger.info(f"📂 تم تحميل {len(data)} حساب من accounts.json")
                            return data
            logger.warning("📂 لم يتم العثور على حسابات محفوظة")
            return []
        except Exception as e:
            logger.error(f"خطأ في تحميل الحسابات: {e}")
            return []

    def save_accounts(self):
        """حفظ الحسابات في سطر واحد لكل حساب"""
        try:
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump(self.accounts, f, ensure_ascii=False, indent=2)
            logger.debug(f"💾 تم حفظ {len(self.accounts)} حساب")
        except Exception as e:
            logger.error(f"خطأ في حفظ الحسابات: {e}")

    def validate_token_format(self, token: str) -> bool:
        """التحقق من صيغة التوكن"""
        if not token:
            return False
        if not re.match(r'^[a-zA-Z0-9]{50,70}$', token):
            return False
        return True

    def create_new_account(self) -> Optional[Dict]:
        """إنشاء حساب جديد تلقائياً"""
        for attempt in range(MAX_ACCOUNT_CREATION_ATTEMPTS):
            logger.info(f"بدء عملية إنشاء حساب جديد...")
            username, email, password = generate_ultimate_human_credentials()

            payload = {
                "login": username,
                "email": email,
                "password": password
            }

            try:
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

                logger.debug(f"إرسال طلب التسجيل... Status: {response.status_code}")

                if response.status_code == 201:
                    data = response.json()
                    api_token = data.get("api_token")

                    if api_token:
                        logger.success(f"نجاح! تم إنشاء الحساب '{username}'.")

                        # حفظ الحساب مع التوكن
                        new_account = {
                            "token": api_token,
                            "username": username,
                            "email": email,
                            "password": password,
                            "created_at": datetime.now().isoformat(),
                            "last_used": None,
                            "use_count": 0,
                            "auto_created": True
                        }
                        self.accounts.append(new_account)
                        self.save_accounts()
                        return new_account

                elif response.status_code == 429:
                    error_data = response.json()
                    if "need_captcha" in str(error_data):
                        logger.error(f"فشل إنشاء الحساب. الرد: {error_data}")
                        wait_time = random.uniform(10, 20)
                        time.sleep(wait_time)
                    else:
                        time.sleep(30)

            except requests.exceptions.RequestException as e:
                logger.error(f"خطأ في الشبكة أثناء إنشاء الحساب: {e}")
                time.sleep(5)
            except Exception as e:
                logger.error(f"خطأ غير متوقع: {e}")
                time.sleep(5)

        return None

    def add_account(self, account_data: str) -> str:
        """إضافة حساب جديد"""
        try:
            if account_data.startswith("{"):
                data = json.loads(account_data)
                token = data.get("token", "")
                username = data.get("username", "unknown")
                email = data.get("email", "")
                password = data.get("password", "")
            else:
                token = account_data.strip()
                username = "imported"
                email = ""
                password = ""

            if not self.validate_token_format(token):
                return "❌ صيغة التوكن غير صحيحة!"

            # التحقق من التكرار
            for existing in self.accounts:
                if existing.get("token") == token:
                    return "⚠️ التوكن موجود بالفعل!"

            # إضافة الحساب
            new_account = {
                "token": token,
                "username": username,
                "email": email,
                "password": password,
                "created_at": datetime.now().isoformat(),
                "last_used": None,
                "use_count": 0,
                "auto_created": False
            }
            self.accounts.append(new_account)
            self.save_accounts()
            return f"✅ تم إضافة الحساب بنجاح!\n👤 المستخدم: {username}\n📊 إجمالي الحسابات: {len(self.accounts)}"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"

    def get_available_account(self) -> Optional[Dict]:
        """الحصول على حساب متاح"""
        now = datetime.now()

        for account in self.accounts:
            last_used = account.get("last_used")

            if last_used is None:
                logger.info(f"✅ استخدام حساب جديد: {account.get('username')}")
                return account

            try:
                last_used_time = datetime.fromisoformat(last_used)
                time_diff = now - last_used_time

                if time_diff.total_seconds() >= (TOKEN_COOLDOWN_HOURS * 3600):
                    logger.info(f"✅ استخدام حساب متاح: {account.get('username')}")
                    return account
            except:
                continue

        # محاولة إنشاء حساب جديد
        logger.warning("⚠️ لا توجد حسابات متاحة، جاري إنشاء حساب جديد...")
        return self.create_new_account()

    def mark_used(self, token: str):
        """تحديد الحساب كمستخدم"""
        for account in self.accounts:
            if account["token"] == token:
                account["last_used"] = datetime.now().isoformat()
                account["use_count"] = account.get("use_count", 0) + 1
                self.save_accounts()

    def get_stats(self) -> Dict:
        """إحصائيات الحسابات"""
        total = len(self.accounts)
        now = datetime.now()
        available = 0

        for account in self.accounts:
            last_used = account.get("last_used")
            if last_used is None:
                available += 1
            else:
                try:
                    last_used_time = datetime.fromisoformat(last_used)
                    if (now - last_used_time).total_seconds() >= (TOKEN_COOLDOWN_HOURS * 3600):
                        available += 1
                except:
                    pass

        auto_created = sum(1 for a in self.accounts if a.get("auto_created", False))

        return {
            "total": total,
            "available": available,
            "on_cooldown": total - available,
            "auto_created": auto_created
        }

# ==============================================================================
# 🚀 معالج الطلبات بنظام الطابور
# ==============================================================================
class OrderProcessor:
    """معالج الطلبات مع نظام الطابور المتعدد"""

    def __init__(self, account_manager: AccountManager, queue_manager: QueueManager):
        self.account_manager = account_manager
        self.queue_manager = queue_manager
        self.stats = self.load_stats()
        self.processing = False
        self.auto_processing_task = None
        self.update_callbacks = {}  # Store update callbacks for each user

    def load_stats(self) -> Dict:
        """تحميل الإحصائيات"""
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, "r") as f:
                    return json.load(f)
        except:
            pass
        return {"total_orders": 0, "successful": 0, "failed": 0}

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

    def place_order_v2(self, api_token: str, link: str, quantity: int = 10) -> Tuple[bool, Optional[str]]:
        """إرسال طلب واحد"""
        logger.info(f"بدء إرسال طلب المتابعين...")

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

            logger.debug(f"إرسال طلب الخدمة... Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if "order" in data:
                    order_id = data['order']
                    logger.success(f"نجاح! تم إرسال الطلب بنجاح. Order ID: {order_id}")
                    return True, order_id
                elif "error" in data:
                    logger.error(f"فشل الطلب: {data['error']}")
                    return False, None
        except Exception as e:
            logger.error(f"خطأ في إرسال الطلب: {e}")
        return False, None

    async def send_update_to_user(self, user_id: str, message: str):
        """Send update to specific user if they have a callback"""
        if user_id in self.update_callbacks:
            callback = self.update_callbacks[user_id]
            try:
                await callback(message)
            except:
                # Remove callback if it fails
                del self.update_callbacks[user_id]

    async def process_queue_continuously(self):
        """معالجة الطابور بشكل مستمر"""
        logger.info("🚀 بدء المعالجة التلقائية للطابور...")

        while True:
            try:
                # الحصول على الطلب التالي من الطابور
                order = self.queue_manager.get_next_order()

                if not order:
                    logger.info("📭 الطابور فارغ، انتظار طلبات جديدة...")
                    await asyncio.sleep(10)  # انتظار 10 ثواني وإعادة الفحص
                    continue

                order_num = order.get('order_number', 'N/A')
                user_id = order['user_id']

                logger.info(f"بدء دورة جديدة...")
                logger.info(f"📋 معالجة طلب #{order_num} - العميل: {user_id}")

                # الحصول على حساب متاح
                account = self.account_manager.get_available_account()

                if not account:
                    logger.warning("❌ لا توجد حسابات متاحة")
                    await self.send_update_to_user(user_id,
                        f"⚠️ الطابور: العميل {user_id}\n"
                        f"❌ لا توجد حسابات متاحة\n"
                        f"📊 التقدم: {order['completed']}/{order['accounts_needed']} - طلب #{order_num}"
                    )
                    wait_time = random.uniform(MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)
                    logger.info(f"اكتملت الدورة، سيتم الانتظار لمدة {wait_time:.2f} ثانية...")
                    await asyncio.sleep(wait_time)
                    continue

                # إرسال تحديث
                await self.send_update_to_user(user_id,
                    f"🔄 **نظام الطابور**\n\n"
                    f"👤 العميل: {user_id}\n"
                    f"📊 التقدم: {order['completed']}/{order['accounts_needed']} - طلب #{order_num}\n"
                    f"🔑 الحساب: {account.get('username')}\n"
                    f"⏳ جاري الإرسال..."
                )

                # إرسال الطلب
                success, service_order_id = self.place_order_v2(account["token"], order["link"], 10)

                if success:
                    # تحديث التقدم
                    self.queue_manager.update_order_progress(order["order_id"], True)
                    self.account_manager.mark_used(account["token"])
                    self.stats["successful"] += 1

                    await self.send_update_to_user(user_id,
                        f"✅ **نجح الطلب!**\n\n"
                        f"👤 العميل: {user_id}\n"
                        f"📊 التقدم: {order['completed'] + 1}/{order['accounts_needed']} - طلب #{order_num}\n"
                        f"👥 متابعين مرسلين: {(order['completed'] + 1) * 10}\n"
                        f"🆔 Order ID: {service_order_id}"
                    )
                else:
                    self.stats["failed"] += 1
                    await self.send_update_to_user(user_id,
                        f"❌ **فشل الطلب**\n\n"
                        f"👤 العميل: {user_id}\n"
                        f"📊 التقدم: {order['completed']}/{order['accounts_needed']} (لم يتغير) - طلب #{order_num}"
                    )

                self.stats["total_orders"] += 1
                self.save_stats()

                # الانتظار بين الطلبات
                wait_time = random.uniform(MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)
                logger.info(f"اكتملت الدورة، سيتم الانتظار لمدة {wait_time:.2f} ثانية...")

                # Send queue status to all users
                queue_status = self.queue_manager.get_queue_status()
                await self.send_update_to_user(user_id,
                    f"⏰ انتظار {wait_time:.1f} ثانية قبل الطلب التالي...\n"
                    f"{queue_status}"
                )

                await asyncio.sleep(wait_time)

            except Exception as e:
                logger.error(f"خطأ في معالجة الطابور: {e}")
                await asyncio.sleep(5)

    def start_auto_processing(self):
        """بدء المعالجة التلقائية في الخلفية"""
        if not self.auto_processing_task or self.auto_processing_task.done():
            self.auto_processing_task = asyncio.create_task(self.process_queue_continuously())
            logger.info("✅ تم تفعيل المعالجة التلقائية للطابور")

# ==============================================================================
# 🤖 البوت الرئيسي
# ==============================================================================
class TelegramBot:
    """البوت الرئيسي مع نظام الطابور التلقائي"""

    def __init__(self):
        self.account_manager = AccountManager()
        self.queue_manager = QueueManager()
        self.order_processor = OrderProcessor(self.account_manager, self.queue_manager)
        self.user_messages = {}  # Store user message for updates

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        user = update.effective_user

        # بدء المعالجة التلقائية عند تشغيل البوت
        self.order_processor.start_auto_processing()

        message = (
            "🔥 **بوت الطابور المتعدد - تلقائي**\n\n"
            "**الأوامر:**\n"
            "`/follow [لينك] [عدد]` - إضافة طلب للطابور\n"
            "`/queue` - عرض حالة الطابور\n"
            "`/add_token [توكن]` - إضافة حساب (للأدمن فقط)\n"
            "`/stats` - الإحصائيات\n\n"
            "**نظام الطابور:**\n"
            "✅ معالجة تلقائية فورية\n"
            "✅ كل عميل ياخد دوره\n"
            "✅ دوران عادل بين العملاء\n"
            "✅ 5-10 ثواني بين الطلبات\n"
            "✅ الأوامر تشتغل حتى أثناء المعالجة\n\n"
            "🇪🇬 صُنع في مصر"
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    async def follow_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إضافة طلب جديد للطابور"""
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ الصيغة:\n`/follow [لينك] [عدد]`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        link = context.args[0]
        try:
            quantity = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ العدد لازم يكون رقم!")
            return

        if not self.order_processor.validate_tiktok_link(link):
            await update.message.reply_text("❌ اللينك غير صحيح!")
            return

        if quantity <= 0:
            await update.message.reply_text("❌ العدد لازم يكون أكبر من صفر!")
            return

        # إضافة الطلب للطابور
        user_id = str(update.effective_user.id)
        order_id, order_number = self.queue_manager.add_order(user_id, link, quantity)
        accounts_needed = (quantity // 10) + (1 if quantity % 10 > 0 else 0)

        # Create update callback for this user
        msg = await update.message.reply_text(
            f"✅ **تم إضافة الطلب للطابور!**\n\n"
            f"🆔 رقم الطلب: #{order_number}\n"
            f"📱 اللينك: {link}\n"
            f"👥 المتابعين: {quantity}\n"
            f"📊 الحسابات المطلوبة: {accounts_needed}\n\n"
            f"🚀 **المعالجة تلقائية وفورية**\n"
            f"📌 سيتم إرسال التحديثات هنا",
            parse_mode=ParseMode.MARKDOWN
        )

        # Store callback for updates
        async def update_callback(text):
            try:
                await msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
            except:
                # If edit fails, send new message
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

        self.order_processor.update_callbacks[user_id] = update_callback

        # بدء المعالجة التلقائية إذا لم تكن شغالة
        self.order_processor.start_auto_processing()

    async def show_queue(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض حالة الطابور"""
        status = self.queue_manager.get_queue_status()
        await update.message.reply_text(status, parse_mode=ParseMode.MARKDOWN)

    async def add_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إضافة حساب جديد"""
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ هذا الأمر للأدمن فقط!")
            return

        if not context.args:
            await update.message.reply_text(
                "📝 **إضافة حساب:**\n"
                '`/add_token {"token":"TOKEN","username":"user","email":"email","password":"pass"}`',
                parse_mode=ParseMode.MARKDOWN
            )
            return

        account_data = " ".join(context.args)
        result = self.account_manager.add_account(account_data)
        await update.message.reply_text(result)

    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإحصائيات"""
        account_stats = self.account_manager.get_stats()
        order_stats = self.order_processor.stats

        message = (
            f"📊 **الإحصائيات**\n"
            f"{'='*25}\n\n"
            f"**👤 الحسابات:**\n"
            f"• الإجمالي: {account_stats['total']}\n"
            f"• المتاح: {account_stats['available']}\n"
            f"• في الانتظار: {account_stats['on_cooldown']}\n"
            f"• تم إنشاؤها تلقائياً: {account_stats['auto_created']}\n\n"
            f"**📦 الطلبات:**\n"
            f"• الإجمالي: {order_stats['total_orders']}\n"
            f"• الناجح: {order_stats['successful']}\n"
            f"• الفاشل: {order_stats['failed']}\n\n"
            f"{self.queue_manager.get_queue_status()}"
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

# ==============================================================================
# 🚀 التشغيل الرئيسي
# ==============================================================================
def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل بوت الطابور المتعدد التلقائي...")
    logger.info("📋 نظام الدوران بين العملاء مفعّل")
    logger.info("🤖 المعالجة التلقائية مفعّلة")
    logger.info("✅ الأوامر تعمل أثناء المعالجة")
    logger.info("📁 ملف واحد فقط: accounts.json")

    bot = TelegramBot()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # إضافة المعالجات
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("follow", bot.follow_order))
    application.add_handler(CommandHandler("queue", bot.show_queue))
    application.add_handler(CommandHandler("add_token", bot.add_token))
    application.add_handler(CommandHandler("stats", bot.show_stats))

    logger.info("✅ البوت جاهز!")
    logger.info("🇪🇬 صُنع بكل حب في مصر")

    # Start auto processing
    asyncio.get_event_loop().run_until_complete(bot.order_processor.start_auto_processing())

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
