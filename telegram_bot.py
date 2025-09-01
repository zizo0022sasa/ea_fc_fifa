#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 بوت التليجرام الاحترافي - نسخة بدون أزرار مع إنشاء حسابات تلقائي
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
TELEGRAM_BOT_TOKEN = "7958170099:AAG-aAVxqOTQmsvrP7viKIo0-KP0AzJUGDE"  # ضع التوكن هنا
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
# 🛠️ مولد الحسابات التلقائي
# ==============================================================================


class AccountGenerator:
    """مولد الحسابات التلقائي"""

    def __init__(self):
        self.email_domains = [
            "gmail.com",
            "hotmail.com",
            "outlook.com",
            "yahoo.com",
            "icloud.com",
        ]
        self.first_names = [
            "ahmed",
            "mohamed",
            "sara",
            "fatma",
            "ali",
            "omar",
            "yasmin",
            "nour",
            "hassan",
            "hussein",
            "mona",
            "laila",
            "karim",
            "salma",
            "tarek",
            "dina",
            "rania",
            "sameh",
        ]
        self.last_names = [
            "hassan",
            "ahmed",
            "mohamed",
            "ali",
            "salem",
            "farouk",
            "khalil",
            "nasser",
            "saeed",
            "rashad",
            "gamal",
            "mostafa",
        ]

    def generate_username(self) -> str:
        """توليد اسم مستخدم عشوائي"""
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        number = random.randint(10, 999)
        styles = [
            f"{first}_{last}{number}",
            f"{first}.{last}{number}",
            f"{first}{last}_{number}",
            f"{first}_{number}",
            f"{last}_{first}{number}",
        ]
        return random.choice(styles)

    def generate_password(self) -> str:
        """توليد كلمة مرور قوية"""
        # كلمة مرور: حروف كبيرة + صغيرة + أرقام + رموز
        upper = random.choices(string.ascii_uppercase, k=2)
        lower = random.choices(string.ascii_lowercase, k=4)
        digits = random.choices(string.digits, k=3)
        symbols = random.choice("!@#$%^&*")

        password_chars = upper + lower + digits + [symbols]
        random.shuffle(password_chars)
        return "".join(password_chars)

    def generate_email(self, username: str) -> str:
        """توليد إيميل بناءً على اسم المستخدم"""
        domain = random.choice(self.email_domains)
        # تنظيف اسم المستخدم من النقاط للإيميل
        clean_username = username.replace(".", "_")
        return f"{clean_username}@{domain}"

    def create_account(self) -> Dict:
        """إنشاء حساب جديد كامل"""
        username = self.generate_username()
        password = self.generate_password()
        email = self.generate_email(username)

        return {
            "username": username,
            "password": password,
            "email": email,
            "created_at": datetime.now().isoformat(),
        }

    def register_on_api(self, account_data: Dict) -> Optional[str]:
        """تسجيل الحساب على API والحصول على توكن"""
        try:
            payload = {
                "login": account_data["username"],
                "email": account_data["email"],
                "password": account_data["password"],
            }

            response = requests.post(
                f"{API_BASE_URL}/register",
                json=payload,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0"},
            )

            if response.status_code == 201:
                data = response.json()
                token = data.get("api_token")
                if token:
                    logger.info(f"✅ تم إنشاء حساب جديد: {account_data['username']}")
                    return token
            else:
                logger.error(f"❌ فشل التسجيل: {response.text}")
        except Exception as e:
            logger.error(f"❌ خطأ في التسجيل: {e}")

        return None


# ==============================================================================
# 🔑 مدير التوكنات المطور
# ==============================================================================


