#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 بوت التليجرام الاحترافي - النسخة النهائية المُصلحة
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
from datetime import datetime
from typing import Dict, List, Optional

import requests
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# ==============================================================================
# 🔐 الإعدادات
# ==============================================================================
TELEGRAM_BOT_TOKEN = "7958170099:AAHsSsdd4WiE1MkZMSUQlm0QpzDYDL-rN5Y"
ADMIN_ID = 1124247595

# API Settings
API_BASE_URL = "https://freefollower.net/api"
TOKENS_FILE = "tokens.json"
STATS_FILE = "stats.json"

# Service Settings
FREE_SERVICE_ID = 196

# States للمحادثة
WAITING_LINK, WAITING_QUANTITY = range(2)

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
# 🛠️ الفئات الأساسية
# ==============================================================================


class TokenManager:
    """مدير التوكنات المتعددة"""

    def __init__(self):
        self.tokens = self.load_tokens()
        self.used_tokens = set()

    def load_tokens(self) -> List[Dict]:
        """تحميل التوكنات من الملف"""
        try:
            if os.path.exists(TOKENS_FILE):
                with open(TOKENS_FILE, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"خطأ في تحميل التوكنات: {e}")
        return []

    def save_tokens(self):
        """حفظ التوكنات"""
        try:
            with open(TOKENS_FILE, "w") as f:
                json.dump(self.tokens, f, indent=2)
        except Exception as e:
            logger.error(f"خطأ في حفظ التوكنات: {e}")

    def add_token(self, token_data: str) -> str:
        """إضافة توكن جديد مع التحقق من التكرار"""
        try:
            # محاولة تحليل JSON
            if token_data.startswith("{"):
                data = json.loads(token_data)
                token = data.get("token", "")
                username = data.get("username", "unknown")
                password = data.get("password", "")
            else:
                # توكن مباشر
                token = token_data.strip()
                username = "imported"
                password = ""

            # التحقق من التكرار
            for existing in self.tokens:
                if existing.get("token") == token:
                    return "⚠️ التوكن موجود بالفعل!"

            # إضافة التوكن
            new_token = {
                "token": token,
                "username": username,
                "password": password,
                "added_at": datetime.now().isoformat(),
                "used": False,
            }

            self.tokens.append(new_token)
            self.save_tokens()

            return f"✅ تم إضافة التوكن بنجاح!\n👤 المستخدم: {username}\n📊 إجمالي التوكنات: {len(self.tokens)}"

        except json.JSONDecodeError:
            return "❌ صيغة JSON غير صحيحة!"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"

    def get_available_token(self) -> Optional[Dict]:
        """الحصول على توكن غير مستخدم"""
        for token in self.tokens:
            if not token.get("used", False) and token["token"] not in self.used_tokens:
                return token
        return None

    def mark_used(self, token: str):
        """تحديد التوكن كمستخدم"""
        self.used_tokens.add(token)
        for t in self.tokens:
            if t["token"] == token:
                t["used"] = True
        self.save_tokens()

    def get_stats(self) -> Dict:
        """إحصائيات التوكنات"""
        total = len(self.tokens)
        used = sum(1 for t in self.tokens if t.get("used", False))
        available = total - used
        return {"total": total, "used": used, "available": available}


