# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              📊 FC26 SUMMARY MESSAGES - رسائل الملخصات                 ║
# ║                        Summary Messages                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from typing import Dict, List, Any
from datetime import datetime

class SummaryMessages:
    """Summary and informational messages"""
    
    @staticmethod
    def create_user_profile_summary(user_data: Dict, formatted_data: Dict = None) -> str:
        """Create complete user profile summary"""
        
        formatted = formatted_data or {}
        
        # Process platform display
        platform = user_data.get('platform', 'غير محدد')
        platform_display = SummaryMessages._get_platform_display_name(platform)
        
        # Process payment display
        payment_method = user_data.get('payment_method', 'غير محدد')
        payment_display = SummaryMessages._get_payment_display_name(payment_method)
        
        # Process payment details display
        payment_details = user_data.get('payment_details', 'غير محدد')
        payment_details_display = formatted.get('payment_display', payment_details)
        
        return f"""👤 <b>ملفك الشخصي - FC26</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>📋 البيانات الأساسية</b>

🎮 <b>المنصة:</b> {platform_display}
📱 <b>رقم الواتساب:</b> {formatted.get('whatsapp_display', user_data.get('whatsapp', 'غير محدد'))}
💳 <b>طريقة الدفع:</b> {payment_display}
💰 <b>بيانات الدفع:</b> {payment_details_display}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>📊 معلومات الحساب</b>

✅ <b>حالة التسجيل:</b> مكتمل
📅 <b>تاريخ التسجيل:</b> {user_data.get('created_at', 'غير محدد')}
🔄 <b>آخر تحديث:</b> {user_data.get('updated_at', 'غير محدد')}
🆔 <b>معرف المستخدم:</b> {user_data.get('telegram_id', 'غير محدد')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 <b>مرحباً بك في مجتمع FC26!</b>"""
    
    @staticmethod
    def _get_platform_display_name(platform: str) -> str:
        """Convert platform code to display name"""
        platform_names = {
            'platform_ps': '🎮 PlayStation (PS4/PS5)',
            'platform_xbox': '🎮 Xbox (One/Series X|S)', 
            'platform_pc': '🖥️ PC (Origin/Steam/Epic)',
            'PlayStation': '🎮 PlayStation (PS4/PS5)',
            'Xbox': '🎮 Xbox (One/Series X|S)', 
            'PC': '🖥️ PC (Origin/Steam/Epic)'
        }
        return platform_names.get(platform, platform if platform else 'غير محدد')
    
    @staticmethod
    def _get_payment_display_name(payment_method: str) -> str:
        """Convert payment method code to display name"""
        payment_names = {
            'payment_vodafone': '📱 فودافون كاش (010)',
            'payment_etisalat': '📱 اتصالات كاش (011)',
            'payment_orange': '📱 أورانج كاش (012)',
            'payment_we': '📱 وي كاش (015)',
            'payment_bank': '🏦 محفظة بنكية',
            'payment_tilda': '💳 كارت تيلدا',
            'payment_instapay': '💰 إنستاباي',
            'فودافون كاش': '📱 فودافون كاش (010)',
            'اتصالات كاش': '📱 اتصالات كاش (011)',
            'أورانج كاش': '📱 أورانج كاش (012)',
            'وي كاش': '📱 وي كاش (015)',
            'محفظة بنكية': '🏦 محفظة بنكية',
            'كارت تيلدا': '💳 كارت تيلدا',
            'إنستاباي': '💰 إنستاباي'
        }
        return payment_names.get(payment_method, payment_method if payment_method else 'غير محدد')
    
    @staticmethod
    def create_registration_progress_summary(step: str, completed_steps: List[str]) -> str:
        """Create registration progress summary"""
        
        all_steps = [
            ('choosing_platform', '1️⃣ اختيار المنصة'),
            ('entering_whatsapp', '2️⃣ تأكيد رقم الواتساب'),
            ('choosing_payment', '3️⃣ اختيار طريقة الدفع'),
            ('entering_payment_details', '4️⃣ إدخال تفاصيل الدفع'),
            ('completed', '5️⃣ إتمام التسجيل')
        ]
        
        progress_text = "📊 <b>تقدم التسجيل</b>\n\n"
        
        for step_key, step_name in all_steps:
            if step_key in completed_steps:
                progress_text += f"✅ {step_name}\n"
            elif step_key == step:
                progress_text += f"🔄 {step_name} ← <b>جاري الآن</b>\n"
            else:
                progress_text += f"⏳ {step_name}\n"
        
        # Calculate percentage
        total_steps = len(all_steps)
        completed_count = len(completed_steps)
        percentage = int((completed_count / total_steps) * 100)
        
        progress_text += f"\n📈 <b>نسبة الإنجاز:</b> {percentage}%"
        
        return progress_text
    
    @staticmethod
    def create_statistics_summary(stats: Dict) -> str:
        """Create bot statistics summary"""
        return f"""📊 <b>إحصائيات FC26 Bot</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>👥 المستخدمون</b>

👤 <b>إجمالي المستخدمين:</b> {stats.get('total_users', 0):,}
✅ <b>المسجلين بالكامل:</b> {stats.get('completed_registrations', 0):,}
🔄 <b>قيد التسجيل:</b> {stats.get('pending_registrations', 0):,}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>🎮 المنصات الأكثر شعبية</b>

🥇 <b>الأول:</b> {stats.get('top_platform', 'PlayStation')}
🥈 <b>الثاني:</b> {stats.get('second_platform', 'Xbox')}
🥉 <b>الثالث:</b> {stats.get('third_platform', 'PC')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>💳 طرق الدفع المفضلة</b>

🥇 <b>الأكثر استخداماً:</b> {stats.get('top_payment', 'فودافون كاش')}
📈 <b>النمو السريع:</b> {stats.get('trending_payment', 'إنستاباي')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ <b>آخر تحديث:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    
    @staticmethod
    def create_daily_report(date: str, metrics: Dict) -> str:
        """Create daily activity report"""
        return f"""📅 <b>تقرير يومي - {date}</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>📊 النشاط اليومي</b>

