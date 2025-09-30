# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              ⌨️ FC26 COIN SELLING KEYBOARDS - أزرار بيع الكوينز          ║
# ║                       Coin Selling Keyboards                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict
from .sell_pricing import CoinSellPricing, Platform

class SellKeyboards:
    """أزرار ولوحات مفاتيح خدمة بيع الكوينز"""
    
    @staticmethod
    def get_main_sell_keyboard() -> InlineKeyboardMarkup:
        """لوحة المفاتيح الرئيسية لخدمة البيع"""
        keyboard = [
            [InlineKeyboardButton("🎮 PlayStation", callback_data="sell_platform_playstation")],
            [InlineKeyboardButton("🎮 Xbox", callback_data="sell_platform_xbox")],
            [InlineKeyboardButton("🖥️ PC", callback_data="sell_platform_pc")],
            [InlineKeyboardButton("❓ مساعدة", callback_data="sell_help"),
             InlineKeyboardButton("🔙 العودة", callback_data="sell_back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    

    @staticmethod
    def get_price_confirmation_keyboard(platform: str, coins: int, price: int) -> InlineKeyboardMarkup:
        """لوحة تأكيد السعر"""
        keyboard = [
            [InlineKeyboardButton("✅ تأكيد البيع", callback_data=f"sell_confirm_{platform}_{coins}_{price}")],
            [InlineKeyboardButton("📝 إدخال كمية أخرى", callback_data=f"sell_platform_{platform}"),
             InlineKeyboardButton("🎮 تغيير المنصة", callback_data="sell_back_platforms")],
            [InlineKeyboardButton("🚫 إلغاء البيع", callback_data="sell_cancel")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_sale_instructions_keyboard(platform: str, coins: int) -> InlineKeyboardMarkup:
        """لوحة تعليمات البيع"""
        keyboard = [
            [InlineKeyboardButton("✅ فهمت التعليمات، متابعة", callback_data=f"sell_ready_{platform}_{coins}")],
            [InlineKeyboardButton("❓ أحتاج مساعدة", callback_data="sell_help_instructions")],
            [InlineKeyboardButton("🔙 العودة للسعر", callback_data=f"sell_back_price_{platform}_{coins}"),
             InlineKeyboardButton("🚫 إلغاء البيع", callback_data="sell_cancel")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_payment_method_keyboard() -> InlineKeyboardMarkup:
        """لوحة اختيار طريقة الدفع"""
        keyboard = [
            [InlineKeyboardButton("📱 فودافون كاش", callback_data="sell_payment_vodafone")],
            [InlineKeyboardButton("📱 اتصالات كاش", callback_data="sell_payment_etisalat")],
            [InlineKeyboardButton("📱 أورانج كاش", callback_data="sell_payment_orange")], 
            [InlineKeyboardButton("📱 وي كاش", callback_data="sell_payment_we")],
            [InlineKeyboardButton("💰 إنستاباي", callback_data="sell_payment_instapay")],
            [InlineKeyboardButton("🏦 تحويل بنكي", callback_data="sell_payment_bank")],
            [InlineKeyboardButton("🔙 العودة", callback_data="sell_back_instructions")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_sale_progress_keyboard() -> InlineKeyboardMarkup:
        """لوحة متابعة حالة البيع"""
        keyboard = [
            [InlineKeyboardButton("📊 حالة البيع", callback_data="sell_status")],
            [InlineKeyboardButton("📞 تواصل مع الدعم", callback_data="sell_support")],
            [InlineKeyboardButton("🚫 إلغاء البيع", callback_data="sell_cancel_confirm")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_sale_completed_keyboard() -> InlineKeyboardMarkup:
        """لوحة إتمام البيع"""
        keyboard = [
            [InlineKeyboardButton("💰 بيع المزيد من الكوينز", callback_data="sell_more")],
            [InlineKeyboardButton("📊 تقييم الخدمة", callback_data="sell_rate_service")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="sell_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_custom_amount_cancel_keyboard(platform: str) -> InlineKeyboardMarkup:
        """لوحة إلغاء الكمية المخصصة"""
        keyboard = [
            [InlineKeyboardButton("🔙 العودة لاختيار المنصة", callback_data="sell_back_platforms")],
            [InlineKeyboardButton("🎮 تغيير المنصة", callback_data="sell_back_platforms")],
            [InlineKeyboardButton("🚫 إلغاء البيع", callback_data="sell_cancel")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_help_keyboard() -> InlineKeyboardMarkup:
        """لوحة المساعدة"""
        keyboard = [
            [InlineKeyboardButton("📞 الدعم الفني", callback_data="sell_support")],
            [InlineKeyboardButton("💡 أسئلة شائعة", callback_data="sell_faq")],
            [InlineKeyboardButton("🔙 العودة للبيع", callback_data="sell_back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_error_keyboard(error_type: str = "general") -> InlineKeyboardMarkup:
        """لوحة مفاتيح الأخطاء"""
        keyboard = [
            [InlineKeyboardButton("🔄 المحاولة مرة أخرى", callback_data="sell_retry")],
            [InlineKeyboardButton("📞 تواصل مع الدعم", callback_data="sell_support")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="sell_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_sell_keyboard() -> InlineKeyboardMarkup:
        """لوحة إدارة البيع (للأدمن)"""
        keyboard = [
            [InlineKeyboardButton("📊 إحصائيات البيع", callback_data="admin_sell_stats")],
            [InlineKeyboardButton("💰 تحديث الأسعار", callback_data="admin_sell_prices")],
            [InlineKeyboardButton("📋 طلبات البيع النشطة", callback_data="admin_sell_active")],
            [InlineKeyboardButton("🔙 لوحة الإدارة", callback_data="admin_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @classmethod
    def get_quick_sell_keyboard(cls) -> InlineKeyboardMarkup:
        """لوحة البيع السريع للقائمة الرئيسية"""
        keyboard = [
            [InlineKeyboardButton("💰 بيع كوينز FIFA", callback_data="sell_start")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @classmethod 
    def get_platform_comparison_keyboard(cls) -> InlineKeyboardMarkup:
        """لوحة مقارنة أسعار المنصات"""
        keyboard = [
            [InlineKeyboardButton("📊 مقارنة الأسعار", callback_data="sell_compare_prices")],
            [InlineKeyboardButton("🎮 PlayStation", callback_data="sell_platform_playstation"),
             InlineKeyboardButton("🎮 Xbox", callback_data="sell_platform_xbox")],
            [InlineKeyboardButton("🖥️ PC", callback_data="sell_platform_pc")],
            [InlineKeyboardButton("🔙 العودة", callback_data="sell_back_main")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @classmethod
    def build_dynamic_keyboard(cls, buttons_data: List[Dict], rows: int = 2) -> InlineKeyboardMarkup:
        """بناء لوحة مفاتيح ديناميكية"""
        keyboard = []
        current_row = []
        
        for i, button in enumerate(buttons_data):
            current_row.append(InlineKeyboardButton(
                button['text'], 
                callback_data=button['callback_data']
            ))
            
            # إذا وصلنا لآخر عنصر في الصف أو آخر عنصر بشكل عام
            if len(current_row) == rows or i == len(buttons_data) - 1:
                keyboard.append(current_row)
                current_row = []
        
        return InlineKeyboardMarkup(keyboard)