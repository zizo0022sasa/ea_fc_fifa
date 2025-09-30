# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🎯 FC26 COIN SELLING HANDLER - معالج بيع الكوينز            ║
# ║                    Main Coin Selling Handler                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from typing import Dict, List, Optional
import re
import logging

from .sell_pricing import CoinSellPricing, Platform
from .sell_messages import SellMessages
from .sell_keyboards import SellKeyboards

# استيراد الأدوات المساعدة من البوت الرئيسي
from utils.logger import log_user_action
from database.operations import UserOperations

logger = logging.getLogger(__name__)

class SellCoinsHandler:
    """معالج خدمة بيع الكوينز الرئيسي"""

    def __init__(self):
        """تهيئة معالج البيع"""
        self.user_sessions = {}  # جلسات المستخدمين النشطة
        self.pending_sales = {}  # البيوعات المعلقة

    def get_handlers(self) -> List:
        """جلب جميع معالجات خدمة البيع"""
        return [
            CommandHandler("sell", self.handle_sell_command),
            CallbackQueryHandler(self.handle_platform_selection, pattern="^sell_platform_"),
            CallbackQueryHandler(self.handle_transfer_type_selection, pattern="^sell_transfer_"),
            CallbackQueryHandler(self.handle_custom_amount, pattern="^sell_custom_"),
            CallbackQueryHandler(self.handle_price_confirmation, pattern="^sell_confirm_"),
            CallbackQueryHandler(self.handle_sale_instructions, pattern="^sell_ready_"),
            CallbackQueryHandler(self.handle_payment_selection, pattern="^sell_payment_"),
            CallbackQueryHandler(self.handle_navigation, pattern="^sell_back_"),
            CallbackQueryHandler(self.handle_help, pattern="^sell_help"),
            CallbackQueryHandler(self.handle_cancel, pattern="^sell_cancel"),
            CallbackQueryHandler(self.handle_support, pattern="^sell_support"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_input)
        ]

    async def handle_sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /sell"""
        user_id = update.effective_user.id
        log_user_action(user_id, "Started coin selling service")

        # التحقق من تسجيل المستخدم
        user_data = UserOperations.get_user_data(user_id)
        if not user_data:
            await update.message.reply_text(
                "❌ <b>يجب التسجيل أولاً!</b>\n\n🚀 استخدم /start للتسجيل قبل بيع الكوينز",
                parse_mode="HTML"
            )
            return

        # بدء جلسة بيع جديدة
        self.user_sessions[user_id] = {
            'step': 'platform_selection',
            'platform': None,
            'coins': None,
            'price': None,
            'started_at': update.message.date
        }

        # عرض رسالة الترحيب
        welcome_message = SellMessages.get_welcome_sell_message()
        keyboard = SellKeyboards.get_main_sell_keyboard()

        await update.message.reply_text(
            welcome_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    async def handle_platform_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة اختيار المنصة"""
        query = update.callback_query
        user_id = query.from_user.id

        await query.answer()

        # استخراج المنصة من callback_data
        platform = query.data.replace("sell_platform_", "")

        # حفظ المنصة في الجلسة
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}

        self.user_sessions[user_id].update({
            'step': 'transfer_type_selection',
            'platform': platform
        })

        log_user_action(user_id, f"Selected platform: {platform}")

        # عرض رسالة الأسعار البسيطة
        transfer_message = CoinSellPricing.get_platform_pricing_message(platform)
        
        # جلب أسعار 1M للأزرار
        normal_price = CoinSellPricing.get_price(platform, 1000000, "normal")
        instant_price = CoinSellPricing.get_price(platform, 1000000, "instant")
        
        normal_formatted = f"{normal_price:,} ج.م" if normal_price else "غير متاح"
        instant_formatted = f"{instant_price:,} ج.م" if instant_price else "غير متاح"
        
        keyboard = [
            [InlineKeyboardButton(f"📅 تحويل عادي - {normal_formatted}", callback_data=f"sell_transfer_normal_{platform}")],
            [InlineKeyboardButton(f"⚡️ تحويل فوري - {instant_formatted}", callback_data=f"sell_transfer_instant_{platform}")],
            [InlineKeyboardButton("🔙 اختر منصة أخرى", callback_data="sell_back_platforms"),
             InlineKeyboardButton("🚫 إلغاء", callback_data="sell_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            transfer_message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    async def handle_transfer_type_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة اختيار نوع التحويل"""
        query = update.callback_query
        user_id = query.from_user.id

        await query.answer()

        # استخراج نوع التحويل والمنصة من callback_data
        # تنسيق: sell_transfer_{transfer_type}_{platform}
        parts = query.data.split("_")
        if len(parts) >= 4:
            transfer_type = parts[2]  # instant أو normal
            platform = parts[3]

            # حفظ نوع التحويل في الجلسة
            self.user_sessions[user_id].update({
                'step': 'amount_input',
                'transfer_type': transfer_type,
                'platform': platform
            })

            log_user_action(user_id, f"Selected transfer type: {transfer_type} for {platform}")

            # إعداد أسماء العرض
            platform_name = {"playstation": "🎮 PlayStation", "xbox": "🎮 Xbox", "pc": "🖥️ PC"}.get(platform, platform)
            transfer_name = "⚡ فوري" if transfer_type == "instant" else "📅 عادي"

            # رسالة طلب إدخال الكمية
            amount_message = f"""✅ **تم اختيار {platform_name} - {transfer_name}**

💰 **أدخل كمية الكوينز للبيع:**

📝 **قواعد الإدخال:**
• أرقام فقط (بدون حروف أو رموز)
• الحد الأدنى: 2 أرقام (مثال: 50)
• الحد الأقصى: 5 أرقام (مثال: 20000)
• ممنوع استخدام k أو m

💡 **أمثلة صحيحة:** 500، 1500، 20000

اكتب الكمية بالأرقام العادية:"""

            keyboard = [
                [InlineKeyboardButton("🔙 تغيير نوع التحويل", callback_data=f"sell_platform_{platform}")],
                [InlineKeyboardButton("🎮 تغيير المنصة", callback_data="sell_back_platforms")],
                [InlineKeyboardButton("🚫 إلغاء البيع", callback_data="sell_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                amount_message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )


    async def handle_custom_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة طلب كمية مخصصة"""
        query = update.callback_query
        user_id = query.from_user.id

        await query.answer()

        # استخراج المنصة
        platform = query.data.replace("sell_custom_", "")

        # تحديث الجلسة
        self.user_sessions[user_id].update({
            'step': 'custom_amount_input',
            'platform': platform
        })

        log_user_action(user_id, f"Requested custom amount for {platform}")

        # عرض رسالة طلب الكمية المخصصة
        custom_message = SellMessages.get_custom_amount_message(platform)
        keyboard = SellKeyboards.get_custom_amount_cancel_keyboard(platform)

        await query.edit_message_text(
            custom_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة النص المُدخل (للكمية المخصصة)"""
        user_id = update.effective_user.id

        # التحقق من وجود جلسة نشطة
        if user_id not in self.user_sessions:
            return

        session = self.user_sessions[user_id]

        # التحقق من الخطوة الحالية
        if session.get('step') not in ['custom_amount_input', 'amount_input']:
            return

        text = update.message.text.strip()
        platform = session.get('platform')
        transfer_type = session.get('transfer_type', 'normal')

        # تحليل الكمية المدخلة
        amount = self.parse_amount(text)

        # التحقق من الصيغة الخاطئة (k أو m)
        if amount == "invalid_format":
            await update.message.reply_text(
                "❌ **صيغة غير صحيحة!**\n\n"
                "🚫 **ممنوع استخدام k أو m**\n\n"
                "✅ **المطلوب:** أرقام فقط (2-5 أرقام)\n"
                "📝 **مثال صحيح:** 500 أو 1500 أو 20000\n\n"
                "يرجى إدخال الكمية بالأرقام العادية فقط:",
                parse_mode="Markdown"
            )
            return

        # التحقق من طول الرقم
        if amount == "invalid_length":
            await update.message.reply_text(
                "❌ **عدد الأرقام غير صحيح!**\n\n"
                "📍 **المطلوب:**\n"
                "• الحد الأدنى: 2 أرقام (مثال: 50)\n"
                "• الحد الأقصى: 5 أرقام (مثال: 20000)\n\n"
                f"أنت أدخلت: {len(text)} أرقام\n\n"
                "📝 **أمثلة صحيحة:** 500، 1500، 20000\n\n"
                "يرجى إدخال رقم بين 2-5 أرقام:",
                parse_mode="Markdown"
            )
            return

        # التحقق من صحة الصيغة العامة
        if amount is None:
            await update.message.reply_text(
                "❌ **صيغة غير صحيحة!**\n\n"
                "✅ **المطلوب:** أرقام فقط (2-5 أرقام)\n"
                "🚫 **ممنوع:** حروف، رموز، k، m\n\n"
                "📝 **أمثلة صحيحة:**\n"
                "• 500 \n"
                "• 1500 \n"
                "• 20000\n\n"
                "يرجى المحاولة مرة أخرى:",
                parse_mode="Markdown"
            )
            return

        # تعريف الحدود الفعلية
        MIN_SELL_AMOUNT = 50  # 50 كوين
        MAX_SELL_AMOUNT = 20000  # 20000 كوين

        # التحقق من الحدود
        if amount < MIN_SELL_AMOUNT:
            await update.message.reply_text(
                f"❌ **الكمية قليلة جداً!**\n\n"
                f"📍 **الحد الأدنى:** {self.format_amount(MIN_SELL_AMOUNT)} كوين\n"
                f"أنت أدخلت: {self.format_amount(amount)} كوين\n\n"
                "يرجى إدخال كمية أكبر:",
                parse_mode="Markdown"
            )
            return

        if amount > MAX_SELL_AMOUNT:
            await update.message.reply_text(
                f"❌ **الكمية كبيرة جداً!**\n\n"
                f"📍 **الحد الأقصى:** {self.format_amount(MAX_SELL_AMOUNT)} كوين\n"
                f"أنت أدخلت: {self.format_amount(amount)} كوين\n\n"
                "لبيع كميات أكبر، يرجى التواصل مع الدعم.",
                parse_mode="Markdown"
            )
            return

        coins = amount
        # حساب السعر للكمية المدخلة
        price = self.calculate_price(coins, transfer_type)

        # تحديث الجلسة
        session.update({
            'step': 'sale_completed',
            'coins': coins,
            'price': price
        })

        log_user_action(user_id, f"Entered amount: {coins} coins, {transfer_type} transfer, price: {price} EGP")

        # إعداد أسماء العرض
        platform_name = {"playstation": "🎮 PlayStation", "xbox": "🎮 Xbox", "pc": "🖥️ PC"}.get(platform, platform)
        transfer_name = "⚡ فوري" if transfer_type == "instant" else "📅 عادي"

        # رسالة التأكيد النهائية
        await update.message.reply_text(
            "🎉 **تم تأكيد طلب البيع بنجاح!**\n\n"
            f"📊 **تفاصيل الطلب:**\n"
            f"🎮 المنصة: {platform_name}\n"
            f"💰 الكمية: {self.format_amount(coins)} كوين\n"
            f"💵 السعر: {price} جنيه\n"
            f"⏰ نوع التحويل: {transfer_name}\n\n"
            "📞 **الخطوات التالية:**\n"
            "1️⃣ سيتم التواصل معك خلال دقائق\n"
            "2️⃣ تسليم الكوينز للممثل\n"
            "3️⃣ استلام المبلغ حسب نوع التحويل\n\n"
            "✅ **تم حفظ طلبك في النظام**\n"
            f"🆔 **رقم الطلب:** #{user_id}{coins}\n\n"
            "💬 **للاستفسار:** /sell\n"
            "🏠 **القائمة الرئيسية:** /start",
            parse_mode="Markdown"
        )

        # مسح بيانات المحادثة
        self.clear_user_session(user_id)

    async def handle_price_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة تأكيد السعر"""
        query = update.callback_query
        user_id = query.from_user.id

        await query.answer()

        # استخراج البيانات من callback_data
        # تنسيق: sell_confirm_{platform}_{coins}_{price}
        parts = query.data.split("_")
        if len(parts) >= 5:
            platform = parts[2]
            coins = int(parts[3])
            price = int(parts[4])

            # تحديث الجلسة
            self.user_sessions[user_id].update({
                'step': 'sale_instructions',
                'platform': platform,
                'coins': coins,
                'price': price
            })

            log_user_action(user_id, f"Confirmed sale: {coins} coins for {price} EGP")

            # عرض تعليمات البيع
            instructions_message = SellMessages.get_sale_instructions_message(platform, coins)
            keyboard = SellKeyboards.get_sale_instructions_keyboard(platform, coins)

            await query.edit_message_text(
                instructions_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )

    async def handle_sale_instructions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الموافقة على تعليمات البيع"""
        query = update.callback_query
        user_id = query.from_user.id

        await query.answer()

        session = self.user_sessions.get(user_id, {})

        # إنشاء طلب بيع
        sale_id = self._create_sale_request(user_id, session)

        log_user_action(user_id, f"Started sale process, sale_id: {sale_id}")

        # عرض اختيار طريقة الدفع
        payment_message = "💳 <b>اختر طريقة الدفع المفضلة:</b>\n\n" + \
                         "ستستلم أموالك على الطريقة المختارة فور إتمام البيع"
        keyboard = SellKeyboards.get_payment_method_keyboard()

        await query.edit_message_text(
            payment_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    async def handle_payment_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة اختيار طريقة الدفع"""
        query = update.callback_query
        user_id = query.from_user.id

        await query.answer()

        # استخراج طريقة الدفع
        payment_method = query.data.replace("sell_payment_", "")

        # حفظ طريقة الدفع في الجلسة
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['payment_method'] = payment_method

        log_user_action(user_id, f"Selected payment method: {payment_method}")

        # عرض رسالة نجاح البدء
        success_message = """✅ <b>تم بدء عملية البيع بنجاح!</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 <b>الخطوات التالية:</b>

1️⃣ سيتواصل معك فريق الدعم خلال 5 دقائق
2️⃣ سيتم إرشادك لتنفيذ التعليمات
3️⃣ ستستلم أموالك فور التأكد من الكوينز

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ <b>وقت الاستجابة:</b> 5-10 دقائق كحد أقصى
📞 <b>للاستعجال:</b> تواصل مع الدعم الفني

🎉 <b>شكراً لثقتك في FC26!</b>"""

        keyboard = SellKeyboards.get_sale_progress_keyboard()

        await query.edit_message_text(
            success_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    async def handle_navigation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة التنقل بين الصفحات"""
        query = update.callback_query
        user_id = query.from_user.id

        await query.answer()

        action = query.data.replace("sell_back_", "")

        if action == "main":
            # العودة للقائمة الرئيسية
            welcome_message = SellMessages.get_welcome_sell_message()
            keyboard = SellKeyboards.get_main_sell_keyboard()

            await query.edit_message_text(
                welcome_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )

        elif action == "platforms":
            # العودة لاختيار المنصة
            platform_message = SellMessages.get_platform_selection_message()
            keyboard = SellKeyboards.get_main_sell_keyboard()

            await query.edit_message_text(
                platform_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )



    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة طلب المساعدة"""
        query = update.callback_query
        await query.answer()

        help_message = SellMessages.get_help_message()
        keyboard = SellKeyboards.get_help_keyboard()

        await query.edit_message_text(
            help_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    async def handle_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إلغاء البيع"""
        query = update.callback_query
        user_id = query.from_user.id

        await query.answer()

        # إزالة الجلسة
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

        log_user_action(user_id, "Cancelled coin selling")

        cancel_message = SellMessages.get_error_message('sale_cancelled')
        keyboard = SellKeyboards.get_error_keyboard()

        await query.edit_message_text(
            cancel_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    async def handle_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة طلب الدعم الفني"""
        query = update.callback_query
        await query.answer()

        support_message = """📞 <b>الدعم الفني FC26</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 <b>متوفر 24/7 لخدمتك</b>

📱 <b>طرق التواصل:</b>
• الدردشة المباشرة في البوت
• واتساب: متوفر في ملفك الشخصي
• رسائل خاصة

⚡ <b>استجابة سريعة:</b> خلال دقائق معدودة

نحن هنا لمساعدتك! 🤝"""

        await query.edit_message_text(
            support_message,
            parse_mode="HTML"
        )

    def _create_sale_request(self, user_id: int, session: Dict) -> str:
        """إنشاء طلب بيع جديد"""
        import time

        sale_id = f"SALE_{user_id}_{int(time.time())}"

        # حفظ طلب البيع
        self.pending_sales[sale_id] = {
            'user_id': user_id,
            'platform': session.get('platform'),
            'coins': session.get('coins'),
            'price': session.get('price'),
            'status': 'pending',
            'created_at': time.time()
        }

        return sale_id

    def get_user_session(self, user_id: int) -> Optional[Dict]:
        """جلب جلسة المستخدم"""
        return self.user_sessions.get(user_id)

    def clear_user_session(self, user_id: int):
        """مسح جلسة المستخدم"""
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

    @staticmethod
    def parse_amount(text: str):
        """تحليل كمية الكوينز - أرقام فقط (2-5 أرقام)"""
        if not text or not isinstance(text, str):
            return None

        text = text.strip()

        # التحقق من وجود k أو m - ممنوع
        if "k" in text.lower() or "m" in text.lower():
            return "invalid_format"

        try:
            if not text.isdigit():
                return None

            number = int(text)

            # التحقق من عدد الأرقام (2-5 أرقام)
            if len(text) < 2 or len(text) > 5:
                return "invalid_length"

            return number

        except (ValueError, TypeError):
            return None

    @staticmethod
    def calculate_price(amount, transfer_type="normal"):
        """حساب السعر حسب الكمية ونوع التحويل"""
        base_price_per_1000 = 5  # 5 جنيه لكل 1000 كوين

        # حساب السعر الأساسي
        base_price = (amount / 1000) * base_price_per_1000

        # إضافة رسوم حسب نوع التحويل
        if transfer_type == "instant":
            base_price *= 1.2  # زيادة 20% للتحويل الفوري

        return int(base_price)

    @staticmethod
    def format_amount(amount: int) -> str:
        """
        تحويل الأرقام العادية لـ K/M format
        مثال: 915 -> 915 K | 1500 -> 1٬500 M
        """
        if not isinstance(amount, (int, float)):
            return "0"

        amount = int(amount)

        if 50 <= amount <= 999:
            # من 50 إلى 999: عرض بصيغة K
            return f"{amount} K"
        elif 1000 <= amount <= 20000:
            # من 1,000 إلى 20,000: عرض بصيغة M مع الفاصلة العربية
            formatted = f"{amount:,}".replace(",", "٬")
            return f"{formatted} M"
        else:
            # للقيم خارج النطاق: عرض بالأرقام العادية
            return str(amount)