🆕 <b>تسجيلات جديدة:</b> {metrics.get('new_registrations', 0)}
✅ <b>تسجيلات مكتملة:</b> {metrics.get('completed_today', 0)}
📱 <b>رسائل مرسلة:</b> {metrics.get('messages_sent', 0)}
❌ <b>أخطاء:</b> {metrics.get('errors_count', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>🎯 معدل النجاح</b>

📈 <b>معدل إكمال التسجيل:</b> {metrics.get('completion_rate', 0):.1f}%
⚡ <b>متوسط وقت التسجيل:</b> {metrics.get('avg_registration_time', 'غير محدد')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>🔝 الذروات</b>

⏰ <b>أكثر الأوقات نشاطاً:</b> {metrics.get('peak_hour', 'غير محدد')}
🎮 <b>منصة اليوم:</b> {metrics.get('platform_of_day', 'غير محدد')}"""
    
    @staticmethod
    def create_help_summary() -> str:
        """Create comprehensive help summary"""
        return """📚 <b>دليل استخدام FC26 Bot</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>🚀 البدء</b>

/start - بدء أو متابعة التسجيل
/help - عرض هذه المساعدة
/profile - عرض الملف الشخصي

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>🎮 المنصات المدعومة</b>

• PlayStation (PS4/PS5)
• Xbox (One/Series X|S)  
• PC (Origin/Steam/Epic)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>💳 طرق الدفع</b>

• فودافون كاش (010)
• اتصالات كاش (011)
• أورانج كاش (012)
• وي كاش (015)
• محفظة بنكية
• كارت تيلدا
• إنستاباي

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>📱 قواعد الأرقام</b>

✅ يبدأ بـ: 010, 011, 012, 015
✅ طول: 11 رقماً بالضبط
❌ لا تضع: +20 أو مسافات

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>🔗 روابط إنستاباي</b>

✅ يجب أن يحتوي على: instapay.com.eg
✅ مثال: https://instapay.com.eg/abc123

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>📞 الدعم الفني</b>

إذا واجهت أي مشكلة، تواصل مع فريق الدعم وستحصل على المساعدة فوراً."""
    
    @staticmethod
    def create_feature_list() -> str:
        """Create bot features list"""
        return """⭐ <b>مميزات FC26 Bot</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>🔥 المميزات الرئيسية</b>

✨ <b>تسجيل سريع وسهل</b> - 4 خطوات بسيطة
🛡️ <b>أمان عالي</b> - حماية شاملة للبيانات
📱 <b>دعم جميع الشبكات</b> - كل طرق الدفع المصرية
🎮 <b>دعم كل المنصات</b> - PS، Xbox، PC
🔄 <b>متابعة التقدم</b> - إكمال من آخر خطوة
💬 <b>واجهة عربية</b> - بالعربية بالكامل

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>🚀 مميزات متقدمة</b>

📋 <b>نسخ بنقرة</b> - نسخ البيانات بسهولة
🔍 <b>تحقق ذكي</b> - فحص تلقائي للبيانات
⚡ <b>استجابة سريعة</b> - رد فوري على جميع الرسائل
🎯 <b>توجيه ذكي</b> - إرشادات واضحة لكل خطوة
📊 <b>تتبع مفصل</b> - متابعة كاملة للعملية

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 <b>FC26 - الخيار الأول للاعبين المحترفين</b>"""