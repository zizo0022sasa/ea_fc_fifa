# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              👑 FC26 ADMIN KEYBOARDS - أزرار الادارة                     ║
# ║                     Admin Keyboards Handler                             ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List

class AdminKeyboards:
    """أزرار لوحة الادارة"""
    
    @staticmethod
    def get_main_admin_keyboard() -> InlineKeyboardMarkup:
        """لوحة المفاتيح الرئيسية للإدارة"""
        keyboard = [
            [InlineKeyboardButton("💰 إدارة الأسعار", callback_data="admin_prices")],
            [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
            [InlineKeyboardButton("📝 سجل الأعمال", callback_data="admin_logs")],
            [InlineKeyboardButton("⚙️ إعدادات النظام", callback_data="admin_settings")],
            [InlineKeyboardButton("🔄 تحديث البوت", callback_data="admin_refresh")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_price_management_keyboard() -> InlineKeyboardMarkup:
        """لوحة إدارة الأسعار"""
        keyboard = [
            [InlineKeyboardButton("📋 عرض الأسعار الحالية", callback_data="admin_view_prices")],
            [InlineKeyboardButton("✏️ تعديل أسعار PlayStation", callback_data="admin_edit_playstation")],
            [InlineKeyboardButton("✏️ تعديل أسعار Xbox", callback_data="admin_edit_xbox")],
            [InlineKeyboardButton("✏️ تعديل أسعار PC", callback_data="admin_edit_pc")],
            [InlineKeyboardButton("📊 مقارنة الأسعار", callback_data="admin_compare_prices")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="admin_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_platform_edit_keyboard(platform: str) -> InlineKeyboardMarkup:
        """لوحة تعديل أسعار منصة معينة"""
        keyboard = [
            [InlineKeyboardButton("📅 تعديل التحويل العادي", callback_data=f"admin_edit_{platform}_normal")],
            [InlineKeyboardButton("⚡️ تعديل التحويل الفوري", callback_data=f"admin_edit_{platform}_instant")],
            [InlineKeyboardButton("👁️ عرض الأسعار الحالية", callback_data="admin_view_prices")],
            [InlineKeyboardButton("🔙 العودة لإدارة الأسعار", callback_data="admin_prices")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_price_edit_keyboard(platform: str, transfer_type: str) -> InlineKeyboardMarkup:
        """لوحة تعديل سعر معين"""
        keyboard = [
            [InlineKeyboardButton("❌ إلغاء التعديل", callback_data=f"admin_edit_{platform}")],
            [InlineKeyboardButton("🔙 العودة", callback_data="admin_prices")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_price_update_success_keyboard() -> InlineKeyboardMarkup:
        """لوحة بعد نجاح التحديث"""
        keyboard = [
            [InlineKeyboardButton("💰 تعديل سعر آخر", callback_data="admin_prices")],
            [InlineKeyboardButton("📋 عرض جميع الأسعار", callback_data="admin_view_prices")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="admin_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_view_prices_keyboard() -> InlineKeyboardMarkup:
        """لوحة عرض الأسعار"""
        keyboard = [
            [InlineKeyboardButton("✏️ تعديل الأسعار", callback_data="admin_prices")],
            [InlineKeyboardButton("🔄 تحديث العرض", callback_data="admin_view_prices")],
            [InlineKeyboardButton("📊 مقارنة المنصات", callback_data="admin_compare_prices")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="admin_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_logs_keyboard() -> InlineKeyboardMarkup:
        """لوحة سجل الأعمال"""
        keyboard = [
            [InlineKeyboardButton("🔄 تحديث السجل", callback_data="admin_logs")],
            [InlineKeyboardButton("🗑️ مسح السجل القديم", callback_data="admin_clear_logs")],
            [InlineKeyboardButton("📊 إحصائيات السجل", callback_data="admin_log_stats")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="admin_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_stats_keyboard() -> InlineKeyboardMarkup:
        """لوحة الإحصائيات"""
        keyboard = [
            [InlineKeyboardButton("👥 إحصائيات المستخدمين", callback_data="admin_user_stats")],
            [InlineKeyboardButton("💰 إحصائيات المبيعات", callback_data="admin_sales_stats")],
            [InlineKeyboardButton("📈 تقرير يومي", callback_data="admin_daily_report")],
            [InlineKeyboardButton("📊 تقرير شهري", callback_data="admin_monthly_report")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="admin_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_unauthorized_keyboard() -> InlineKeyboardMarkup:
        """لوحة عدم وجود صلاحية"""
        keyboard = [
            [InlineKeyboardButton("🏠 العودة للقائمة الرئيسية", callback_data="main_menu")],
            [InlineKeyboardButton("📞 التواصل مع الدعم", callback_data="contact_support")]
        ]
        return InlineKeyboardMarkup(keyboard)