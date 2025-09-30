# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🎉 FC26 CONFIRMATION MESSAGES - رسائل التأكيد              ║
# ║                      Confirmation Messages                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from typing import Any, Dict
from config import GAMING_PLATFORMS  # إضافة هذا الimport


class ConfirmationMessages:
    """Payment confirmation and success messages"""

    @staticmethod
    def create_payment_confirmation(
        payment_method: str, validation: Dict, payment_name: str
    ) -> str:
        """Create beautiful payment confirmation message"""

        # Mobile wallets confirmation
        if payment_method in [
            "vodafone_cash",
            "etisalat_cash",
            "orange_cash",
            "we_cash",
            "bank_wallet",
        ]:
            return f"""✅ تم حفظ {payment_name}!

📱 الرقم: {validation['display']}

━━━━━━━━━━━━━━━━"""

        # Telda card confirmation (بدون تشفير)
        elif payment_method == "telda":
            return f"""✅ تم حفظ كارت تيلدا!

💳 رقم الكارت: {validation['display']}

━━━━━━━━━━━━━━━━"""

        # InstaPay confirmation
        elif payment_method == "instapay":
            return f"""✅ تم حفظ رابط إنستاباي!

🔗 الرابط: {validation['display']}

━━━━━━━━━━━━━━━━"""

        # Fallback for unknown methods
        else:
            return f"""✅ تم حفظ {payment_name}!

💰 التفاصيل: {validation.get('display', 'غير محدد')}

━━━━━━━━━━━━━━━━"""

    @staticmethod
    def create_whatsapp_confirmation(validation: Dict) -> str:
        """Create WhatsApp confirmation message"""
        return f"""✅ تم حفظ رقم الواتساب!

📱 الرقم: {validation['display']}

━━━━━━━━━━━━━━━━"""

    @staticmethod
    def create_final_summary(
        user_data: Dict, payment_name: str, validation: Dict, user_info: Dict
    ) -> str:
        """Create enhanced final registration summary"""

        # الحصول على اسم المنصة من الconfig
        platform_key = user_data.get('platform', '')
        platform_name = GAMING_PLATFORMS.get(platform_key, {}).get('name', 'غير محدد')

        # Format payment details based on method
        if user_data["payment_method"] == "telda":
            # For Telda, show full card number (غير مشفر)
            payment_details_line = f"• رقم الكارت: {validation['display']}"

        elif user_data["payment_method"] == "instapay":
            # For InstaPay, show the clean URL
            payment_details_line = f"• الرابط: {validation['display']}"

        else:
            # For mobile wallets, show the phone number
            payment_details_line = f"• الرقم: {validation['display']}"

        return f"""
✅ تم تحديث بياناتك بنجاح!

📊 ملخص البيانات المحدثة:
━━━━━━━━━━━━━━━━
🎮 المنصة: {platform_name}
📱 واتساب: {user_data['whatsapp']}
💳 طريقة الدفع: {payment_name}
💰 بيانات الدفع:
{payment_details_line}
━━━━━━━━━━━━━━━━

👤 اسم المستخدم: @{user_info.get('username', 'غير متوفر')}
🆔 معرف التليجرام: {user_info['id']}

✨ تم تحديث ملفك الشخصي بنجاح!"""

    @staticmethod
    def create_registration_completed_message(
        user_data: Dict, display_format: Dict
    ) -> str:
        """Create message for already completed registration"""

        # الحصول على اسم المنصة من الconfig
        platform_key = user_data.get('platform', '')
        platform_name = GAMING_PLATFORMS.get(platform_key, {}).get('name', 'غير محدد')

        return f"""✅ <b>تسجيلك مكتمل بالفعل!</b>

📋 <b>ملخص بياناتك:</b>

🎮 <b>المنصة:</b> {platform_name}
📱 <b>الواتساب:</b> {display_format.get('whatsapp_display', user_data.get('whatsapp', 'غير محدد'))}
💳 <b>الدفع:</b> {user_data.get('payment_name', 'غير محدد')}
💰 <b>التفاصيل:</b> {display_format.get('payment_display', 'غير محدد')}

🚀 <b>مرحباً بك في عائلة FC26!</b>"""

    @staticmethod
    def create_data_updated_message() -> str:
        """Create data updated confirmation"""
        return """✅ <b>تم تحديث بياناتك بنجاح!</b>

🔄 <b>ماذا حدث:</b>
• تم حفظ جميع المعلومات
• تم تحديث ملفك الشخصي
• أصبحت جاهزاً لاستخدام الخدمات

🎮 <b>الخطوات التالية:</b>
• يمكنك الآن استخدام جميع خدمات FC26
• تواصل معنا للحصول على المساعدة
• راجع ملفك الشخصي للتأكد من البيانات

🚀 <b>مرحباً بك في FC26!</b>"""

    @staticmethod
    def create_step_completed_message(step_name: str, next_step: str = None) -> str:
        """Create step completion message"""
        base_message = f"✅ <b>تم إكمال: {step_name}</b>\n\n"

        if next_step:
            base_message += f"➡️ <b>الخطوة التالية:</b> {next_step}\n\n"

        base_message += "🎯 <b>أنت تتقدم بشكل ممتاز!</b>"

        return base_message

    @staticmethod
    def create_profile_summary(user_data: Dict, formatted_data: Dict = None) -> str:
        """Create complete profile summary"""

        formatted = formatted_data or {}
        
        # الحصول على اسم المنصة من الconfig
        platform_key = user_data.get('platform', '')
        platform_name = GAMING_PLATFORMS.get(platform_key, {}).get('name', 'غير محدد')

        return f"""👤 <b>ملفك الشخصي في FC26</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>📋 البيانات الأساسية:</b>

🎮 <b>المنصة:</b> {platform_name}
📱 <b>الواتساب:</b> {formatted.get('whatsapp_display', user_data.get('whatsapp', 'غير محدد'))}
💳 <b>طريقة الدفع:</b> {user_data.get('payment_name', 'غير محدد')}
💰 <b>بيانات الدفع:</b> {formatted.get('payment_display', 'غير محدد')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>⏰ معلومات التسجيل:</b>

📅 <b>تاريخ التسجيل:</b> {user_data.get('created_at', 'غير محدد')}
🔄 <b>آخر تحديث:</b> {user_data.get('updated_at', 'غير محدد')}
✅ <b>حالة التسجيل:</b> مكتمل

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 <b>مرحباً بك في عائلة FC26!</b>"""

    @staticmethod
    def create_success_animation() -> str:
        """Create animated success message"""
        return """🎉✨🎉✨🎉✨🎉✨🎉

      🏆 <b>نجح التسجيل!</b> 🏆

      🎮 FC26 Gaming Community 🎮

🎉✨🎉✨🎉✨🎉✨🎉

✅ <b>أهلاً بك في الفريق!</b>"""
