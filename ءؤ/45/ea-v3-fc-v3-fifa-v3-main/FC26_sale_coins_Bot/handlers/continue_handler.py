# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🔄 FC26 CONTINUE HANDLER - معالج الاستكمال                 ║
# ║                    Continue Registration Handler                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import Update
from telegram.ext import ContextTypes
from messages.welcome_messages import WelcomeMessages
from keyboards.platform_keyboard import PlatformKeyboard
from keyboards.payment_keyboard import PaymentKeyboard
from utils.logger import log_user_action

async def handle_continue_registration(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
    """Handle continuing registration from where user left off"""
    user_id = update.effective_user.id
    step = user_data.get("registration_step", "start")
    
    log_user_action(user_id, f"Continue registration from step: {step}")
    
    try:
        # Get continuation message
        continue_text = WelcomeMessages.get_continue_registration_message(step, user_data)
        
        if step == "choosing_platform":
            # Show platform selection keyboard
            keyboard = PlatformKeyboard.create_platform_selection_keyboard()
            await update.message.reply_text(
                continue_text, 
                reply_markup=keyboard, 
                parse_mode="HTML"
            )
            
        elif step == "choosing_payment":
            # Show payment selection keyboard
            keyboard = PaymentKeyboard.create_payment_selection_keyboard()
            await update.message.reply_text(
                continue_text, 
                reply_markup=keyboard, 
                parse_mode="HTML"
            )
            
        elif step == "entering_whatsapp":
            # Just show the message for WhatsApp input
            await update.message.reply_text(continue_text, parse_mode="Markdown")
            
        elif step == "entering_payment_details":
            # Just show the message for payment details input
            await update.message.reply_text(continue_text, parse_mode="Markdown")
            
        else:
            # Default case - show basic continue message
            await update.message.reply_text(continue_text, parse_mode="Markdown")
            
    except Exception as e:
        from utils.logger import fc26_logger
        logger = fc26_logger.get_logger()
        logger.error(f"❌ Error in continue registration for user {user_id}: {e}")
        
        from messages.error_messages import ErrorMessages
        await update.message.reply_text(ErrorMessages.get_general_error(), parse_mode="HTML")