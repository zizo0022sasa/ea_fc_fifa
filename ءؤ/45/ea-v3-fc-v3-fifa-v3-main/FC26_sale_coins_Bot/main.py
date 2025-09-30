# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                🎮 FC26 GAMING BOT - MODULAR MAIN FILE                    ║
# ║                     بوت FC26 للألعاب - الملف الرئيسي                   ║
# ║                        🔥 PRODUCTION READY 🔥                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import asyncio
import platform as sys_platform
import sys
from telegram.ext import (
    Application,
    CallbackQueryHandler, 
    CommandHandler,
    MessageHandler,
    filters,
)

# Import configuration
from config import BOT_TOKEN, ENVIRONMENT, DEBUG

# Import database initialization
from database.models import DatabaseModels
from database.operations import UserOperations, StatisticsOperations

# Import utilities
from utils.logger import fc26_logger, log_user_action, log_database_operation
from utils.locks import user_lock_manager, is_rate_limited

# Import validators
from validators.phone_validator import PhoneValidator
from validators.payment_validator import PaymentValidator
from validators.url_validator import URLValidator

# Import message handlers
from messages.welcome_messages import WelcomeMessages
from messages.confirmation_msgs import ConfirmationMessages
from messages.error_messages import ErrorMessages
from messages.summary_messages import SummaryMessages

# Import keyboard handlers
from keyboards.platform_keyboard import PlatformKeyboard
from keyboards.payment_keyboard import PaymentKeyboard

# Import profile delete handler
from handlers.profile_delete_handler import ProfileDeleteHandler

# Import coin selling service
from services.sell_coins import SellCoinsHandler