class OrderProcessor:
    """معالج الطلبات"""

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

    def calculate_accounts_needed(self, followers: int) -> int:
        """حساب عدد الحسابات المطلوبة"""
        # كل حساب يعطي 10 متابعين
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
        }

        for i in range(accounts_needed):
            token_data = self.token_manager.get_available_token()

            if not token_data:
                results["failed"] += 1
                logger.warning("❌ لا توجد توكنات متاحة!")
                continue

            token = token_data["token"]
            success = self.send_order(token, link, 10)

            if success:
                results["successful"] += 1
                results["tokens_used"].append(token_data["username"])
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
        self.token_manager = TokenManager()
        self.order_processor = OrderProcessor(self.token_manager)
        self.user_data = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        user = update.effective_user

        if user.id != ADMIN_ID:
            await update.message.reply_text("❌ عذراً، هذا البوت خاص بالأدمن فقط!")
            return

        keyboard = [
            [KeyboardButton("/new - طلب جديد")],
            [KeyboardButton("/token - إضافة توكنات")],
            [KeyboardButton("/stats - الإحصائيات")],
            [KeyboardButton("/help - المساعدة")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        message = (
            "🔥 **أهلاً يا كبير!**\n"
            "ده البوت المصري الاحترافي\n\n"
            "**الأوامر المتاحة:**\n"
            "/new - طلب جديد (ابعت لينك وعدد)\n"
            "/token - إضافة توكنات متعددة\n"
            "/stats - عرض الإحصائيات\n"
            "/help - المساعدة\n\n"
            "🇪🇬 صُنع بكل حب في مصر"
        )

        await update.message.reply_text(
            message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )

    async def new_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء طلب جديد"""
        if update.effective_user.id != ADMIN_ID:
            return ConversationHandler.END

        await update.message.reply_text(
            "📱 **طلب جديد**\n\n"
            "ابعت لينك التيك توك:\n"
            "مثال: https://www.tiktok.com/@username",
            parse_mode=ParseMode.MARKDOWN,
        )

        return WAITING_LINK

    async def receive_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """استقبال اللينك"""
        link = update.message.text.strip()

        # التحقق من اللينك
        if not self.order_processor.validate_tiktok_link(link):
            await update.message.reply_text(
                "❌ اللينك غير صحيح!\n" "تأكد إنه لينك تيك توك صحيح"
            )
            return WAITING_LINK

        # حفظ اللينك
        context.user_data["link"] = link

        await update.message.reply_text(
            "✅ تمام، اللينك صحيح!\n\n"
            "دلوقتي ابعت عدد المتابعين:\n"
            "مثال: 1000\n\n"
            "📊 ملاحظة:\n"
            "• 100 متابع = 10 حسابات\n"
            "• 1000 متابع = 100 حساب",
            parse_mode=ParseMode.MARKDOWN,
        )

        return WAITING_QUANTITY

    async def receive_quantity(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """استقبال العدد ومعالجة الطلب"""
        try:
            quantity = int(update.message.text.strip())

            if quantity <= 0:
                await update.message.reply_text("❌ العدد لازم يكون أكبر من صفر!")
                return WAITING_QUANTITY

            link = context.user_data.get("link")
            accounts_needed = self.order_processor.calculate_accounts_needed(quantity)

            # التحقق من التوكنات المتاحة
            token_stats = self.token_manager.get_stats()

            if token_stats["available"] < accounts_needed:
                await update.message.reply_text(
                    f"⚠️ **مفيش توكنات كفاية!**\n\n"
                    f"محتاجين: {accounts_needed} حساب\n"
                    f"متاح: {token_stats['available']} حساب\n\n"
                    f"استخدم /token لإضافة توكنات جديدة",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return ConversationHandler.END

            # رسالة البداية
            await update.message.reply_text(
                f"⏳ **جاري المعالجة...**\n\n"
                f"📱 اللينك: {link}\n"
                f"👥 المتابعين: {quantity}\n"
                f"📊 الحسابات المطلوبة: {accounts_needed}\n\n"
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
                f"👥 متابعين تم إرسالهم: {results['successful'] * 10}\n\n"
            )

            if results["tokens_used"]:
                message += "**الحسابات المستخدمة:**\n"
                for i, username in enumerate(results["tokens_used"][:10], 1):
                    message += f"{i}. {username}\n"

                tokens_count = len(results["tokens_used"])
                if tokens_count > 10:
                    remaining = tokens_count - 10
                    message += f"... و {remaining} آخرين\n"

            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

        except ValueError:
            await update.message.reply_text("❌ ابعت رقم صحيح!")
            return WAITING_QUANTITY
        except Exception as e:
            logger.error(f"خطأ في معالجة الطلب: {e}")
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

        return ConversationHandler.END

    async def add_tokens(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إضافة توكنات جديدة"""
        if update.effective_user.id != ADMIN_ID:
            return

        if not context.args:
            await update.message.reply_text(
                "📝 **طريقة إضافة التوكنات:**\n\n"
                "**طريقة 1 - JSON:**\n"
                '`/token {"token": "YOUR_TOKEN", "username": "user", "password": "pass"}`\n\n'
                "**طريقة 2 - توكن مباشر:**\n"
                "`/token YOUR_TOKEN_HERE`\n\n"
                "**طريقة 3 - عدة توكنات:**\n"
                "ابعت كل توكن في سطر منفصل",
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
            f"• المستخدم: {token_stats['used']}\n"
            f"• المتاح: {token_stats['available']}\n\n"
            f"**📦 الطلبات:**\n"
            f"• الإجمالي: {order_stats['total_orders']}\n"
            f"• الناجح: {order_stats['successful']}\n"
            f"• الفاشل: {order_stats['failed']}\n\n"
            f"**📈 المعدلات:**\n"
        )

        if order_stats["total_orders"] > 0:
            success_rate = (
                order_stats["successful"] / order_stats["total_orders"]
            ) * 100
            message += f"• معدل النجاح: {success_rate:.1f}%\n"

        message += "\n⚡ بدون حد أقصى للطلبات"

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """المساعدة"""
        if update.effective_user.id != ADMIN_ID:
            return

        message = (
            "📚 **دليل الاستخدام**\n"
            f"{'='*25}\n\n"
            "**1️⃣ طلب جديد:**\n"
            "• اكتب /new\n"
            "• ابعت لينك التيك توك\n"
            "• ابعت عدد المتابعين\n"
            "• البوت هيحسب الحسابات المطلوبة\n\n"
            "**2️⃣ إضافة توكنات:**\n"
            "• /token + التوكن أو JSON\n"
            "• البوت بيتحقق من التكرار\n\n"
            "**3️⃣ الإحصائيات:**\n"
            "• /stats لعرض كل الأرقام\n\n"
            "**📝 ملاحظات:**\n"
            "• كل حساب = 10 متابعين\n"
            "• 1000 متابع = 100 حساب\n"
            "• البوت بيستنى 5-10 ثواني بين الطلبات\n\n"
            "🔥 صُنع بكل حب في مصر 🇪🇬"
        )

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء العملية الحالية"""
        await update.message.reply_text("❌ تم الإلغاء")
        return ConversationHandler.END

    async def handle_token_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """معالج رسائل التوكنات"""
        if update.effective_user.id != ADMIN_ID:
            return

        text = update.message.text

        # التحقق من وجود توكن
        if "{" in text and "token" in text:
            result = self.token_manager.add_token(text)
            await update.message.reply_text(result)
        elif len(text) > 30:  # ربما يكون توكن
            result = self.token_manager.add_token(text)
            await update.message.reply_text(result)


# ==============================================================================
# 🚀 التشغيل الرئيسي
# ==============================================================================


def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل البوت...")

    # إنشاء البوت
    bot = TelegramBot()

    # إنشاء التطبيق
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # معالج المحادثة للطلبات
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("new", bot.new_order)],
        states={
            WAITING_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot.receive_link)
            ],
            WAITING_QUANTITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot.receive_quantity)
            ],
        },
        fallbacks=[CommandHandler("cancel", bot.cancel)],
    )

    # إضافة المعالجات
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("token", bot.add_tokens))
    application.add_handler(CommandHandler("stats", bot.show_stats))
    application.add_handler(CommandHandler("help", bot.help_command))
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