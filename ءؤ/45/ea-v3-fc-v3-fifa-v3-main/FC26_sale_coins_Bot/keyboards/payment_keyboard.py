# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              💳 FC26 PAYMENT KEYBOARDS - لوحات مفاتيح الدفع             ║
# ║                       Payment Keyboards                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict
from config import PAYMENT_METHODS

class PaymentKeyboard:
    """Payment method selection keyboards"""
    
    @staticmethod
    def create_payment_selection_keyboard() -> InlineKeyboardMarkup:
        """Create payment method selection keyboard"""
        keyboard = []
        
        for payment_key, payment_name in PAYMENT_METHODS.items():
            keyboard.append([
                InlineKeyboardButton(
                    payment_name,
                    callback_data=f"payment_{payment_key}"
                )
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_payment_confirmation_keyboard(payment_key: str) -> InlineKeyboardMarkup:
        """Create payment method confirmation keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد الطريقة", callback_data=f"confirm_payment_{payment_key}"),
                InlineKeyboardButton("🔄 تغيير", callback_data="change_payment")
            ],
            [
                InlineKeyboardButton("ℹ️ معلومات الطريقة", callback_data=f"payment_info_{payment_key}")
            ],
            [
                InlineKeyboardButton("🔙 العودة للمنصات", callback_data="back_to_platforms")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_payment_help_keyboard() -> InlineKeyboardMarkup:
        """Create payment help keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📱 أرقام الهاتف", callback_data="phone_help"),
                InlineKeyboardButton("💳 الكروت", callback_data="card_help")
            ],
            [
                InlineKeyboardButton("🔗 إنستاباي", callback_data="instapay_help"),
                InlineKeyboardButton("🏦 المحافظ", callback_data="wallet_help")
            ],
            [
                InlineKeyboardButton("🔙 العودة", callback_data="payment_selection")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_mobile_networks_keyboard() -> InlineKeyboardMarkup:
        """Create mobile networks information keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("⭕️ فودافون (010)", callback_data="network_vodafone"),
                InlineKeyboardButton("🟢 اتصالات (011)", callback_data="network_etisalat")
            ],
            [
                InlineKeyboardButton("🍊 أورانج (012)", callback_data="network_orange"),
                InlineKeyboardButton("🟣 وي (015)", callback_data="network_we")
            ],
            [
                InlineKeyboardButton("🔙 العودة", callback_data="payment_help")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_payment_examples_keyboard(payment_key: str) -> InlineKeyboardMarkup:
        """Create keyboard with payment examples"""
        keyboard = [
            [
                InlineKeyboardButton("📝 أمثلة", callback_data=f"examples_{payment_key}"),
                InlineKeyboardButton("⚠️ أخطاء شائعة", callback_data=f"common_errors_{payment_key}")
            ],
            [
                InlineKeyboardButton("✅ فهمت، أدخل البيانات", callback_data=f"understood_{payment_key}"),
            ],
            [
                InlineKeyboardButton("🔙 تغيير الطريقة", callback_data="payment_selection")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_validation_retry_keyboard(payment_key: str) -> InlineKeyboardMarkup:
        """Create keyboard for validation retry options"""
        keyboard = [
            [
                InlineKeyboardButton("🔄 إعادة المحاولة", callback_data=f"retry_{payment_key}"),
                InlineKeyboardButton("❓ مساعدة", callback_data=f"help_{payment_key}")
            ],
            [
                InlineKeyboardButton("🔄 تغيير طريقة الدفع", callback_data="payment_selection")
            ],
            [
                InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_skip_optional_keyboard(step: str) -> InlineKeyboardMarkup:
        """Create keyboard to skip optional steps"""
        keyboard = [
            [
                InlineKeyboardButton("⏭️ تخطي هذه الخطوة", callback_data=f"skip_{step}"),
                InlineKeyboardButton("✅ متابعة", callback_data=f"continue_{step}")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_payment_emoji(payment_key: str) -> str:
        """Get emoji for payment method"""
        emojis = {
            'vodafone_cash': '⭕️',
            'etisalat_cash': '🟢',
            'orange_cash': '🍊',
            'we_cash': '🟣',
            'bank_wallet': '🏦',
            'telda': '💳',
            'instapay': '🔗'
        }
        return emojis.get(payment_key, '💰')
    
    @staticmethod
    def get_payment_display_name(payment_key: str) -> str:
        """Get display name for payment method"""
        return PAYMENT_METHODS.get(payment_key, "طريقة غير معروفة")
    
    @staticmethod
    def create_final_confirmation_keyboard() -> InlineKeyboardMarkup:
        """Create final confirmation keyboard after all data is entered"""
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد جميع البيانات", callback_data="final_confirm"),
                InlineKeyboardButton("✏️ تعديل البيانات", callback_data="edit_data")
            ],
            [
                InlineKeyboardButton("🔄 بدء من جديد", callback_data="restart_registration")
            ]
        ]
        
        return InlineKeyboardMarkup(keyboard)