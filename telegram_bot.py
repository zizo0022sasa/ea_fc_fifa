#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 بوت تيليجرام مصري - النسخة النهائية المدمجة
👨‍💻 Dev: @zizo0022sasa
🇪🇬 Made in Egypt with ❤️
📅 آخر تحديث: 2024
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

import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

# ألوان للترمينال
try:
    from colorama import Back, Fore, Style
    from colorama import init as colorama_init

    colorama_init(autoreset=True)
    COLORAMA_OK = True
except ImportError:
    COLORAMA_OK = False

# حل مشكلة event loop على ويندوز
try:
    import nest_asyncio

    nest_asyncio.apply()
except Exception:
    pass

# ==============================================================================
# 🔐 الإعدادات المباشرة
# ==============================================================================
TELEGRAM_BOT_TOKEN = "7958170099:AAHTcRK6S7WrG7XDbQMME-f9ns6et0T52m4"
ADMIN_ID = 1124247595

# API Settings
API_BASE_URL = "https://freefollower.net/api"
FREE_SERVICE_ID = 196

# Files
ACCOUNTS_JSON = "accounts.json"
ACCOUNTS_TXT = "accounts.txt"
STATS_FILE = "stats.json"
QUEUE_FILE = "queue.json"

# Timing
TOKEN_COOLDOWN_HOURS = 25
MIN_WAIT_SECONDS = 5
MAX_WAIT_SECONDS = 10
MAX_ACCOUNT_CREATION_ATTEMPTS = 3

# Smart Mode
SMART_IDLE_ENABLED = False
SMART_DEFAULT_LINK = ""


# ==============================================================================
# 🎨 نظام اللوجز الملون المحسن
# ==============================================================================
class SuperColoredFormatter(logging.Formatter):
    """نظام لوجز احترافي بألوان واضحة"""

    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        message = record.getMessage()

        if "✅" in message or "نجح" in message or "SUCCESS" in message.upper():
            if COLORAMA_OK:
                return f"{Fore.BLACK}{Back.GREEN} ✅ SUCCESS {Style.RESET_ALL} {Fore.GREEN}{timestamp} ➜ {message}{Style.RESET_ALL}"
            return f"[✅ SUCCESS] {timestamp} ➜ {message}"

        if (
            "❌" in message
            or "فشل" in message
            or "FAILED" in message.upper()
            or "ERROR" in record.levelname
        ):
            if COLORAMA_OK:
                return f"{Fore.WHITE}{Back.RED} ❌ FAILED {Style.RESET_ALL} {Fore.RED}{timestamp} ➜ {message}{Style.RESET_ALL}"
            return f"[❌ FAILED] {timestamp} ➜ {message}"

        if "⚠️" in message or "WARNING" in record.levelname:
            if COLORAMA_OK:
                return f"{Fore.BLACK}{Back.YELLOW} ⚠️ WARNING {Style.RESET_ALL} {Fore.YELLOW}{timestamp} ➜ {message}{Style.RESET_ALL}"
            return f"[⚠️ WARNING] {timestamp} ➜ {message}"

        if "🔄" in message or "معالجة" in message:
            if COLORAMA_OK:
                return f"{Fore.WHITE}{Back.BLUE} 🔄 PROCESS {Style.RESET_ALL} {Fore.CYAN}{timestamp} ➜ {message}{Style.RESET_ALL}"
            return f"[🔄 PROCESS] {timestamp} ➜ {message}"

        if "📊" in message or "إحصائيات" in message:
            if COLORAMA_OK:
                return f"{Fore.WHITE}{Back.MAGENTA} 📊 STATS {Style.RESET_ALL} {Fore.MAGENTA}{timestamp} ➜ {message}{Style.RESET_ALL}"
            return f"[📊 STATS] {timestamp} ➜ {message}"

        if COLORAMA_OK:
            level_colors = {"INFO": Fore.WHITE, "DEBUG": Fore.CYAN}
            color = level_colors.get(record.levelname, Fore.WHITE)
            return (
                f"{color}[{record.levelname}] {timestamp} ➜ {message}{Style.RESET_ALL}"
            )
        return f"[{record.levelname}] {timestamp} ➜ {message}"


