# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              ❌ FC26 ERROR MESSAGES - رسائل الأخطاء                     ║
# ║                         Error Messages                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from typing import Dict, Optional

class ErrorMessages:
    """Error and warning messages for the bot"""
    
    @staticmethod
    def get_general_error() -> str:
        """General error message"""
        return "❌ حدث خطأ، حاول مرة أخرى"
    
    @staticmethod
    def get_database_error() -> str:
        """Database error message"""
        return "❌ خطأ في قاعدة البيانات، حاول مرة أخرى"
    
    @staticmethod
    def get_validation_error(details: str = None) -> str:
        """Validation error with optional details"""
        base_message = "❌ البيانات المدخلة غير صحيحة"
        if details:
            return f"{base_message}\n\n📋 <b>التفاصيل:</b> {details}"
        return base_message
    
    @staticmethod
    def get_invalid_platform_error() -> str:
        """Invalid platform error"""
        return "❌ منصة غير صحيحة"
    
    @staticmethod
    def get_invalid_payment_error() -> str:
        """Invalid payment method error"""
        return "❌ طريقة دفع غير صحيحة"
    
    @staticmethod
    def get_start_required_error() -> str:
        """Start command required error"""
        return "🚀 اكتب /start للبدء!"
    
    @staticmethod
    def get_restart_required_error() -> str:
        """Restart required error"""
        return "🚀 اكتب /start للبدء من جديد!"
    
    @staticmethod
    def get_phone_validation_error(error_details: str = None) -> str:
        """Phone number validation error with tips"""
        base_error = error_details or "❌ رقم الهاتف غير صحيح"
        
        return f"""{base_error}

💡 <b>نصائح:</b>
• تأكد من البدء بـ 010, 011, 012, أو 015
• أدخل 11 رقماً بالضبط
• لا تضع كود الدولة (+20)

🔹 <b>أمثلة صحيحة:</b>
• 01012345678
• 01112345678
• 01212345678
• 01512345678"""
    
    @staticmethod
    def get_payment_validation_error(payment_method: str, error_details: str = None) -> str:
        """Payment validation error with method-specific tips"""
        base_error = error_details or "❌ بيانات الدفع غير صحيحة"
        
        tips = {
            'vodafone_cash': "💡 <b>فودافون كاش:</b> رقم 11 خانة يبدأ بـ 010",
            'etisalat_cash': "💡 <b>اتصالات كاش:</b> رقم 11 خانة يبدأ بـ 011", 
            'orange_cash': "💡 <b>أورانج كاش:</b> رقم 11 خانة يبدأ بـ 012",
            'we_cash': "💡 <b>وي كاش:</b> رقم 11 خانة يبدأ بـ 015",
            'bank_wallet': "💡 <b>محفظة بنكية:</b> رقم 11 خانة لأي شبكة",
            'telda': "💡 <b>تيلدا:</b> 16 رقماً بدون مسافات أو شرطات\n<b>مثال:</b> 1234567890123456",
            'instapay': "💡 <b>إنستاباي:</b> رابط كامل\n<b>مثال:</b> https://instapay.com.eg/abc123"
        }
        
        tip = tips.get(payment_method, "💡 تحقق من صحة البيانات المدخلة")
        
        return f"""{base_error}

{tip}"""
    
    @staticmethod
    def get_url_validation_error(error_details: str = None) -> str:
        """URL validation error for InstaPay"""
        base_error = error_details or "❌ رابط إنستاباي غير صحيح"
        
        return f"""{base_error}

💡 <b>نصائح لرابط إنستاباي:</b>
• يجب أن يحتوي على instapay.com.eg أو ipn.eg
• انسخ الرابط كاملاً من التطبيق
• تأكد من صحة الرابط

🔹 <b>مثال صحيح:</b>
https://instapay.com.eg/abc123"""
    
    @staticmethod
    def get_rate_limit_error() -> str:
        """Rate limiting error"""
        return """⏳ <b>تم تجاوز الحد المسموح</b>

🔹 <b>الرجاء الانتظار قليلاً ثم المحاولة مرة أخرى</b>
🔹 <b>هذا للحماية من الاستخدام المفرط</b>

⏰ <b>حاول مرة أخرى خلال دقيقة</b>"""
    
    @staticmethod
    def get_maintenance_error() -> str:
        """Maintenance mode error"""
        return """🔧 <b>البوت تحت الصيانة</b>

⏳ <b>نعتذر للإزعاج، نحن نعمل على تحسين الخدمة</b>

🔄 <b>سيعود البوت للعمل قريباً</b>
📞 <b>للضرورة القصوى، تواصل مع الدعم الفني</b>"""
    
    @staticmethod
    def get_user_not_found_error() -> str:
        """User not found error"""
        return """❌ <b>لم يتم العثور على بياناتك</b>

🚀 <b>اكتب /start لبدء التسجيل من جديد</b>"""
    
    @staticmethod
    def get_session_expired_error() -> str:
        """Session expired error"""
        return """⏰ <b>انتهت صلاحية الجلسة</b>

🔄 <b>الرجاء بدء التسجيل من جديد</b>
🚀 <b>اكتب /start للمتابعة</b>"""
    
    @staticmethod
    def get_security_error() -> str:
        """Security violation error"""
        return """🛡️ <b>تم اكتشاف نشاط مشبوه</b>

⚠️ <b>تم حظر العملية لأسباب أمنية</b>
📞 <b>تواصل مع الدعم الفني إذا كان هذا خطأ</b>"""
    
    @staticmethod
    def get_network_error() -> str:
        """Network/connection error"""
        return """🌐 <b>مشكلة في الاتصال</b>

🔄 <b>الرجاء المحاولة مرة أخرى</b>
📡 <b>تأكد من جودة الاتصال بالإنترنت</b>"""
    
    @staticmethod
    def get_file_error() -> str:
        """File operation error"""
        return """📁 <b>خطأ في العملية</b>

❌ <b>لم يتم حفظ البيانات بنجاح</b>
🔄 <b>الرجاء المحاولة مرة أخرى</b>"""
    
    @staticmethod
    def format_error_with_code(error_code: str, message: str) -> str:
        """Format error message with error code"""
        return f"""❌ <b>خطأ #{error_code}</b>

{message}

🔍 <b>كود الخطأ:</b> {error_code}
📞 <b>اذكر هذا الكود عند التواصل مع الدعم</b>"""
    
    @staticmethod
    def get_custom_error(title: str, message: str, suggestions: list = None) -> str:
        """Create custom error message"""
        error_msg = f"""❌ <b>{title}</b>

{message}"""
        
        if suggestions:
            error_msg += "\n\n💡 <b>اقتراحات:</b>"
            for suggestion in suggestions:
                error_msg += f"\n• {suggestion}"
        
        return error_msg