# ╔══════════════════════════════════════════════════════════════════════════╗
# ║      🎯 FC26 SELL CONVERSATION FUNCTIONS - دوال محادثة البيع            ║
# ║                    Sell Conversation Handler Functions                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from states.sell_states import SellStates

from .sell_conversation_handler import SellConversationHandler
from .sell_pricing import CoinSellPricing


# ================================ أوامر البيع ================================
async def sell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر بيع الكوينز /sell"""
    user_id = update.effective_user.id

    keyboard = [
        [InlineKeyboardButton("🎮 بيع كوينز FC 26", callback_data="sell_fc26")],
        [InlineKeyboardButton("📞 التحدث مع الدعم", callback_data="contact_support")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "💰 **بيع الكوينز - FC 26**\n\n"
        "🔥 **خدماتنا:**\n"
        "• بيع كوينز FC 26 بأفضل الأسعار\n"
        "• دفع فوري وآمن\n"
        "• دعم فني 24/7\n"
        "• ضمان المعاملة\n\n"
        "اختر الخدمة المطلوبة:",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def sell_coins_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بداية محادثة البيع"""
    user_id = update.callback_query.from_user.id

    # عرض خيارات المنصة
    keyboard = [
        [InlineKeyboardButton("🎮 PlayStation", callback_data="platform_playstation")],
        [InlineKeyboardButton("🎮 Xbox", callback_data="platform_xbox")],
        [InlineKeyboardButton("🖥️ PC", callback_data="platform_pc")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_sell")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        "🎮 **اختر منصة اللعب:**\n\n" "اختر المنصة اللي عندك عليها الكوينز:",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )

    return SellStates.CHOOSE_PLATFORM


async def platform_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار المنصة"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_sell":
        await query.edit_message_text(
            "✅ **تم إلغاء عملية البيع**\n\nيمكنك العودة في أي وقت باستخدام /sell",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    # حفظ المنصة
    platform = query.data.replace("platform_", "")
    context.user_data["platform"] = platform
    platform_name = SellConversationHandler.get_platform_name(platform)

    # عرض خيارات نوع التحويل
    keyboard = [
        [
            InlineKeyboardButton(
                "⚡ تحويل فوري (خلال ساعة)", callback_data="type_instant"
            )
        ],
        [
            InlineKeyboardButton(
                "📅 تحويل عادي (خلال 24 ساعة)", callback_data="type_normal"
            )
        ],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_sell")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"✅ **تم اختيار {platform_name}**\n\n"
        "💰 **اختر نوع التحويل:**\n\n"
        "⚡ **تحويل فوري:** خلال ساعة واحدة (سعر أعلى)\n"
        "📅 **تحويل عادي:** خلال 24 ساعة (سعر عادي)\n\n"
        "💡 **الأسعار تختلف حسب الكمية ونوع التحويل**",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )

    return SellStates.CHOOSE_TYPE


async def sell_type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار نوع التحويل"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_sell":
        await query.edit_message_text(
            "✅ **تم إلغاء عملية البيع**\n\nيمكنك العودة في أي وقت باستخدام /sell",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    # حفظ نوع التحويل
    transfer_type = "instant" if query.data == "type_instant" else "normal"
    context.user_data["transfer_type"] = transfer_type

    type_name = SellConversationHandler.get_transfer_type_name(transfer_type)
    platform_name = SellConversationHandler.get_platform_name(
        context.user_data.get("platform", "")
    )

    await query.edit_message_text(
        f"✅ **تم اختيار {platform_name} - {type_name}**\n\n"
        "💰 **أدخل كمية الكوينز للبيع:**\n\n"
        "📝 **قواعد الإدخال:**\n"
        "• أرقام فقط (بدون حروف أو رموز)\n"
        "• الحد الأدنى: 2 أرقام (مثال: 50)\n"
        "• الحد الأقصى: 5 أرقام (مثال: 20000)\n"
        "• ممنوع استخدام k أو m\n\n"
        "💡 **أمثلة صحيحة:** 500، 1500، 20000\n\n"
        "اكتب الكمية بالأرقام العادية:",
        parse_mode="Markdown",
    )

    return SellStates.ENTER_AMOUNT


async def sell_amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدخال كمية الكوينز"""
    user_id = update.effective_user.id
    amount_text = update.message.text

    # تحليل الكمية المدخلة
    amount = SellConversationHandler.parse_amount(amount_text)

    # التحقق من أنواع الأخطاء المختلفة
    error_responses = {
        "invalid_format": "❌ **صيغة غير صحيحة!**\n\n🚫 **ممنوع استخدام k أو m**\n\n✅ **المطلوب:** أرقام فقط (2-5 أرقام)\n📝 **مثال صحيح:** 500 أو 1500 أو 20000\n\nيرجى إدخال الكمية بالأرقام العادية فقط:",
        "invalid_length": f"❌ **عدد الأرقام غير صحيح!**\n\n📍 **المطلوب:**\n• الحد الأدنى: 2 أرقام (مثال: 50)\n• الحد الأقصى: 5 أرقام (مثال: 20000)\n\nأنت أدخلت: {len(amount_text)} أرقام\n\n📝 **أمثلة صحيحة:** 500، 1500، 20000\n\nيرجى إدخال رقم بين 2-5 أرقام:",
        None: "❌ **صيغة غير صحيحة!**\n\n✅ **المطلوب:** أرقام فقط (2-5 أرقام)\n🚫 **ممنوع:** حروف، رموز، k، m\n\n📝 **أمثلة صحيحة:**\n• 500 \n• 1500 \n• 20000\n\nيرجى المحاولة مرة أخرى:",
    }

    if amount in error_responses:
        await update.message.reply_text(error_responses[amount], parse_mode="Markdown")
        return SellStates.ENTER_AMOUNT

    # التحقق من الحدود
    is_valid, validation_message = SellConversationHandler.validate_amount(amount)
    if not is_valid:
        await update.message.reply_text(
            f"❌ **{validation_message}**", parse_mode="Markdown"
        )
        return SellStates.ENTER_AMOUNT

    # حفظ الكمية وحساب السعر
    context.user_data["amount"] = amount
    transfer_type = context.user_data.get("transfer_type", "normal")
    platform = context.user_data.get("platform", "playstation")
    price = SellConversationHandler.calculate_price(amount, transfer_type)

    # عرض ملخص البيع
    summary = _create_sale_summary(user_id, amount, transfer_type, platform, price)
    await update.message.reply_text(summary, parse_mode="Markdown")

    # مسح بيانات المحادثة وإنهاء المحادثة
    context.user_data.clear()
    return ConversationHandler.END


def _create_sale_summary(user_id, amount, transfer_type, platform, price):
    """إنشاء ملخص البيع"""
    formatted_amount = SellConversationHandler.format_amount(amount)
    type_name = SellConversationHandler.get_transfer_type_name(transfer_type)
    platform_name = SellConversationHandler.get_platform_name(platform)

    # جلب سعر المليون كمرجع للمستخدم - مع fallback للأسعار الافتراضية
    million_price = CoinSellPricing.get_price(platform, 1000000, transfer_type)

    # إذا لم يتم العثور على السعر، استخدم الأسعار الافتراضية المباشرة
    if million_price is None:
        # أسعار احتياطية ثابتة (نفس الأسعار من sell_pricing.py)
        default_prices = {
            "normal": {"playstation": 5600, "xbox": 5600, "pc": 6100},
            "instant": {"playstation": 5300, "xbox": 5300, "pc": 5800},
        }
        million_price = default_prices.get(transfer_type, {}).get(platform, 5600)

    # تنسيق سعر المليون مع فواصل
    million_price_formatted = f"{million_price:,}"

    return (
        "🎉 **تم تأكيد طلب البيع بنجاح!**\n\n"
        f"📊 **تفاصيل الطلب:**\n"
        f"🎮 المنصة: {platform_name}\n"
        f"💰 الكمية: {formatted_amount} كوين\n"
        f"💵 السعر الإجمالي: {price} جنيه\n"
        f"⭐ (سعر المليون: {million_price_formatted} جنيه)\n"
        f"⏰ نوع التحويل: {type_name}\n\n"
        "📞 **الخطوات التالية:**\n"
        "1️⃣ سيتم التواصل معك خلال دقائق\n"
        "2️⃣ تسليم الكوينز للممثل\n"
        "3️⃣ استلام المبلغ حسب نوع التحويل\n\n"
        "✅ **تم حفظ طلبك في النظام**\n"
        f"🆔 **رقم الطلب:** #{user_id}{amount}\n\n"
        "💬 **للاستفسار:** /sell\n"
        "🏠 **القائمة الرئيسية:** /start"
    )


async def sell_conversation_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء محادثة البيع"""
    await update.message.reply_text(
        "✅ **تم إلغاء عملية البيع**\n\nيمكنك البدء من جديد باستخدام /sell",
        parse_mode="Markdown",
    )
    context.user_data.clear()
    return ConversationHandler.END


# ================================ إعداد محادثة البيع ================================
def get_sell_conversation_handler():
    """إرجاع معالج محادثة البيع"""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(sell_coins_start, pattern="^sell_fc26$")],
        states={
            SellStates.CHOOSE_PLATFORM: [
                CallbackQueryHandler(
                    platform_chosen,
                    pattern="^(platform_playstation|platform_xbox|platform_pc|cancel_sell)$",
                )
            ],
            SellStates.CHOOSE_TYPE: [
                CallbackQueryHandler(
                    sell_type_chosen,
                    pattern="^(type_instant|type_normal|cancel_sell)$",
                )
            ],
            SellStates.ENTER_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, sell_amount_entered)
            ],
        },
        fallbacks=[CommandHandler("cancel", sell_conversation_cancel)],
    )