console_handler = logging.StreamHandler()
console_handler.setFormatter(SuperColoredFormatter())
file_handler = logging.FileHandler("bot.log", encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])
logger = logging.getLogger("EgyptianBot")

logging.addLevelName(25, "SUCCESS")


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(25):
        self._log(25, message, args, **kwargs)


logging.Logger.success = success


# ==============================================================================
# 🛠️ الدوال المساعدة
# ==============================================================================
def generate_human_credentials():
    """توليد بيانات حساب بشرية واقعية"""
    vowels = "aeiou"
    consonants = "bcdfghjklmnprstvwxyz"

    name_part1 = "".join(random.choices(consonants, k=1)) + random.choice(vowels)
    name_part2 = random.choice(consonants) + random.choice(vowels)
    name_part3 = random.choice(consonants) + random.choice(vowels)

    username_styles = [
        lambda: f"{name_part1}{name_part2}{name_part3}{random.randint(1990, 2005)}",
        lambda: f"{name_part1}{name_part2}{name_part3}_{random.randint(10, 99)}",
        lambda: f"{name_part1}{name_part2}_{random.randint(70, 99)}",
    ]

    username = random.choice(username_styles)()
    email_domains = ["gmail.com", "outlook.com", "yahoo.com"]
    email = f"{username}@{random.choice(email_domains)}"

    pass_letters = "".join(random.choices(string.ascii_letters, k=5))
    password = f"{pass_letters.capitalize()}{random.randint(1990, 2005)}{random.choice('!@#$*')}"

    return username, email, password


def rand_wait():
    """انتظار عشوائي ذكي"""
    return random.uniform(MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)


# ==============================================================================
# 📋 نظام الطابور المحسن
# ==============================================================================
class QueueManager:
    def __init__(self):
        self.queues: Dict[str, List[Dict]] = {}
        self.active_orders: List[str] = []
        self.order_counter: Dict[str, int] = {}
        self.load()

    def load(self):
        try:
            if os.path.exists(QUEUE_FILE):
                with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.queues = data.get("queues", {})
                    self.active_orders = data.get("active_orders", [])
                    self.order_counter = data.get("order_counter", {})
                    logger.info(
                        f"📂 تم تحميل الطابور: {len(self.active_orders)} طلب نشط"
                    )
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل الطابور: {e}")
            self.queues, self.active_orders, self.order_counter = {}, [], {}

    def save(self):
        try:
            with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "queues": self.queues,
                        "active_orders": self.active_orders,
                        "order_counter": self.order_counter,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ الطابور: {e}")

    def add_order(
        self, user_id: str, link: str, total_followers: int
    ) -> Tuple[str, int]:
        if user_id not in self.order_counter:
            self.order_counter[user_id] = 0
        self.order_counter[user_id] += 1
        order_number = self.order_counter[user_id]

        accounts_needed = (total_followers // 10) + (
            1 if total_followers % 10 > 0 else 0
        )
        order_id = f"order_{user_id}_{int(time.time())}"

        order = {
            "order_id": order_id,
            "order_number": order_number,
            "user_id": user_id,
            "link": link,
            "total_requested": total_followers,
            "completed": 0,
            "accounts_needed": accounts_needed,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }

        if user_id not in self.queues:
            self.queues[user_id] = []
        self.queues[user_id].append(order)
        self.active_orders.append(order_id)
        self.save()

        logger.info(
            f"📝 طلب جديد #{order_number} للعميل {user_id} - يحتاج {accounts_needed} حساب"
        )
        return order_id, order_number

    def get_next_order(self) -> Optional[Dict]:
        if not self.active_orders:
            return None

        for order_id in self.active_orders[:]:
            for user_id, orders in self.queues.items():
                for order in orders:
                    if order["order_id"] == order_id and order["status"] == "pending":
                        if order["completed"] < order["accounts_needed"]:
                            self.active_orders.remove(order_id)
                            self.active_orders.append(order_id)
                            return order
        return None

    def update_order_progress(self, order_id: str, success: bool):
        for user_id, orders in self.queues.items():
            for order in orders:
                if order["order_id"] == order_id:
                    if success:
                        order["completed"] += 1
                        order_num = order.get("order_number", "N/A")
                        progress = f"{order['completed']}/{order['accounts_needed']}"
                        logger.info(
                            f"✅ نجح إرسال المتابعين! التقدم: {progress} للطلب #{order_num}"
                        )

                        if order["completed"] >= order["accounts_needed"]:
                            order["status"] = "completed"
                            if order_id in self.active_orders:
                                self.active_orders.remove(order_id)
                            logger.info(
                                f"✅ اكتمل الطلب #{order_num} بنجاح للعميل {user_id} 🎉"
                            )
                    self.save()
                    return

    def status_markdown(self) -> str:
        total_orders = sum(len(orders) for orders in self.queues.values())
        active = len(
            [
                o
                for orders in self.queues.values()
                for o in orders
                if o["status"] == "pending"
            ]
        )
        completed = len(
            [
                o
                for orders in self.queues.values()
                for o in orders
                if o["status"] == "completed"
            ]
        )

        status = f"📊 **حالة الطابور:**\n"
        status += f"• إجمالي: {total_orders}\n"
        status += f"• نشط: {active}\n"
        status += f"• مكتمل: {completed}\n\n"

        for user_id, orders in self.queues.items():
            if orders:
                status += f"**العميل {user_id}:**\n"
                for order in orders[-3:]:
                    order_num = order.get("order_number", "N/A")
                    status += f"  • {order['completed']}/{order['accounts_needed']} - {order['status']} - طلب #{order_num}\n"
        return status