class EnhancedTokenManager:
    """مدير التوكنات مع ميزة إنشاء الحسابات التلقائية"""

    def __init__(self):
        self.tokens = self.load_tokens()
        self.accounts = self.load_accounts()
        self.account_generator = AccountGenerator()

    def load_tokens(self) -> List[Dict]:
        """تحميل التوكنات من الملف"""
        try:
            if os.path.exists(TOKENS_FILE):
                with open(TOKENS_FILE, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"خطأ في تحميل التوكنات: {e}")
        return []

    def load_accounts(self) -> List[Dict]:
        """تحميل الحسابات من الملف"""
        try:
            if os.path.exists(ACCOUNTS_FILE):
                with open(ACCOUNTS_FILE, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"خطأ في تحميل الحسابات: {e}")
        return []

    def save_tokens(self):
        """حفظ التوكنات"""
        try:
            with open(TOKENS_FILE, "w") as f:
                json.dump(self.tokens, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"خطأ في حفظ التوكنات: {e}")

    def save_accounts(self):
        """حفظ الحسابات"""
        try:
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump(self.accounts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"خطأ في حفظ الحسابات: {e}")

    def validate_token_format(self, token: str) -> bool:
        """التحقق من صيغة التوكن"""
        if not token:
            return False
        # التوكن يجب أن يكون 50-70 حرف alphanumeric
        if not re.match(r"^[a-zA-Z0-9]{50,70}$", token):
            return False
        return True

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

            # إضافة التوكن
            new_token = {
                "token": token,
                "username": username,
                "email": email,
                "password": password,
                "added_at": datetime.now().isoformat(),
                "last_used": None,
                "use_count": 0,
            }

            self.tokens.append(new_token)
            self.save_tokens()

            # حفظ معلومات الحساب إذا كانت متوفرة
            if email and password:
                account = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "token": token,
                    "created_at": datetime.now().isoformat(),
                }
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
                return token_data

            last_used_time = datetime.fromisoformat(last_used)
            time_diff = now - last_used_time

            if time_diff.total_seconds() >= (TOKEN_COOLDOWN_HOURS * 3600):
                # التوكن متاح للاستخدام
                return token_data

        # لا يوجد توكن متاح، نحاول إنشاء حساب جديد
        logger.info("🔄 لا توجد توكنات متاحة، جاري إنشاء حساب جديد...")
        return self.create_new_account()

    def create_new_account(self) -> Optional[Dict]:
        """إنشاء حساب جديد تلقائياً"""
        account = self.account_generator.create_account()
        token = self.account_generator.register_on_api(account)

        if token:
            # إضافة التوكن الجديد
            new_token = {
                "token": token,
                "username": account["username"],
                "email": account["email"],
                "password": account["password"],
                "added_at": datetime.now().isoformat(),
                "last_used": None,
                "use_count": 0,
                "auto_created": True,
            }

            self.tokens.append(new_token)
            self.save_tokens()

            # حفظ معلومات الحساب
            account["token"] = token
            self.accounts.append(account)
            self.save_accounts()

            logger.info(f"✅ تم إنشاء حساب جديد تلقائياً: {account['username']}")
            return new_token

        return None

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
                last_used_time = datetime.fromisoformat(last_used)
                if (now - last_used_time).total_seconds() >= (
                    TOKEN_COOLDOWN_HOURS * 3600
                ):
                    available += 1

        auto_created = sum(1 for t in self.tokens if t.get("auto_created", False))

        return {
            "total": total,
            "available": available,
            "on_cooldown": total - available,
            "auto_created": auto_created,
            "total_accounts": len(self.accounts),
        }


# ==============================================================================
# 🚀 معالج الطلبات
# ==============================================================================


class OrderProcessor:
    """معالج الطلبات"""

    def __init__(self, token_manager: EnhancedTokenManager):
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
            "auto_accounts_created": 0,
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

    def send_order(self, token: str, link: str, quantity: int = 10) -> bool:
        """إرسال طلب واحد"""
        try:
            payload = {
                "key": token,
                "action": "add",
                "service": FREE_SERVICE_ID,
                "link": link,
                "quantity": quantity,
            }

            response = requests.post(
                f"{API_BASE_URL}/v2",
                json=payload,
                timeout=20,
                headers={"User-Agent": "Mozilla/5.0"},
            )

            if response.status_code == 200:
                data = response.json()
                if "order" in data:
                    logger.info(f"✅ طلب ناجح: {data['order']}")
                    return True
                else:
                    logger.error(f"❌ فشل: {data.get('error', 'Unknown')}")

            return False

        except Exception as e:
            logger.error(f"❌ خطأ في الطلب: {e}")
            return False

    def process_bulk_order(self, link: str, total_followers: int) -> Dict:
        """معالجة طلب كبير بتوكنات متعددة"""
        accounts_needed = self.calculate_accounts_needed(total_followers)

        results = {
            "requested": total_followers,
            "accounts_needed": accounts_needed,
            "successful": 0,
            "failed": 0,
            "tokens_used": [],
            "auto_accounts_created": 0,
        }

        for i in range(accounts_needed):
            token_data = self.token_manager.get_available_token()

            if not token_data:
                results["failed"] += 1
                logger.warning("❌ لا توجد توكنات متاحة ولم نتمكن من إنشاء حساب جديد!")
                continue

            # تتبع الحسابات المُنشأة تلقائياً
            if token_data.get("auto_created", False):
                results["auto_accounts_created"] += 1
                self.stats["auto_accounts_created"] = (
                    self.stats.get("auto_accounts_created", 0) + 1
                )

            token = token_data["token"]
            success = self.send_order(token, link, 10)

            if success:
                results["successful"] += 1
                results["tokens_used"].append(token_data.get("username", "unknown"))
                self.token_manager.mark_used(token)
                self.stats["successful"] += 1
            else:
                results["failed"] += 1
                self.stats["failed"] += 1

            self.stats["total_orders"] += 1

            # انتظار عشوائي بين الطلبات
            if i < accounts_needed - 1:
                wait_time = random.uniform(5, 10)
                logger.info(f"⏰ انتظار {wait_time:.1f} ثانية...")
                time.sleep(wait_time)

        self.save_stats()
        return results


# ==============================================================================
# 🤖 البوت الرئيسي
# ==============================================================================