class FC26Bot:
    """Main FC26 Gaming Bot class"""
    
    def __init__(self):
        self.app = None
        self.logger = fc26_logger.get_logger()
        
        # Initialize services
        self.sell_coins_handler = SellCoinsHandler()
        
        # Initialize admin system
        try:
            from services.admin import AdminHandler
            self.admin_handler = AdminHandler()
            self.logger.info("✅ Admin system initialized successfully")
        except ImportError as e:
            self.admin_handler = None
            self.logger.warning(f"⚠️ Admin system not available: {e}")
        

    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def handle_start(self, update, context):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        if is_rate_limited(user_id):
            self.logger.info(f"🚫 Rate limited user {user_id}")
            await update.message.reply_text(ErrorMessages.get_rate_limit_error())
            return
        
        log_user_action(user_id, "Started bot", f"@{username}")
        
        try:
            async with user_lock_manager.acquire_user_lock(user_id, "start"):
                # Check existing user
                user_data = UserOperations.get_user_data(user_id)
                self.logger.info(f"📊 User {user_id} data: {user_data}")
                
                if user_data:
                    current_step = user_data.get("registration_step", "unknown")
                    self.logger.info(f"👤 User {user_id} current step: {current_step}")
                    
                    if current_step == "completed":
                        # User has completed registration - show main menu
                        self.logger.info(f"✅ User {user_id} registration completed - showing main menu")
                        await self._show_main_menu(update, context, user_data)
                        return
                    elif current_step != "start":
                        # User is in middle of registration - continue
                        self.logger.info(f"🔄 User {user_id} continuing from step: {current_step}")
                        await self._continue_registration(update, context, user_data)
                        return
                
                # New user or user at start - show welcome and platforms
                self.logger.info(f"🆕 New user {user_id} - showing platform selection")
                keyboard = PlatformKeyboard.create_platform_selection_keyboard()
                welcome_text = WelcomeMessages.get_start_message()
                
                await update.message.reply_text(welcome_text, reply_markup=keyboard, parse_mode="HTML")
                UserOperations.save_user_step(user_id, "choosing_platform")
                
        except Exception as e:
            self.logger.error(f"❌ Start error for user {user_id}: {e}")
            await update.message.reply_text(ErrorMessages.get_general_error())
    
    async def handle_help(self, update, context):
        """Handle /help command"""
        user_id = update.effective_user.id
        log_user_action(user_id, "Requested help")
        
        help_text = WelcomeMessages.get_help_message()
        await update.message.reply_text(help_text, parse_mode="HTML")
    
    async def handle_profile(self, update, context):
        """Handle /profile command"""
        user_id = update.effective_user.id
        log_user_action(user_id, "Requested profile")
        
        user_data = UserOperations.get_user_data(user_id)
        if not user_data:
            await update.message.reply_text(ErrorMessages.get_start_required_error())
            return
        
        profile_text = SummaryMessages.create_user_profile_summary(user_data)
        
        # Add profile management keyboard with delete option
        keyboard = ProfileDeleteHandler.create_profile_management_keyboard()
        
        await update.message.reply_text(
            profile_text, 
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_delete(self, update, context):
        """Handle /delete command - direct profile deletion"""
        user_id = update.effective_user.id
        log_user_action(user_id, "Requested profile deletion via /delete command")
        
        user_data = UserOperations.get_user_data(user_id)
        if not user_data:
            await update.message.reply_text(
                "❌ <b>لا يوجد ملف شخصي للحذف!</b>\n\n🚀 اكتب /start لبدء التسجيل",
                parse_mode="HTML"
            )
            return
        
        # Show deletion confirmation directly
        username = update.effective_user.username or "غير محدد"
        
        confirmation_text = f"""⚠️ <b>تحذير هام!</b>

🗑️ <b>أنت على وشك مسح ملفك الشخصي نهائياً</b>

<b>📋 سيتم مسح البيانات التالية:</b>
• 🎮 المنصة: {user_data.get('platform', 'غير محدد')}
• 📱 رقم الواتساب: {user_data.get('whatsapp', 'غير محدد')}  
• 💳 طريقة الدفع: {user_data.get('payment_method', 'غير محدد')}
• 📊 سجل التسجيل والإحصائيات
• 🗂️ جميع البيانات المرتبطة بحسابك

<b>⚠️ هذا الإجراء لا يمكن التراجع عنه!</b>

<b>🔄 بعد المسح:</b>
• ستحتاج للتسجيل من البداية
• ستفقد جميع بياناتك المحفوظة
• لن نتمكن من استرداد أي معلومات

<b>👤 المستخدم:</b> @{username}
<b>🆔 معرف التليجرام:</b> {user_id}

<b>❓ هل أنت متأكد من رغبتك في المتابعة؟</b>"""
        
        keyboard = ProfileDeleteHandler.create_delete_confirmation_keyboard()
        
        await update.message.reply_text(
            confirmation_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CALLBACK HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def handle_platform_choice(self, update, context):
        """Handle platform selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        self.logger.info(f"🎮 User {user_id} selecting platform: {query.data}")
        
        try:
            async with user_lock_manager.acquire_user_lock(user_id, "platform_selection"):
                await query.answer()
                
                platform_key = query.data.replace("platform_", "")
                platform_name = PlatformKeyboard.get_platform_name(platform_key)
                
                self.logger.info(f"✅ User {user_id} selected platform: {platform_name}")
                
                # Update user data
                UserOperations.save_user_step(user_id, "entering_whatsapp", {"platform": platform_key})
                
                # Send WhatsApp request message
                success_text = WelcomeMessages.get_platform_selected_message(platform_name)
                await query.edit_message_text(success_text, parse_mode="HTML")
                
                log_user_action(user_id, f"Selected platform: {platform_key}")
                
        except Exception as e:
            self.logger.error(f"❌ Platform choice error: {e}")
            await query.answer(ErrorMessages.get_general_error(), show_alert=True)
    
    async def handle_payment_choice(self, update, context):
        """Handle payment method selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        self.logger.info(f"💳 User {user_id} selecting payment method: {query.data}")
        
        try:
            async with user_lock_manager.acquire_user_lock(user_id, "payment_selection"):
                await query.answer()
                
                payment_key = query.data.replace("payment_", "")
                payment_name = PaymentKeyboard.get_payment_display_name(payment_key)
                
                self.logger.info(f"✅ User {user_id} selected payment: {payment_name}")
                
                # Get user data
                user_data = UserOperations.get_user_data(user_id)
                if not user_data:
                    await query.answer(ErrorMessages.get_start_required_error(), show_alert=True)
                    return
                
                # Update user data
                UserOperations.save_user_step(user_id, "entering_payment_details", {
                    "platform": user_data["platform"],
                    "whatsapp": user_data["whatsapp"],
                    "payment_method": payment_key
                })
                
                # Send payment details request
                instruction = PaymentValidator.get_payment_instructions(payment_key)
                details_text = WelcomeMessages.get_payment_method_selected_message(payment_name, instruction)
                await query.edit_message_text(details_text, parse_mode="HTML")
                
                log_user_action(user_id, f"Selected payment: {payment_key}")
                
        except Exception as e:
            self.logger.error(f"❌ Payment choice error: {e}")
            await query.answer(ErrorMessages.get_general_error(), show_alert=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MESSAGE HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def handle_message(self, update, context):
        """Handle text messages"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        self.logger.info(f"📩 Message from user {user_id}: '{message_text}'")
        
        # Note: Admin messages are handled by a separate handler with group=1 (higher priority)
        # This handler only processes non-admin messages (group=0 - default priority)
        
        user_data = UserOperations.get_user_data(user_id)
        
        if not user_data:
            self.logger.info(f"⚠️ User {user_id} has no data - requiring /start")
            await update.message.reply_text(ErrorMessages.get_start_required_error())
            return
        
        step = user_data.get("registration_step", "unknown")
        self.logger.info(f"📝 User {user_id} in step '{step}' sent message")
        
        if step == "entering_whatsapp":
            await self._handle_whatsapp_input(update, context, user_data)
        elif step == "entering_payment_details":
            await self._handle_payment_details(update, context, user_data)
        elif step == "completed":
            # User completed registration - guide them
            self.logger.info(f"✅ Completed user {user_id} sent message - guiding to main menu")
            await update.message.reply_text(
                "✅ <b>لقد أكملت التسجيل بالفعل!</b>\n\n"
                "🔹 اضغط <code>/profile</code> لعرض ملفك الشخصي\n"
                "🔹 اضغط <code>/help</code> للمساعدة\n"
                "🔹 اضغط <code>/start</code> للقائمة الرئيسية",
                parse_mode="HTML"
            )
        else:
            self.logger.info(f"🔄 User {user_id} in unexpected step '{step}' - requiring restart")
            await update.message.reply_text(ErrorMessages.get_restart_required_error())
    
    async def _handle_whatsapp_input(self, update, context, user_data):
        """Handle WhatsApp number input"""
        user_id = update.effective_user.id
        phone = update.message.text.strip()
        
        self.logger.info(f"📱 User {user_id} entered WhatsApp: {phone[:4]}***{phone[-4:] if len(phone) > 8 else '***'}")
        
        # Validate phone
        validation = PhoneValidator.validate_whatsapp(phone)
        if not validation["valid"]:
            self.logger.info(f"❌ User {user_id} WhatsApp validation failed: {validation['error']}")
            error_msg = ErrorMessages.get_phone_validation_error(validation["error"])
            await update.message.reply_text(error_msg, parse_mode="HTML")
            return
        
        self.logger.info(f"✅ User {user_id} WhatsApp validated successfully")
        
        # Create payment keyboard
        keyboard = PaymentKeyboard.create_payment_selection_keyboard()
        success_text = WelcomeMessages.get_whatsapp_confirmed_message(validation["display"])
        
        message = await update.message.reply_text(success_text, reply_markup=keyboard, parse_mode="HTML")
        
        # Update user data
        UserOperations.save_user_step(user_id, "choosing_payment", {
            "platform": user_data["platform"],
            "whatsapp": validation["cleaned"]
        })
        
        log_user_action(user_id, f"WhatsApp validated: {validation['display']}")
    
    async def _handle_payment_details(self, update, context, user_data):
        """Handle payment details input"""
        user_id = update.effective_user.id
        details = update.message.text.strip()
        
        self.logger.info(f"💰 User {user_id} entered payment details for: {user_data.get('payment_method', 'unknown')}")
        
        # Validate payment details
        validation = PaymentValidator.validate_payment_details(user_data["payment_method"], details)
        if not validation["valid"]:
            self.logger.info(f"❌ User {user_id} payment validation failed: {validation['error']}")
            error_msg = ErrorMessages.get_payment_validation_error(user_data["payment_method"], validation["error"])
            await update.message.reply_text(error_msg, parse_mode="HTML")
            return
        
        self.logger.info(f"✅ User {user_id} payment details validated successfully - completing registration")
        
        # Create confirmation message
        payment_name = PaymentKeyboard.get_payment_display_name(user_data["payment_method"])
        confirmation = ConfirmationMessages.create_payment_confirmation(user_data["payment_method"], validation, payment_name)
        await update.message.reply_text(confirmation)
        
        # Create final summary
        user_info = {"id": user_id, "username": update.effective_user.username or "غير متوفر"}
        final_summary = ConfirmationMessages.create_final_summary(user_data, payment_name, validation, user_info)
        await update.message.reply_text(final_summary, parse_mode="HTML")
        
        # Complete registration
        UserOperations.save_user_step(user_id, "completed", {
            "platform": user_data["platform"],
            "whatsapp": user_data["whatsapp"], 
            "payment_method": user_data["payment_method"],
            "payment_details": validation["cleaned"]
        })
        
        # Update statistics
        StatisticsOperations.update_daily_metric("completed_registrations")
        
        log_user_action(user_id, "Registration completed successfully")
    
    async def _continue_registration(self, update, context, user_data):
        """Continue registration from last step"""
        step = user_data["registration_step"]
        user_id = update.effective_user.id
        
        self.logger.info(f"🔄 User {user_id} continuing registration from step: {step}")
        
        continue_text = WelcomeMessages.get_continue_registration_message(step, user_data)
        
        if step == "choosing_platform":
            keyboard = PlatformKeyboard.create_platform_selection_keyboard()
            await update.message.reply_text(continue_text, reply_markup=keyboard, parse_mode="HTML")
        elif step == "choosing_payment":
            keyboard = PaymentKeyboard.create_payment_selection_keyboard()
            await update.message.reply_text(continue_text, reply_markup=keyboard, parse_mode="HTML")
        else:
            await update.message.reply_text(continue_text, parse_mode="HTML")
    
    async def _show_main_menu(self, update, context, user_data):
        """Show main menu for completed users"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Create main menu message
        platform = user_data.get("platform", "غير محدد")
        whatsapp = user_data.get("whatsapp", "غير محدد")
        
        main_menu_text = f"""✅ <b>أهلاً وسهلاً بعودتك!</b>

👤 <b>المستخدم:</b> @{username}
🎮 <b>المنصة:</b> {platform}
📱 <b>الواتساب:</b> <code>{whatsapp}</code>

<b>🏠 القائمة الرئيسية:</b>

🔹 <code>/profile</code> - عرض الملف الشخصي
🔹 <code>/help</code> - المساعدة والدعم
🔹 <b>تواصل معنا للخدمات</b>

<b>🎯 خدماتنا:</b>
• شراء وبيع العملات
• تجارة اللاعبين
• خدمات التطوير
• دعم فني متخصص

💬 <b>للحصول على الخدمات تواصل مع الإدارة</b>"""

        await update.message.reply_text(main_menu_text, parse_mode="HTML")
        log_user_action(user_id, "Shown main menu", f"Platform: {platform}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN EXECUTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def start_bot(self):
        """Start the bot"""
        
        # Windows event loop fix - must be called before any async operations
        if sys_platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            self.logger.info("✅ Windows event loop policy configured")
        
        # Initialize database
        self.logger.info("💾 Initializing database...")
        success = DatabaseModels.create_all_tables()
        if success:
            self.logger.info("✅ Database initialized successfully")
            log_database_operation("Database initialized", success=True)
        else:
            self.logger.error("❌ Database initialization failed")
            log_database_operation("Database initialization", success=False)
            return
        
        # Create application
        self.app = Application.builder().token(BOT_TOKEN).build()
        
        # Setup handlers
        self.logger.info("🔧 Setting up bot handlers...")
        
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.handle_start))
        self.app.add_handler(CommandHandler("help", self.handle_help))
        self.app.add_handler(CommandHandler("profile", self.handle_profile))
        self.app.add_handler(CommandHandler("delete", self.handle_delete))
        
        # Callback query handlers
        self.app.add_handler(CallbackQueryHandler(self.handle_platform_choice, pattern="^platform_"))
        self.app.add_handler(CallbackQueryHandler(self.handle_payment_choice, pattern="^payment_"))
        
        # Profile delete handlers
        for handler in ProfileDeleteHandler.get_handlers():
            self.app.add_handler(handler)
        
        # Coin selling service handlers
        for handler in self.sell_coins_handler.get_handlers():
            self.app.add_handler(handler)
        
        # Admin system handlers (MUST be before main message handler)
        if self.admin_handler:
            admin_handlers = self.admin_handler.get_handlers()
            print(f"\n🔧 [SYSTEM] Registering {len(admin_handlers)} admin handlers...")
            
            for i, handler in enumerate(admin_handlers, 1):
                self.app.add_handler(handler)
                handler_type = type(handler).__name__
                print(f"   {i:2d}. {handler_type} registered")
            
            # 🔥🔥 HIGH PRIORITY: Admin text input handler with group=1 🔥🔥
            # This handler MUST be checked BEFORE the general message handler
            # group=1 gives it higher priority than group=0 (default)
            self.app.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_handler.handle_price_input),
                group=1
            )
            print("   🔑 [PRIORITY] Admin text input handler registered with HIGH PRIORITY (group=1)")
            
            self.logger.info("✅ Admin system handlers configured")
            print("✅ [SYSTEM] All admin handlers registered successfully")
        else:
            print("❌ [SYSTEM] Admin handler not available!")
        
        # Message handlers (this should be last to avoid conflicts)
        # group=0 (default) - lower priority than admin handler
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        print("🔧 [SYSTEM] Main message handler registered (group=0 - default priority)")
        
        self.logger.info("✅ All handlers configured successfully")
        
        # Log startup
        fc26_logger.log_bot_start()
        
        print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                     🎮 FC26 GAMING BOT - MODULAR 🎮                     ║
║                        بوت FC26 للألعاب - النسخة المنظمة                ║
║                                                                          ║
║  🏗️ ADVANCED MODULAR ARCHITECTURE:                                      ║
║  📦 28 specialized files in organized folders                           ║
║  💾 Advanced database with statistics & logging                         ║
║  ✅ Enhanced validation & security                                      ║
║  📝 Comprehensive message management                                     ║
║  🎯 Professional handler system                                         ║
║  🔒 Anti-conflict locks & rate limiting                                 ║
║  🚀 Production-ready with error handling                                ║
║                                                                          ║
║  🌟 READY FOR GITHUB & PRODUCTION DEPLOYMENT!                           ║
╚══════════════════════════════════════════════════════════════════════════╝
        """)
        
        # Start polling
        try:
            self.app.run_polling(drop_pending_updates=True)
        except Exception as e:
            self.logger.error(f"❌ Critical error: {e}")
        finally:
            fc26_logger.log_bot_stop()

def main():
    """Main entry point"""
    # Configure Windows event loop before creating any async operations
    if sys_platform.system() == "Windows":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except:
            pass
    
    try:
        bot = FC26Bot()
        bot.start_bot()
    except KeyboardInterrupt:
        print("🔴 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
