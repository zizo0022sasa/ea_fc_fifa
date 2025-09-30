# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🚀 FC26 START HANDLER - معالج البدء                        ║
# ║                        Start Command Handler                             ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import Update
from telegram.ext import ContextTypes
from utils.logger import log_user_action, log_registration_step, logger
from utils.locks import user_lock_manager, is_rate_limited
from database.operations import UserOperations
from messages.welcome_messages import WelcomeMessages
from messages.error_messages import ErrorMessages
from keyboards.platform_keyboard import PlatformKeyboard
from handlers.continue_handler import handle_continue_registration

class StartHandler:
    """Handle /start command and user registration initialization"""
    
    @staticmethod
    async def handle_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Rate limiting check
        if is_rate_limited(user_id):
            await update.message.reply_text(ErrorMessages.get_rate_limit_error(), parse_mode="HTML")
            return
        
        log_user_action(user_id, "Started bot interaction", f"Username: @{username}")
        
        try:
            async with user_lock_manager.acquire_user_lock(user_id, "start_command"):
                await StartHandler._process_start_command(update, context)
                
        except Exception as e:
            logger.error(f"❌ Error in start handler for user {user_id}: {e}")
            await update.message.reply_text(ErrorMessages.get_general_error(), parse_mode="HTML")
    
    @staticmethod
    async def _process_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process start command with user checks"""
        user_id = update.effective_user.id
        
        # Check if user exists and their current step
        user_data = UserOperations.get_user_data(user_id)
        
        if user_data and user_data["registration_step"] != "start":
            # User exists and has started registration - continue from where they left
            log_registration_step(user_id, f"Continue from {user_data['registration_step']}")
            await handle_continue_registration(update, context, user_data)
            return
        
        # New user or user at start - show welcome and platform selection
        await StartHandler._show_welcome_and_platforms(update, context)
    
    @staticmethod
    async def _show_welcome_and_platforms(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show welcome message and platform selection"""
        user_id = update.effective_user.id
        
        try:
            # Create platform selection keyboard
            keyboard = PlatformKeyboard.create_platform_selection_keyboard()
            
            # Get welcome message
            welcome_text = WelcomeMessages.get_start_message()
            
            # Send message
            message = await update.message.reply_text(
                welcome_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
            # Save user step
            UserOperations.save_user_step(user_id, "choosing_platform")
            
            log_registration_step(user_id, "choosing_platform", True)
            log_user_action(user_id, "Shown platform selection", f"Message ID: {message.message_id}")
            
        except Exception as e:
            logger.error(f"❌ Error showing welcome to user {user_id}: {e}")
            await update.message.reply_text(ErrorMessages.get_general_error(), parse_mode="HTML")
    
    @staticmethod
    async def handle_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = update.effective_user.id
        
        if is_rate_limited(user_id):
            await update.message.reply_text(ErrorMessages.get_rate_limit_error(), parse_mode="HTML")
            return
        
        log_user_action(user_id, "Requested help")
        
        try:
            help_text = WelcomeMessages.get_help_message()
            await update.message.reply_text(help_text, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"❌ Error in help handler for user {user_id}: {e}")
            await update.message.reply_text(ErrorMessages.get_general_error(), parse_mode="HTML")
    
    @staticmethod
    async def handle_about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command"""
        user_id = update.effective_user.id
        
        if is_rate_limited(user_id):
            await update.message.reply_text(ErrorMessages.get_rate_limit_error(), parse_mode="HTML")
            return
        
        log_user_action(user_id, "Requested about info")
        
        try:
            about_text = WelcomeMessages.get_about_message()
            await update.message.reply_text(about_text, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"❌ Error in about handler for user {user_id}: {e}")
            await update.message.reply_text(ErrorMessages.get_general_error(), parse_mode="HTML")