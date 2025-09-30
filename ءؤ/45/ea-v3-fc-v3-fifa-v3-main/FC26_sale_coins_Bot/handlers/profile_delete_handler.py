# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🗑️ FC26 PROFILE DELETE HANDLER - معالج مسح الملف الشخصي      ║
# ║                     Profile Management & Deletion                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from typing import List

# Import database operations
from database.operations import UserOperations

# Import logging utilities
from utils.logger import log_user_action, fc26_logger

# Import messages
from messages.error_messages import ErrorMessages

class ProfileDeleteHandler:
    """Handle profile management and deletion functionality"""
    
    @staticmethod
    def create_profile_management_keyboard():
        """Create keyboard for profile management with delete option"""
        keyboard = [
            [InlineKeyboardButton("🗑️ مسح الملف الشخصي", callback_data="delete_profile_confirm")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_delete_confirmation_keyboard():
        """Create confirmation keyboard for profile deletion"""
        keyboard = [
            [
                InlineKeyboardButton("❌ نعم، امسح كل شيء", callback_data="delete_profile_execute"),
                InlineKeyboardButton("✅ لا، راجع تاني", callback_data="delete_profile_cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    async def handle_delete_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle delete profile confirmation dialog"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "غير محدد"
        
        logger = fc26_logger.get_logger()
        logger.info(f"🗑️ User {user_id} requested profile deletion confirmation")
        
        try:
            await query.answer()
            
            # Check if user exists
            user_data = UserOperations.get_user_data(user_id)
            if not user_data:
                await query.edit_message_text(
                    "❌ لم يتم العثور على ملف شخصي لحذفه!\n\n🚀 اكتب /start لبدء التسجيل",
                    parse_mode="HTML"
                )
                return
            
            # Create confirmation message
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
            
            await query.edit_message_text(
                confirmation_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
            log_user_action(user_id, f"Profile deletion confirmation shown", f"@{username}")
            
        except Exception as e:
            logger.error(f"❌ Error showing deletion confirmation for user {user_id}: {e}")
            await query.edit_message_text(
                ErrorMessages.get_general_error(),
                parse_mode="HTML"
            )
    
    @staticmethod
    async def handle_delete_execution(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute profile deletion"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "غير محدد"
        
        logger = fc26_logger.get_logger()
        logger.info(f"🗑️ User {user_id} confirmed profile deletion - executing...")
        
        try:
            await query.answer()
            
            # Check if user exists before deletion
            user_data = UserOperations.get_user_data(user_id)
            if not user_data:
                await query.edit_message_text(
                    "❌ <b>الملف الشخصي غير موجود!</b>\n\n🚀 اكتب /start لبدء التسجيل من جديد",
                    parse_mode="HTML"
                )
                return
            
            # Execute deletion
            deletion_success = UserOperations.delete_user(user_id)
            
            if deletion_success:
                # Success message
                success_message = f"""✅ <b>تم مسح الملف الشخصي بنجاح!</b>

🗑️ <b>البيانات الممسوحة:</b>
• جميع معلومات التسجيل
• سجل الأنشطة والإحصائيات  
• البيانات الشخصية والدفع
• سجل الأخطاء المرتبط بالحساب

<b>🎮 أهلاً بك من جديد في FC26!</b>

🚀 <b>للتسجيل مرة أخرى:</b>
اكتب /start وابدأ رحلتك من جديد

<b>👋 شكراً لاستخدامك بوت FC26</b>"""
                
                await query.edit_message_text(success_message, parse_mode="HTML")
                
                log_user_action(user_id, f"Profile deletion completed successfully", f"@{username}")
                logger.info(f"✅ User {user_id} profile deleted successfully")
                
            else:
                # Failure message
                await query.edit_message_text(
                    "❌ <b>حدث خطأ أثناء مسح الملف الشخصي!</b>\n\n🔄 الرجاء المحاولة مرة أخرى أو التواصل مع الدعم الفني",
                    parse_mode="HTML"
                )
                logger.error(f"❌ Failed to delete user {user_id} profile")
        
        except Exception as e:
            logger.error(f"❌ Error executing profile deletion for user {user_id}: {e}")
            await query.edit_message_text(
                ErrorMessages.get_general_error(),
                parse_mode="HTML"
            )
    
    @staticmethod
    async def handle_delete_cancellation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle profile deletion cancellation"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "غير محدد"
        
        logger = fc26_logger.get_logger()
        logger.info(f"🚫 User {user_id} cancelled profile deletion")
        
        try:
            await query.answer("تم الإلغاء - لم يحدث أي تغيير")
            
            cancellation_message = """✅ <b>تم إلغاء العملية بنجاح!</b>

🛡️ <b>لم يتم مسح أي بيانات</b>
📊 ملفك الشخصي آمن ولم يتأثر

<b>🎮 يمكنك الآن:</b>
• 👤 اكتب /profile لعرض ملفك الشخصي
• 📞 اكتب /help للمساعدة والدعم  
• 🏠 اكتب /start للقائمة الرئيسية

<b>💚 شكراً لك على الحذر!</b>"""

            await query.edit_message_text(cancellation_message, parse_mode="HTML")
            
            log_user_action(user_id, f"Profile deletion cancelled", f"@{username}")
            
        except Exception as e:
            logger = fc26_logger.get_logger()
            logger.error(f"❌ Error handling deletion cancellation for user {user_id}: {e}")
            await query.edit_message_text(
                ErrorMessages.get_general_error(),
                parse_mode="HTML"
            )
    
    @staticmethod
    def get_handlers() -> List[CallbackQueryHandler]:
        """Get all callback handlers for profile deletion"""
        return [
            CallbackQueryHandler(ProfileDeleteHandler.handle_delete_confirmation, pattern="^delete_profile_confirm$"),
            CallbackQueryHandler(ProfileDeleteHandler.handle_delete_execution, pattern="^delete_profile_execute$"),
            CallbackQueryHandler(ProfileDeleteHandler.handle_delete_cancellation, pattern="^delete_profile_cancel$")
        ]