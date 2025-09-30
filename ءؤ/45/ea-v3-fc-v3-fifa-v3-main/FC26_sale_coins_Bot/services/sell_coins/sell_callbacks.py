# ╔══════════════════════════════════════════════════════════════════════════╗
# ║            🎯 FC26 SELL CALLBACKS - معالجات أزرار البيع                ║
# ║                      Sell Callback Handlers                             ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def handle_sell_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار البيع"""
    query = update.callback_query
    await query.answer()

    if query.data == "contact_support":
        await query.edit_message_text(
            "📞 **التواصل مع الدعم**\n\n"
            "🔥 **للمعاملات السريعة:**\n"
            "واتساب الدعم: `01094591331`\n\n"
            "⚡ **أوقات العمل:**\n"
            "• 24 ساعة يومياً\n"
            "• 7 أيام في الأسبوع\n"
            "• رد سريع خلال دقائق\n\n"
            "💬 **اكتب رسالتك وسنرد عليك فوراً**",
            parse_mode="Markdown"
        )
    
    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("💰 بيع الكوينز", callback_data="sell_coins_menu")],
            [InlineKeyboardButton("📞 الدعم", callback_data="contact_support")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🏠 **القائمة الرئيسية - FC 26**\n\n"
            "مرحباً بك في بوت FC 26\n"
            "اختر الخدمة المطلوبة:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif query.data == "sell_coins_menu":
        keyboard = [
            [InlineKeyboardButton("🎮 بيع كوينز FC 26", callback_data="sell_fc26")],
            [InlineKeyboardButton("📞 التحدث مع الدعم", callback_data="contact_support")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "💰 **بيع الكوينز - FC 26**\n\n"
            "🔥 **خدماتنا:**\n"
            "• بيع كوينز FC 26 بأفضل الأسعار\n"
            "• دفع فوري وآمن\n"
            "• دعم فني 24/7\n"
            "• ضمان المعاملة\n\n"
            "اختر الخدمة المطلوبة:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )