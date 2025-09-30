# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🎮 FC26 PLATFORM KEYBOARDS - لوحات مفاتيح المنصات          ║
# ║                       Platform Keyboards                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict
from config import GAMING_PLATFORMS

class PlatformKeyboard:
    """Gaming platform selection keyboards"""
    
    @staticmethod
    def create_platform_selection_keyboard() -> InlineKeyboardMarkup:
        """Create platform selection keyboard"""
        keyboard = []
        
        for platform_key, platform_info in GAMING_PLATFORMS.items():
            keyboard.append([
                InlineKeyboardButton(
                    platform_info["name"],
                    callback_data=f"platform_{platform_key}"
                )
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_platform_confirmation_keyboard(platform_key: str) -> InlineKeyboardMarkup:
        """Create platform confirmation keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد", callback_data=f"confirm_platform_{platform_key}"),
                InlineKeyboardButton("🔄 تغيير", callback_data="change_platform")
            ],
            [
                InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_platform_info_keyboard(platform_key: str) -> InlineKeyboardMarkup:
        """Create keyboard with platform information options"""
        keyboard = [
            [
                InlineKeyboardButton("ℹ️ معلومات المنصة", callback_data=f"platform_info_{platform_key}")
            ],
            [
                InlineKeyboardButton("✅ اختيار هذه المنصة", callback_data=f"platform_{platform_key}"),
                InlineKeyboardButton("🔙 العودة", callback_data="platform_selection")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_navigation_keyboard() -> InlineKeyboardMarkup:
        """Create navigation keyboard for platform selection"""
        keyboard = [
            [
                InlineKeyboardButton("🔄 إعادة التحديد", callback_data="platform_selection")
            ],
            [
                InlineKeyboardButton("❓ مساعدة", callback_data="platform_help"),
                InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_platform_emoji(platform_key: str) -> str:
        """Get emoji for platform"""
        return GAMING_PLATFORMS.get(platform_key, {}).get("emoji", "🎮")
    
    @staticmethod
    def get_platform_name(platform_key: str) -> str:
        """Get display name for platform"""
        return GAMING_PLATFORMS.get(platform_key, {}).get("name", "منصة غير معروفة")