# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              👑 FC26 ADMIN HANDLER - معالج الادارة الرئيسي               ║
# ║                     Main Admin Handler                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from typing import List, Dict, Optional
import logging
import sys
import os

# إضافة مسار المشروع للاستيراد
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.admin_operations import AdminOperations
from .admin_messages import AdminMessages
from .admin_keyboards import AdminKeyboards
from .price_management import PriceManagement

logger = logging.getLogger(__name__)

class AdminHandler:
    """معالج الادارة الرئيسي"""
    
    # معرف الادمن
    ADMIN_ID = 1124247595
    
    def __init__(self):
        """تهيئة معالج الادارة"""
        self.user_sessions = {}  # جلسات تعديل الأسعار
        
        # تهيئة قاعدة البيانات
        AdminOperations.init_admin_db()
        
        print(f"\n👑 [ADMIN] AdminHandler initialized for admin ID: {self.ADMIN_ID}")
        print(f"🔐 [ADMIN] Session storage ready for price editing workflows")
        
        # طباعة الـ callback patterns للتصحيح
        self.debug_callback_patterns()
        
        logger.info("✅ Admin handler initialized")
    
    def get_handlers(self) -> List:
        """جلب جميع معالجات الادارة"""
        print(f"\n🔧 [ADMIN] Registering admin handlers...")
        
        handlers = [
            # أوامر الادمن
            CommandHandler("admin", self.handle_admin_command),
            CommandHandler("prices", self.handle_prices_command),
            
            # معالجات الأزرار
            CallbackQueryHandler(self.handle_admin_main, pattern="^admin_main$"),
            CallbackQueryHandler(self.handle_price_management, pattern="^admin_prices$"),
            CallbackQueryHandler(self.handle_view_prices, pattern="^admin_view_prices$"),
            CallbackQueryHandler(self.handle_platform_edit, pattern="^admin_edit_(playstation|xbox|pc)$"),
            CallbackQueryHandler(self.handle_transfer_type_edit, pattern="^admin_edit_(playstation|xbox|pc)_(normal|instant)$"),
            CallbackQueryHandler(self.handle_admin_logs, pattern="^admin_logs$"),
            CallbackQueryHandler(self.handle_admin_stats, pattern="^admin_stats$"),
            
            # معالج عام للـ callbacks غير المعروفة (آخر واحد عشان ميتداخلش)
            CallbackQueryHandler(self.handle_unknown_callback, pattern="^admin_.*$")
        ]
        
        print(f"✅ [ADMIN] {len(handlers)} admin handlers prepared for registration")
        print(f"🎯 [ADMIN] Handlers include: commands and callbacks")
        print(f"📝 [ADMIN] Note: Admin text message handler will be registered separately with group=1")
        return handlers
    
    def is_admin(self, user_id: int) -> bool:
        """التحقق من صلاحية الادمن"""
        is_authorized = user_id == self.ADMIN_ID
        if not is_authorized:
            print(f"⚠️ [ADMIN] Unauthorized access attempt from user {user_id} (Expected: {self.ADMIN_ID})")
        return is_authorized
    
    def debug_callback_patterns(self):
        """طباعة جميع الـ callback patterns المتاحة للتصحيح"""
        patterns = [
            "admin_main",
            "admin_prices", 
            "admin_view_prices",
            "admin_edit_playstation",
            "admin_edit_xbox", 
            "admin_edit_pc",
            "admin_edit_playstation_normal",
            "admin_edit_playstation_instant",
            "admin_edit_xbox_normal",
            "admin_edit_xbox_instant",
            "admin_edit_pc_normal",
            "admin_edit_pc_instant",
            "admin_logs",
            "admin_stats"
        ]
        
        print(f"\n🎯 [ADMIN] Available callback patterns:")
        for i, pattern in enumerate(patterns, 1):
            print(f"   {i:2d}. {pattern}")
        print(f"📊 [ADMIN] Total patterns: {len(patterns)}")
        
        return patterns
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def handle_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /admin"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        print(f"\n🔑 [ADMIN] Admin command received from user {user_id} (@{username})")
        
        if not self.is_admin(user_id):
            print(f"❌ [ADMIN] Unauthorized access attempt by user {user_id}")
            await update.message.reply_text(
                AdminMessages.get_unauthorized_message(),
                reply_markup=AdminKeyboards.get_unauthorized_keyboard(),
                parse_mode="HTML"
            )
            return
        
        print(f"✅ [ADMIN] Admin {user_id} successfully logged in")
        
        # تسجيل دخول الادمن
        AdminOperations.log_admin_action(user_id, "ADMIN_LOGIN", f"Accessed via /admin command")
        
        # عرض لوحة الادارة
        message = AdminMessages.get_main_admin_message(user_id)
        keyboard = AdminKeyboards.get_main_admin_keyboard()
        
        await update.message.reply_text(
            message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        print(f"📊 [ADMIN] Admin dashboard sent to user {user_id}")
    
    async def handle_prices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /prices - عرض الأسعار مباشرة"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text(
                AdminMessages.get_unauthorized_message(),
                reply_markup=AdminKeyboards.get_unauthorized_keyboard(),
                parse_mode="HTML"
            )
            return
        
        # عرض الأسعار مباشرة
        await self._show_current_prices(update, user_id)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CALLBACK HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def handle_admin_main(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج العودة للقائمة الرئيسية"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        
        print(f"\n🏠 [ADMIN] Main menu callback received from user {user_id} (@{username})")
        print(f"📞 [ADMIN] Callback data: {query.data}")
        
        await query.answer()
        print(f"✅ [ADMIN] Callback answered for user {user_id}")
        
        if not self.is_admin(user_id):
            await query.edit_message_text(
                AdminMessages.get_unauthorized_message(),
                reply_markup=AdminKeyboards.get_unauthorized_keyboard(),
                parse_mode="HTML"
            )
            return
        
        message = AdminMessages.get_main_admin_message(user_id)
        keyboard = AdminKeyboards.get_main_admin_keyboard()
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_price_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج إدارة الأسعار"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        
        print(f"\n💰 [ADMIN] Price management callback received from user {user_id} (@{username})")
        print(f"📞 [ADMIN] Callback data: {query.data}")
        
        await query.answer()
        print(f"✅ [ADMIN] Callback answered for user {user_id}")
        
        if not self.is_admin(user_id):
            await query.edit_message_text(AdminMessages.get_unauthorized_message())
            return
        
        AdminOperations.log_admin_action(user_id, "ACCESSED_PRICE_MANAGEMENT")
        
        message = AdminMessages.get_price_management_message()
        keyboard = AdminKeyboards.get_price_management_keyboard()
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_view_prices(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج عرض الأسعار الحالية"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        
        await query.answer()
        
        print(f"\n📊 [ADMIN] View prices requested by {user_id} (@{username})")
        
        if not self.is_admin(user_id):
            print(f"❌ [ADMIN] Unauthorized view prices request from user {user_id}")
            return
        
        await self._show_current_prices_callback(query, user_id)
        print(f"✅ [ADMIN] Prices displayed to admin {user_id}")
    
    async def handle_platform_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج اختيار منصة للتعديل"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        
        print(f"\n🎮 [ADMIN] Platform edit callback received from user {user_id} (@{username})")
        print(f"📞 [ADMIN] Callback data: {query.data}")
        
        await query.answer()
        print(f"✅ [ADMIN] Callback answered for user {user_id}")
        
        if not self.is_admin(user_id):
            return
        
        # استخراج اسم المنصة
        platform = query.data.split("_")[-1]  # admin_edit_playstation -> playstation
        print(f"🔧 [ADMIN] Extracted platform: {platform}")
        
        AdminOperations.log_admin_action(user_id, "SELECTED_PLATFORM_EDIT", f"Platform: {platform}")
        print(f"📝 [ADMIN] Action logged for platform selection: {platform}")
        
        message = AdminMessages.get_platform_edit_message(platform)
        keyboard = AdminKeyboards.get_platform_edit_keyboard(platform)
        print(f"📋 [ADMIN] Message and keyboard prepared for platform: {platform}")
        
        try:
            await query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            print(f"✅ [ADMIN] Platform edit interface sent successfully for {platform}")
        except Exception as e:
            print(f"❌ [ADMIN] Failed to send platform edit interface: {e}")
    
    async def handle_transfer_type_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج اختيار نوع التحويل للتعديل"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        
        await query.answer()
        
        print(f"\n⚡ [ADMIN] Transfer type edit requested by {user_id} (@{username})")
        
        if not self.is_admin(user_id):
            print(f"❌ [ADMIN] Unauthorized callback from user {user_id}")
            return
        
        # استخراج البيانات من callback_data
        # تنسيق: admin_edit_playstation_normal
        print(f"🔍 [ADMIN] Parsing callback data: '{query.data}'")
        
        try:
            parts = query.data.split("_")
            print(f"📋 [ADMIN] Split parts: {parts}")
            
            if len(parts) < 4:
                print(f"❌ [ADMIN] Invalid callback data format: expected 4 parts, got {len(parts)}")
                return
                
            platform = parts[2]  # playstation
            transfer_type = parts[3]  # normal
            
            print(f"🎮 [ADMIN] Successfully extracted - Platform: {platform}, Type: {transfer_type}")
            
        except Exception as e:
            print(f"❌ [ADMIN] Error parsing callback data: {e}")
            return
        
        # جلب السعر الحالي
        current_price = PriceManagement.get_current_price(platform, transfer_type)
        
        if current_price is None:
            print(f"❌ [ADMIN] Failed to get current price for {platform} {transfer_type}")
            await query.edit_message_text(
                AdminMessages.get_error_message("database_error"),
                parse_mode="HTML"
            )
            return
        
        print(f"💰 [ADMIN] Current price for {platform} {transfer_type}: {current_price}")
        
        # حفظ بيانات الجلسة
        self.user_sessions[user_id] = {
            'step': 'waiting_price',
            'platform': platform,
            'transfer_type': transfer_type,
            'current_price': current_price
        }
        
        print(f"📝 [ADMIN] Session created for admin {user_id}: waiting for price input")
        
        AdminOperations.log_admin_action(user_id, "STARTED_PRICE_EDIT", 
                                       f"Platform: {platform}, Type: {transfer_type}, Current: {current_price}")
        
        message = AdminMessages.get_price_edit_prompt(platform, transfer_type, current_price)
        keyboard = AdminKeyboards.get_price_edit_keyboard(platform, transfer_type)
        
        try:
            await query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            print(f"✅ [ADMIN] Price edit prompt sent to admin {user_id}")
        except Exception as e:
            print(f"❌ [ADMIN] Failed to send price edit prompt: {e}")
    
    async def handle_admin_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج عرض سجل الأعمال"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        
        print(f"\n📊 [ADMIN] Logs callback received from user {user_id} (@{username})")
        print(f"📞 [ADMIN] Callback data: {query.data}")
        
        await query.answer()
        print(f"✅ [ADMIN] Callback answered for user {user_id}")
        
        if not self.is_admin(user_id):
            return
        
        logs = AdminOperations.get_admin_logs(50)
        message = AdminMessages.get_admin_logs_message(logs)
        keyboard = AdminKeyboards.get_admin_logs_keyboard()
        
        await query.edit_message_text(
            message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الإحصائيات (للتطوير المستقبلي)"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        
        print(f"\n📈 [ADMIN] Stats callback received from user {user_id} (@{username})")
        print(f"📞 [ADMIN] Callback data: {query.data}")
        
        await query.answer()
        print(f"✅ [ADMIN] Callback answered for user {user_id}")
        
        if not self.is_admin(user_id):
            return
        
        # رسالة مؤقتة - يمكن تطويرها لاحقاً
        await query.edit_message_text(
            "📊 <b>الإحصائيات</b>\n\n🚧 هذه الميزة قيد التطوير...\n\nستكون متاحة قريباً!",
            reply_markup=AdminKeyboards.get_main_admin_keyboard(),
            parse_mode="HTML"
        )
    
    async def handle_unknown_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الـ callbacks غير المعروفة للتصحيح"""
        query = update.callback_query
        user_id = query.from_user.id
        username = query.from_user.username or "Unknown"
        
        print(f"\n❓ [ADMIN] UNKNOWN callback received from user {user_id} (@{username})")
        print(f"🔍 [ADMIN] Callback data: '{query.data}'")
        print(f"⚠️ [ADMIN] This callback was not handled by any specific pattern!")
        
        await query.answer()
        
        # إذا كان admin، أرسل رسالة توضيحية
        if self.is_admin(user_id):
            print(f"🛠️ [ADMIN] Sending debug message to admin about unknown callback")
            await query.edit_message_text(
                f"🐛 <b>Debug Info</b>\n\n"
                f"❓ Unknown callback received: <code>{query.data}</code>\n\n"
                f"This helps debug admin system issues!",
                reply_markup=AdminKeyboards.get_main_admin_keyboard(),
                parse_mode="HTML"
            )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MESSAGE HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def handle_price_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج إدخال السعر الجديد"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        print(f"\n💰 [ADMIN] ========== PRICE INPUT HANDLER CALLED ==========")
        print(f"💰 [ADMIN] Price input received from user {user_id} (@{username})")
        
        # التحقق من صلاحية الادمن أولاً
        if not self.is_admin(user_id):
            print(f"❌ [ADMIN] Non-admin user {user_id} trying to update price")
            return
        
        print(f"✅ [ADMIN] User {user_id} is admin - continuing")
        
        # التحقق من وجود جلسة تعديل سعر
        if user_id not in self.user_sessions:
            print(f"⚠️ [ADMIN] No active session found for admin {user_id}")
            print(f"📊 [ADMIN] Current sessions: {list(self.user_sessions.keys())}")
            return
        
        print(f"✅ [ADMIN] Session found for admin {user_id}")
        session = self.user_sessions[user_id]
        print(f"📋 [ADMIN] Session data: {session}")
        
        if session.get('step') != 'waiting_price':
            print(f"⚠️ [ADMIN] Admin {user_id} not in price waiting step: {session.get('step', 'unknown')}")
            return
        
        print(f"✅ [ADMIN] Admin {user_id} is in correct step: waiting_price")
        
        price_text = update.message.text.strip()
        print(f"📝 [ADMIN] Admin {user_id} entered price: '{price_text}'")
        
        # التحقق من صحة السعر
        is_valid, new_price, error_message = PriceManagement.validate_price_input(price_text)
        
        if not is_valid:
            print(f"❌ [ADMIN] Invalid price input from admin {user_id}: {error_message}")
            await update.message.reply_text(
                f"❌ {error_message}\n\nيرجى المحاولة مرة أخرى:",
                parse_mode="HTML"
            )
            return
        
        # بيانات التحديث
        platform = session['platform']
        transfer_type = session['transfer_type']
        old_price = session['current_price']
        
        print(f"🔄 [ADMIN] Updating price: {platform} {transfer_type} from {old_price} to {new_price}")
        
        # تحديث السعر في قاعدة البيانات - THREAD-SAFE ASYNC VERSION
        success = await PriceManagement.update_price(platform, transfer_type, new_price, user_id)
        
        if not success:
            print(f"❌ [ADMIN] Failed to update price in database")
            await update.message.reply_text(
                AdminMessages.get_error_message("database_error"),
                parse_mode="HTML"
            )
            return
        
        print(f"✅ [ADMIN] Price successfully updated in database")
        
        # رسالة النجاح
        success_message = AdminMessages.get_price_update_success(platform, transfer_type, old_price, new_price)
        keyboard = AdminKeyboards.get_price_update_success_keyboard()
        
        try:
            await update.message.reply_text(
                success_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            print(f"✅ [ADMIN] Success message sent to admin {user_id}")
        except Exception as e:
            print(f"❌ [ADMIN] Failed to send success message: {e}")
        
        # مسح الجلسة
        del self.user_sessions[user_id]
        print(f"🧹 [ADMIN] Session cleared for admin {user_id}")
        
        logger.info(f"✅ Price updated by admin {user_id}: {platform} {transfer_type} {old_price} -> {new_price}")
        print(f"💾 [ADMIN] Price update logged: {platform} {transfer_type} {old_price} -> {new_price}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _show_current_prices(self, update: Update, user_id: int):
        """عرض الأسعار الحالية (للأوامر)"""
        prices = PriceManagement.get_all_current_prices()
        message = AdminMessages.get_current_prices_message(prices)
        keyboard = AdminKeyboards.get_view_prices_keyboard()
        
        AdminOperations.log_admin_action(user_id, "VIEWED_PRICES")
        
        await update.message.reply_text(
            message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def _show_current_prices_callback(self, query, user_id: int):
        """عرض الأسعار الحالية (للأزرار)"""
        print(f"📋 [ADMIN] Fetching current prices for admin {user_id}")
        
        try:
            prices = PriceManagement.get_all_current_prices()
            print(f"💰 [ADMIN] Retrieved {len(prices)} price entries from database")
            
            message = AdminMessages.get_current_prices_message(prices)
            keyboard = AdminKeyboards.get_view_prices_keyboard()
            
            AdminOperations.log_admin_action(user_id, "VIEWED_PRICES")
            
            await query.edit_message_text(
                message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            print(f"✅ [ADMIN] Prices successfully displayed to admin {user_id}")
            
        except Exception as e:
            print(f"❌ [ADMIN] Error displaying prices to admin {user_id}: {e}")
            await query.edit_message_text(
                "❌ حدث خطأ في عرض الأسعار. يرجى المحاولة مرة أخرى.",
                parse_mode="HTML"
            )