# ==============================================================================
# 🔑 مدير الحسابات المحسن
# ==============================================================================
class AccountManager:
    def __init__(self):
        self.accounts: List[Dict] = self.load_accounts()
        self.round_index = 0

    def load_accounts(self) -> List[Dict]:
        accounts: List[Dict] = []
        seen = set()

        # تحميل من JSON
        if os.path.exists(ACCOUNTS_JSON):
            try:
                with open(ACCOUNTS_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f) or []
                    if isinstance(data, list):
                        for a in data:
                            tok = a.get("token")
                            if tok and tok not in seen:
                                a.setdefault("use_count", 0)
                                a.setdefault("auto_created", False)
                                a.setdefault("username", "unknown")
                                a.setdefault("email", "")
                                a.setdefault("password", "")
                                a.setdefault("created_at", datetime.now().isoformat())
                                a.setdefault("last_used", None)
                                accounts.append(a)
                                seen.add(tok)
                        logger.info(
                            f"📂 تم تحميل {len(accounts)} حساب من {ACCOUNTS_JSON}"
                        )
            except Exception as e:
                logger.warning(f"⚠️ تعذر قراءة {ACCOUNTS_JSON}: {e}")

        # تحميل من TXT
        if os.path.exists(ACCOUNTS_TXT):
            try:
                with open(ACCOUNTS_TXT, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            a = json.loads(line)
                            tok = a.get("token")
                            if tok and tok not in seen:
                                a.setdefault("use_count", 0)
                                a.setdefault("auto_created", False)
                                a.setdefault("username", a.get("username", "imported"))
                                a.setdefault("email", a.get("email", ""))
                                a.setdefault("password", a.get("password", ""))
                                a.setdefault("created_at", datetime.now().isoformat())
                                a.setdefault("last_used", None)
                                accounts.append(a)
                                seen.add(tok)
                        except:
                            continue
                logger.info(f"📂 تم قراءة حسابات إضافية من {ACCOUNTS_TXT}")
            except Exception as e:
                logger.warning(f"⚠️ تعذر قراءة {ACCOUNTS_TXT}: {e}")

        # إحصائيات الحسابات
        available = self._count_available_accounts(accounts)
        logger.info(f"📊 إحصائيات الحسابات: {available} متاح من {len(accounts)} إجمالي")

        return accounts

    def _count_available_accounts(self, accounts: List[Dict]) -> int:
        now = datetime.now()
        available = 0
        for acc in accounts:
            last_used = acc.get("last_used")
            if last_used is None:
                available += 1
            else:
                try:
                    last_used_time = datetime.fromisoformat(last_used)
                    hours = (now - last_used_time).total_seconds() / 3600
                    if hours >= TOKEN_COOLDOWN_HOURS:
                        available += 1
                except:
                    pass
        return available

    def save_accounts(self):
        try:
            temp_file = f"{ACCOUNTS_JSON}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.accounts, f, ensure_ascii=False, indent=2)

            if os.path.exists(ACCOUNTS_JSON):
                os.remove(ACCOUNTS_JSON)
            os.rename(temp_file, ACCOUNTS_JSON)

            logger.debug(f"💾 تم حفظ {len(self.accounts)} حساب")
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ الحسابات: {e}")

    @staticmethod
    def validate_token_format(token: str) -> bool:
        if not token:
            return False
        return bool(re.match(r"^[a-zA-Z0-9]{20,100}$", token))

    def _append_to_txt_legacy(self, account: Dict):
        try:
            with open(ACCOUNTS_TXT, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "token": account.get("token"),
                            "username": account.get("username", "imported"),
                            "password": account.get("password", ""),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except:
            pass

    def create_new_account(self) -> Optional[Dict]:
        for attempt in range(MAX_ACCOUNT_CREATION_ATTEMPTS):
            try:
                logger.info(
                    f"🔄 محاولة إنشاء حساب جديد... (محاولة {attempt + 1}/{MAX_ACCOUNT_CREATION_ATTEMPTS})"
                )
                username, email, password = generate_human_credentials()

                payload = {"login": username, "email": email, "password": password}
                time.sleep(random.uniform(1.5, 3.5))

                resp = requests.post(
                    f"{API_BASE_URL}/register",
                    json=payload,
                    timeout=20,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                )

                if resp.status_code == 201:
                    data = resp.json()
                    api_token = data.get("api_token")

                    if api_token and self.validate_token_format(api_token):
                        acc = {
                            "token": api_token,
                            "username": username,
                            "email": email,
                            "password": password,
                            "created_at": datetime.now().isoformat(),
                            "last_used": None,
                            "use_count": 0,
                            "auto_created": True,
                        }
                        self.accounts.append(acc)
                        self.save_accounts()
                        self._append_to_txt_legacy(acc)

                        logger.info(f"✅ تم إنشاء الحساب '{username}' بنجاح!")
                        return acc

                elif resp.status_code == 429:
                    logger.warning("⚠️ Rate limited - انتظار...")
                    time.sleep(random.uniform(8, 15))
                else:
                    logger.error(f"❌ فشل إنشاء الحساب: {resp.text[:100]}")
                    time.sleep(random.uniform(3, 6))

            except Exception as e:
                logger.error(f"❌ خطأ في إنشاء الحساب: {e}")
                time.sleep(random.uniform(3, 6))

        logger.error(f"❌ فشلت جميع محاولات إنشاء حساب جديد!")
        return None

    def add_account(self, account_data: str) -> str:
        try:
            if account_data.strip().startswith("{"):
                data = json.loads(account_data)
                token = data.get("token", "")
                username = data.get("username", "imported")
                email = data.get("email", "")
                password = data.get("password", "")
            else:
                token = account_data.strip()
                username, email, password = "imported", "", ""

            if not self.validate_token_format(token):
                return "❌ صيغة التوكن غير صحيحة!"

            for a in self.accounts:
                if a.get("token") == token:
                    return "⚠️ التوكن موجود بالفعل!"

            acc = {
                "token": token,
                "username": username,
                "email": email,
                "password": password,
                "created_at": datetime.now().isoformat(),
                "last_used": None,
                "use_count": 0,
                "auto_created": False,
            }
            self.accounts.append(acc)
            self.save_accounts()
            self._append_to_txt_legacy(acc)

            return f"✅ تم إضافة الحساب بنجاح!\n👤 المستخدم: {username}\n📊 إجمالي الحسابات: {len(self.accounts)}"

        except Exception as e:
            return f"❌ خطأ: {e}"

    def get_available_account(self) -> Optional[Dict]:
        now = datetime.now()
        available_accounts = []

        for acc in self.accounts:
            last_used = acc.get("last_used")
            if last_used is None:
                available_accounts.append(acc)
            else:
                try:
                    last_used_time = datetime.fromisoformat(last_used)
                    hours = (now - last_used_time).total_seconds() / 3600
                    if hours >= TOKEN_COOLDOWN_HOURS:
                        available_accounts.append(acc)
                except:
                    continue

        if not available_accounts:
            logger.warning(
                f"⚠️ لا توجد حسابات متاحة! (كل الـ {len(self.accounts)} حساب في فترة الانتظار)"
            )
            return None

        available_accounts.sort(
            key=lambda a: (a.get("use_count", 0), a.get("last_used") or "1900-01-01")
        )
        selected = available_accounts[self.round_index % len(available_accounts)]
        self.round_index = (self.round_index + 1) % len(available_accounts)

        username = selected.get("username", "unknown")
        logger.info(
            f"🔑 استخدام الحساب: {username} (متاح: {len(available_accounts)}/{len(self.accounts)})"
        )

        return selected

    def mark_used(self, token: str):
        for acc in self.accounts:
            if acc.get("token") == token:
                acc["last_used"] = datetime.now().isoformat()
                acc["use_count"] = acc.get("use_count", 0) + 1
                self.save_accounts()

                username = acc.get("username", "unknown")
                logger.info(f"🔒 الحساب {username} لن يكون متاح لمدة 25 ساعة")
                return

    def stats(self) -> Dict:
        total = len(self.accounts)
        now = datetime.now()
        available = 0
        never_used = 0

        for acc in self.accounts:
            last_used = acc.get("last_used")
            if last_used is None:
                available += 1
                never_used += 1
            else:
                try:
                    last_used_time = datetime.fromisoformat(last_used)
                    hours = (now - last_used_time).total_seconds() / 3600
                    if hours >= TOKEN_COOLDOWN_HOURS:
                        available += 1
                except:
                    pass

        auto_created = sum(1 for a in self.accounts if a.get("auto_created"))

        return {
            "total": total,
            "available": available,
            "on_cooldown": total - available,
            "auto_created": auto_created,
            "never_used": never_used,
        }


# ==============================================================================
# 🚀 معالج الطلبات المحسن
# ==============================================================================
class OrderProcessor:
    def __init__(self, account_manager: AccountManager, queue_manager: QueueManager):
        self.account_manager = account_manager
        self.queue_manager = queue_manager
        self.processing_task: Optional[asyncio.Task] = None
        self._callbacks: Dict[str, callable] = {}
        self.stats = self._load_stats()

    def _load_stats(self):
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return {"total_orders": 0, "successful": 0, "failed": 0}

    def _save_stats(self):
        try:
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except:
            pass

    def validate_tiktok_link(self, link: str) -> bool:
        patterns = [
            r"https?://(?:www\.)?tiktok\.com/@[\w\.-]+",
            r"https?://(?:www\.)?tiktok\.com/[\w\.-]+",
            r"https?://vm\.tiktok\.com/[\w]+",
            r"@[\w\.-]+",
        ]
        return any(re.match(p, link) for p in patterns)

    def place_order_v2(
        self, api_token: str, link: str, quantity: int = 10
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        payload = {
            "key": api_token,
            "action": "add",
            "service": FREE_SERVICE_ID,
            "link": link,
            "quantity": quantity,
        }

        try:
            resp = requests.post(
                f"{API_BASE_URL}/v2",
                json=payload,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            )

            if resp.status_code == 200:
                data = resp.json()
                if "order" in data:
                    logger.info(f"✅ نجح إرسال 10 متابعين! Order ID: {data['order']}")
                    return True, str(data["order"]), None
                elif "error" in data:
                    error_msg = str(data.get("error"))
                    logger.error(f"❌ فشل إرسال المتابعين: {error_msg}")
                    return False, None, error_msg

            elif resp.status_code == 429:
                logger.error(f"❌ فشل: Rate limited")
                return False, None, "Rate limited"
            else:
                logger.error(f"❌ فشل: HTTP {resp.status_code}")
                return False, None, f"HTTP {resp.status_code}"

        except Exception as e:
            logger.error(f"❌ خطأ في الإرسال: {e}")
            return False, None, f"Exception: {e}"

    async def _notify(self, user_id: str, msg: str):
        cb = self._callbacks.get(user_id)
        if cb:
            try:
                await cb(msg)
            except:
                self._callbacks.pop(user_id, None)

    def set_callback(self, user_id: str, cb):
        self._callbacks[user_id] = cb

    async def run(self):
        logger.info("🚀 بدء المعالجة التلقائية للطابور...")
        consecutive_failures = 0

        while True:
            try:
                order = self.queue_manager.get_next_order()

                if not order:
                    await asyncio.sleep(10)
                    continue

                user_id = order["user_id"]
                order_num = order.get("order_number", "N/A")

                logger.info(f"🔄 معالجة طلب #{order_num} للعميل {user_id}")

                acc = self.account_manager.get_available_account()

                if not acc:
                    logger.warning("⚠️ لا توجد حسابات متاحة - محاولة إنشاء حساب جديد...")
                    acc = self.account_manager.create_new_account()

                    if not acc:
                        consecutive_failures += 1
                        await self._notify(
                            user_id,
                            f"⚠️ لا توجد حسابات متاحة حالياً\n"
                            f"📊 التقدم: {order['completed']}/{order['accounts_needed']} - طلب #{order_num}\n"
                            f"⏳ سيتم إعادة المحاولة...",
                        )

                        if consecutive_failures >= 5:
                            logger.error(f"❌ فشل 5 محاولات متتالية - انتظار دقيقة")
                            await asyncio.sleep(60)
                            consecutive_failures = 0
                        else:
                            await asyncio.sleep(15)
                        continue

                consecutive_failures = 0

                await self._notify(
                    user_id,
                    f"🔄 **معالجة الطلب**\n"
                    f"📊 التقدم: {order['completed']}/{order['accounts_needed']} - طلب #{order_num}\n"
                    f"🔑 الحساب: {acc.get('username')}\n"
                    f"⏳ جاري الإرسال...",
                )

                ok, service_order_id, err = self.place_order_v2(
                    acc["token"], order["link"], 10
                )

                # مهم: أي حساب يُستخدم (نجاح/فشل) ينتظر 25 ساعة
                self.account_manager.mark_used(acc["token"])

                if ok:
                    self.queue_manager.update_order_progress(order["order_id"], True)
                    self.stats["successful"] += 1

                    await self._notify(
                        user_id,
                        f"✅ **نجح الإرسال!**\n"
                        f"📊 التقدم: {order['completed'] + 1}/{order['accounts_needed']} - طلب #{order_num}\n"
                        f"👥 تم إرسال: {(order['completed'] + 1) * 10} متابع\n"
                        f"🆔 Order: {service_order_id}",
                    )
                else:
                    self.stats["failed"] += 1

                    await self._notify(
                        user_id,
                        f"❌ **فشل الإرسال**\n"
                        f"📊 التقدم: {order['completed']}/{order['accounts_needed']} - طلب #{order_num}\n"
                        f"📝 السبب: {err}",
                    )

                self.stats["total_orders"] += 1
                self._save_stats()

                wt = rand_wait()
                await self._notify(
                    user_id,
                    f"⏰ انتظار {wt:.1f} ثانية...\n{self.queue_manager.status_markdown()}",
                )
                await asyncio.sleep(wt)

            except Exception as e:
                logger.error(f"❌ خطأ في المعالجة: {e}")
                await asyncio.sleep(5)

    def start(self):
        if not self.processing_task or self.processing_task.done():
            self.processing_task = asyncio.create_task(self.run())
            logger.info("✅ تم تفعيل المعالجة التلقائية")


# ==============================================================================
# 🤖 البوت الرئيسي
# ==============================================================================
class TelegramBot:
    def __init__(self):
        self.acc_mgr = AccountManager()
        self.queue_mgr = QueueManager()
        self.proc = OrderProcessor(self.acc_mgr, self.queue_mgr)

    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.proc.start()
        msg = (
            "🔥 **بوت الطابور المصري - النسخة النهائية**\n\n"
            "**الأوامر المتاحة:**\n"
            "`/follow [لينك] [عدد]` - طلب متابعين\n"
            "`/queue` - حالة الطابور\n"
            "`/add_token [توكن]` - إضافة حساب (أدمن)\n"
            "`/stats` - الإحصائيات\n\n"
            "**المميزات:**\n"
            "✅ دوران عادل بين الحسابات\n"
            f"✅ انتظار {MIN_WAIT_SECONDS}-{MAX_WAIT_SECONDS} ثانية\n"
            "✅ إنشاء حسابات تلقائي\n"
            "✅ كل حساب ينتظر 25 ساعة\n\n"
            "🇪🇬 صُنع بكل فخر في مصر"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def follow_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ الصيغة:\n`/follow [لينك] [عدد]`", parse_mode=ParseMode.MARKDOWN
            )
            return

        link = context.args[0]
        try:
            qty = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ العدد يجب أن يكون رقم!")
            return

        if qty <= 0:
            await update.message.reply_text("❌ العدد يجب أن يكون أكبر من صفر!")
            return

        if not self.proc.validate_tiktok_link(link):
            await update.message.reply_text("❌ رابط TikTok غير صحيح!")
            return

        user_id = str(update.effective_user.id)
        order_id, order_num = self.queue_mgr.add_order(user_id, link, qty)
        accounts_needed = (qty // 10) + (1 if qty % 10 > 0 else 0)

        sent_msg = await update.message.reply_text(
            f"✅ **تم إضافة طلبك!**\n\n"
            f"🆔 رقم الطلب: #{order_num}\n"
            f"📱 الرابط: {link}\n"
            f"👥 العدد المطلوب: {qty}\n"
            f"📊 الحسابات المطلوبة: {accounts_needed}\n\n"
            f"🚀 المعالجة تلقائية\n"
            f"📌 ستصلك التحديثات هنا",
            parse_mode=ParseMode.MARKDOWN,
        )

        async def cb(text):
            try:
                await sent_msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
            except:
                await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

        self.proc.set_callback(user_id, cb)
        self.proc.start()

    async def queue_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            self.queue_mgr.status_markdown(), parse_mode=ParseMode.MARKDOWN
        )

    async def add_token_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if ADMIN_ID and update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ هذا الأمر للأدمن فقط!")
            return

        if not context.args:
            await update.message.reply_text(
                "📝 **الاستخدام:**\n"
                '`/add_token {"token":"TOKEN","username":"user"}`\n'
                "أو\n"
                "`/add_token TOKEN`",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        data = " ".join(context.args)
        res = self.acc_mgr.add_account(data)
        await update.message.reply_text(res)

    async def stats_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        a = self.acc_mgr.stats()
        s = self.proc.stats

        success_rate = 0
        if s["total_orders"] > 0:
            success_rate = (s["successful"] / s["total_orders"]) * 100

        msg = (
            f"📊 **الإحصائيات**\n"
            f"{'='*20}\n\n"
            f"**👤 الحسابات:**\n"
            f"• الإجمالي: {a['total']}\n"
            f"• المتاح الآن: {a['available']}\n"
            f"• في الانتظار: {a['on_cooldown']}\n"
            f"• لم تُستخدم: {a.get('never_used', 0)}\n"
            f"• مُنشأة تلقائياً: {a['auto_created']}\n\n"
            f"**📦 الطلبات:**\n"
            f"• الإجمالي: {s['total_orders']}\n"
            f"• ✅ الناجح: {s['successful']}\n"
            f"• ❌ الفاشل: {s['failed']}\n"
            f"• 📈 معدل النجاح: {success_rate:.1f}%\n\n"
            f"{self.queue_mgr.status_markdown()}"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def run(self):
        if not TELEGRAM_BOT_TOKEN:
            logger.error("❌ توكن البوت غير موجود!")
            return

        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", self.start_cmd))
        app.add_handler(CommandHandler("follow", self.follow_cmd))
        app.add_handler(CommandHandler("queue", self.queue_cmd))
        app.add_handler(CommandHandler("add_token", self.add_token_cmd))
        app.add_handler(CommandHandler("stats", self.stats_cmd))

        async def after_start(_):
            self.proc.start()

        app.post_init = after_start

        logger.info("=" * 50)
        logger.info("✅ البوت جاهز للعمل!")
        logger.info(f"🤖 Token: {TELEGRAM_BOT_TOKEN[:20]}...")
        logger.info(f"👑 Admin: {ADMIN_ID}")
        logger.info("=" * 50)

        await app.run_polling(allowed_updates=Update.ALL_TYPES)


# ==============================================================================
# 🚀 نقطة البداية
# ==============================================================================
async def main():
    print("\n" + "=" * 60)
    print("🔥 بوت الطابور المصري - النسخة النهائية")
    print("👨‍💻 Developer: @zizo0022sasa")
    print("🇪🇬 Made with ❤️ in Egypt")
    print("=" * 60 + "\n")

    bot = TelegramBot()
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 تم إيقاف البوت بنجاح")