class TelegramBot:
    """البوت الرئيسي"""

    def __init__(self):
        self.token_manager = EnhancedTokenManager()
        self.order_processor = OrderProcessor(self.token_manager)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية - بدون أزرار"""
        user = update.effective_user

        if user.id != ADMIN_ID:
            await update.message.reply_text("❌ عذراً، هذا البوت خاص بالأدمن فقط!")
            return

        message = (
            "🔥 **أهلاً يا كبير!**\n"
            "ده البوت الاحترافي بدون أزرار\n\n"
            "**الأوامر المتاحة:**\n"
            "`/follow [لينك] [عدد]` - طلب متابعين\n"
            "`/token [توكن]` - إضافة توكن\n"
            "`/stats` - عرض الإحصائيات\n\n"
            "**الميزات الجديدة:**\n"
            "✅ إنشاء حسابات تلقائياً عند الحاجة\n"
            "✅ إدارة ذكية للتوكنات (25 ساعة cooldown)\n"
            "✅ إيميلات حقيقية (Gmail, Hotmail, Yahoo, iCloud)\n\n"
            "**مثال:**\n"
            "`/follow https://tiktok.com/@username 1000`\n\n"
            "🇪🇬 صُنع بكل حب في مصر"
        )

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    async def follow_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة طلب المتابعين"""
        if update.effective_user.id != ADMIN_ID:
            return

        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ **صيغة غلط!**\n\n"
                "الصيغة الصحيحة:\n"
                "`/follow [لينك] [عدد]`\n\n"
                "مثال:\n"
                "`/follow https://tiktok.com/@username 1000`",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        link = context.args[0]

        try:
            quantity = int(context.args[1])
        except ValueError:
            await update.message.reply_text(
                "❌ العدد لازم يكون رقم!\n"
                "مثال: `/follow https://tiktok.com/@username 1000`",
                parse_mode=ParseMode.MARKDOWN,
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
        await update.message.reply_text(
            f"⏳ **جاري المعالجة...**\n\n"
            f"📱 اللينك: {link}\n"
            f"👥 المتابعين: {quantity}\n"
            f"📊 الحسابات المطلوبة: {accounts_needed}\n"
            f"🎫 التوكنات المتاحة: {token_stats['available']}\n\n"
            f"💡 سيتم إنشاء حسابات جديدة تلقائياً إذا لزم الأمر\n"
            f"انتظر شوية...",
            parse_mode=ParseMode.MARKDOWN,
        )

        # معالجة الطلب
        results = self.order_processor.process_bulk_order(link, quantity)

        # عرض النتائج
        success_rate = (
            (results["successful"] / accounts_needed * 100)
            if accounts_needed > 0
            else 0
        )

        message = (
            f"📊 **نتيجة الطلب**\n"
            f"{'='*20}\n"
            f"✅ نجح: {results['successful']}/{accounts_needed}\n"
            f"❌ فشل: {results['failed']}\n"
            f"📈 معدل النجاح: {success_rate:.1f}%\n"
            f"👥 متابعين تم إرسالهم: {results['successful'] * 10}\n"
        )

        if results["auto_accounts_created"] > 0:
            message += (
                f"🆕 حسابات جديدة تم إنشاؤها: {results['auto_accounts_created']}\n"
            )

        message += "\n"

        if results["tokens_used"]:
            message += "**الحسابات المستخدمة:**\n"
            for i, username in enumerate(results["tokens_used"][:10], 1):
                message += f"{i}. {username}\n"

            tokens_count = len(results["tokens_used"])
            if tokens_count > 10:
                remaining = tokens_count - 10
                message += f"... و {remaining} آخرين\n"

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    async def add_tokens(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إضافة توكنات جديدة"""
        if update.effective_user.id != ADMIN_ID:
            return

        if not context.args:
            await update.message.reply_text(
                "📝 **طريقة إضافة التوكنات:**\n\n"
                "**طريقة 1 - توكن مباشر:**\n"
                "`/token YOUR_TOKEN_HERE`\n\n"
                "**طريقة 2 - JSON كامل:**\n"
                '`/token {"token": "TOKEN", "username": "user", "email": "email@domain.com", "password": "pass"}`\n\n'
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
            f"**📈 المعدلات:**\n"
        )

        if order_stats["total_orders"] > 0:
            success_rate = (
                order_stats["successful"] / order_stats["total_orders"]
            ) * 100
            message += f"• معدل النجاح: {success_rate:.1f}%\n"

        message += "\n⚡ نظام إنشاء الحسابات التلقائي مفعّل"

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
            if re.match(r"^[a-zA-Z0-9]+$", text.strip()):
                result = self.token_manager.add_token(text)
                await update.message.reply_text(result)


# ==============================================================================
# 🚀 التشغيل الرئيسي
# ==============================================================================


def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل البوت الاحترافي...")

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

    logger.info(f"✅ البوت جاهز! Token: {TELEGRAM_BOT_TOKEN[:20]}...")

    # بدء البوت
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
