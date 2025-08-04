from flask import Flask, render_template, request, jsonify, abort
import json, os, secrets, time, re, hashlib
from datetime import datetime, timedelta
import logging
from functools import wraps
from collections import defaultdict
import urllib.parse

# إعداد التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# إعداد الـ Logging للأمان
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# متغيرات الحماية العامة
blocked_ips = {}
request_counts = defaultdict(list)
failed_attempts = {}

# إعدادات الواتساب
WHATSAPP_NUMBER = "+201094591331"
BUSINESS_NAME = "شهد السنيورة"

# دالة تنسيق الأرقام بالفاصلة العشرية
def format_number(number):
    """تنسيق الأرقام بالفاصلة العشرية"""
    return f"{int(number):,}"

# Rate Limiting محسن بدون CSRF
def rate_limit(max_requests=10, window=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            current_time = time.time()
            
            # فحص IP محظور
            if client_ip in blocked_ips:
                block_time, duration = blocked_ips[client_ip]
                if current_time - block_time < duration:
                    logger.warning(f"🚨 IP محظور: {client_ip}")
                    abort(429)
                else:
                    del blocked_ips[client_ip]
            
            # تنظيف الطلبات القديمة
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if current_time - req_time < window
            ]
            
            # فحص عدد الطلبات
            if len(request_counts[client_ip]) >= max_requests:
                # حظر مؤقت
                blocked_ips[client_ip] = (current_time, 300)  # 5 دقائق
                logger.warning(f"🚨 Rate limit exceeded - IP blocked: {client_ip}")
                abort(429)
            
            # إضافة الطلب الحالي
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# حماية إضافية من Spam
def anti_spam_check(ip_address, user_agent):
    """فحص إضافي ضد الـ spam والـ bots"""
    current_time = time.time()
    
    # فحص User Agent
    suspicious_agents = ['bot', 'crawler', 'spider', 'scraper']
    if any(agent in user_agent.lower() for agent in suspicious_agents):
        logger.warning(f"🚨 Suspicious user agent from IP: {ip_address}")
        return False
    
    # فحص التكرار السريع
    key = f"{ip_address}_{user_agent}"
    if key not in failed_attempts:
        failed_attempts[key] = []
    
    # تنظيف المحاولات القديمة
    failed_attempts[key] = [
        t for t in failed_attempts[key] 
        if current_time - t < 60  # آخر دقيقة
    ]
    
    # إذا أكتر من 3 محاولات في دقيقة واحدة
    if len(failed_attempts[key]) >= 3:
        blocked_ips[ip_address] = (current_time, 900)  # حظر 15 دقيقة
        logger.warning(f"🚨 Anti-spam triggered - IP blocked: {ip_address}")
        return False
    
    failed_attempts[key].append(current_time)
    return True

# 🔥 دالة جديدة لإدارة العروض - مع الأسعار الوهمية
def get_offers():
    """
    🔥 مركز التحكم الذكي - أسعار وهمية + أسعار حقيقية!
    =========================================================
    
    📝 النظام الجديد:
    - FAKE_PRICE = السعر الوهمي (اللي هيتشطب)
    - REAL_PRICE = السعر الحقيقي (اللي العميل هيدفعه)
    - الخصم هيتحسب تلقائي = ((FAKE - REAL) / FAKE) * 100
    
    🎯 مثال:
    FAKE_PRICE = 5000  (السعر الوهمي)
    REAL_PRICE = 3200  (السعر الحقيقي) 
    النتيجة = خصم 36% تلقائي!
    
    💡 استراتيجية التسعير:
    1. حط السعر الحقيقي اللي عايزه
    2. حط السعر الوهمي أعلى منه
    3. الخصم هيظهر تلقائي وجذاب!
    """
    
    # 🎮 تحكم عام في العروض
    # ======================
    ALL_OFFERS_ACTIVE = "yas"  # yas = كل العروض شغالة | no = كل العروض مقفولة
    
    # 🇸🇦 ================ ARABIC STANDARD EDITION ================
    
    # Arabic Standard - PS5 - Full
    AR_STD_PS5_FULL_ACTIVE = "no"      # yas = العرض شغال | no = مقفول
    AR_STD_PS5_FULL_FAKE_PRICE = 5000  # السعر الوهمي (اللي هيتشطب)
    AR_STD_PS5_FULL_REAL_PRICE = 3200  # السعر الحقيقي (اللي العميل هيدفعه)
    
    # Arabic Standard - PS5 - Primary  
    AR_STD_PS5_PRIMARY_ACTIVE = "no"     # yas = العرض شغال | no = مقفول
    AR_STD_PS5_PRIMARY_FAKE_PRICE = 2500 # السعر الوهمي
    AR_STD_PS5_PRIMARY_REAL_PRICE = 1600 # السعر الحقيقي
    
    # Arabic Standard - PS5 - Secondary
    AR_STD_PS5_SECONDARY_ACTIVE = "no"  # yas = العرض شغال | no = مقفول
    AR_STD_PS5_SECONDARY_FAKE_PRICE = 1800 # السعر الوهمي
    AR_STD_PS5_SECONDARY_REAL_PRICE = 900  # السعر الحقيقي
    
    # Arabic Standard - PS4 - Full
    AR_STD_PS4_FULL_ACTIVE = "no"       # yas = العرض شغال | no = مقفول
    AR_STD_PS4_FULL_FAKE_PRICE = 4800   # السعر الوهمي
    AR_STD_PS4_FULL_REAL_PRICE = 3200   # السعر الحقيقي
    
    # Arabic Standard - PS4 - Primary
    AR_STD_PS4_PRIMARY_ACTIVE = "yas"     # yas = العرض شغال | no = مقفول
    AR_STD_PS4_PRIMARY_FAKE_PRICE = 1800 # السعر الوهمي
    AR_STD_PS4_PRIMARY_REAL_PRICE = 800  # السعر الحقيقي
    
    # Arabic Standard - PS4 - Secondary
    AR_STD_PS4_SECONDARY_ACTIVE = "no"  # yas = العرض شغال | no = مقفول
    AR_STD_PS4_SECONDARY_FAKE_PRICE = 1500 # السعر الوهمي
    AR_STD_PS4_SECONDARY_REAL_PRICE = 1000 # السعر الحقيقي
    
    # 🇸🇦 ================ ARABIC ULTIMATE EDITION ================
    
    # Arabic Ultimate - PS5 - Full
    AR_ULT_PS5_FULL_ACTIVE = "no"        # yas = العرض شغال | no = مقفول
    AR_ULT_PS5_FULL_FAKE_PRICE = 7000    # السعر الوهمي
    AR_ULT_PS5_FULL_REAL_PRICE = 4500    # السعر الحقيقي
    
    # Arabic Ultimate - PS5 - Primary
    AR_ULT_PS5_PRIMARY_ACTIVE = "no"    # yas = العرض شغال | no = مقفول
    AR_ULT_PS5_PRIMARY_FAKE_PRICE = 3200 # السعر الوهمي
    AR_ULT_PS5_PRIMARY_REAL_PRICE = 2000 # السعر الحقيقي
    
    # Arabic Ultimate - PS5 - Secondary
    AR_ULT_PS5_SECONDARY_ACTIVE = "no"   # yas = العرض شغال | no = مقفول
    AR_ULT_PS5_SECONDARY_FAKE_PRICE = 3500 # السعر الوهمي
    AR_ULT_PS5_SECONDARY_REAL_PRICE = 1800 # السعر الحقيقي
    
    # Arabic Ultimate - PS4 - Full
    AR_ULT_PS4_FULL_ACTIVE = "no"       # yas = العرض شغال | no = مقفول
    AR_ULT_PS4_FULL_FAKE_PRICE = 6800    # السعر الوهمي
    AR_ULT_PS4_FULL_REAL_PRICE = 4300    # السعر الحقيقي
    
    # Arabic Ultimate - PS4 - Primary
    AR_ULT_PS4_PRIMARY_ACTIVE = "no"     # yas = العرض شغال | no = مقفول
    AR_ULT_PS4_PRIMARY_FAKE_PRICE = 2500 # السعر الوهمي
    AR_ULT_PS4_PRIMARY_REAL_PRICE = 1200 # السعر الحقيقي
    
    # Arabic Ultimate - PS4 - Secondary
    AR_ULT_PS4_SECONDARY_ACTIVE = "no"  # yas = العرض شغال | no = مقفول
    AR_ULT_PS4_SECONDARY_FAKE_PRICE = 2800 # السعر الوهمي
    AR_ULT_PS4_SECONDARY_REAL_PRICE = 1900 # السعر الحقيقي
    
    # 🇺🇸 ================ ENGLISH STANDARD EDITION ================
    
    # English Standard - PS5 - Full
    EN_STD_PS5_FULL_ACTIVE = "no"        # yas = العرض شغال | no = مقفول
    EN_STD_PS5_FULL_FAKE_PRICE = 4500    # السعر الوهمي
    EN_STD_PS5_FULL_REAL_PRICE = 2800    # السعر الحقيقي
    
    # English Standard - PS5 - Primary
    EN_STD_PS5_PRIMARY_ACTIVE = "no"    # yas = العرض شغال | no = مقفول
    EN_STD_PS5_PRIMARY_FAKE_PRICE = 2200 # السعر الوهمي
    EN_STD_PS5_PRIMARY_REAL_PRICE = 1600 # السعر الحقيقي
    
    # English Standard - PS5 - Secondary
    EN_STD_PS5_SECONDARY_ACTIVE = "no"   # yas = العرض شغال | no = مقفول
    EN_STD_PS5_SECONDARY_FAKE_PRICE = 1600 # السعر الوهمي
    EN_STD_PS5_SECONDARY_REAL_PRICE = 800  # السعر الحقيقي
    
    # English Standard - PS4 - Full
    EN_STD_PS4_FULL_ACTIVE = "no"       # yas = العرض شغال | no = مقفول
    EN_STD_PS4_FULL_FAKE_PRICE = 4200    # السعر الوهمي
    EN_STD_PS4_FULL_REAL_PRICE = 2900    # السعر الحقيقي
    
    # English Standard - PS4 - Primary
    EN_STD_PS4_PRIMARY_ACTIVE = "no"     # yas = العرض شغال | no = مقفول
    EN_STD_PS4_PRIMARY_FAKE_PRICE = 1800 # السعر الوهمي
    EN_STD_PS4_PRIMARY_REAL_PRICE = 850  # السعر الحقيقي
    
    # English Standard - PS4 - Secondary
    EN_STD_PS4_SECONDARY_ACTIVE = "no"  # yas = العرض شغال | no = مقفول
    EN_STD_PS4_SECONDARY_FAKE_PRICE = 1400 # السعر الوهمي
    EN_STD_PS4_SECONDARY_REAL_PRICE = 1000 # السعر الحقيقي
    
    # 🇺🇸 ================ ENGLISH ULTIMATE EDITION ================
    
    # English Ultimate - PS5 - Full
    EN_ULT_PS5_FULL_ACTIVE = "no"        # yas = العرض شغال | no = مقفول
    EN_ULT_PS5_FULL_FAKE_PRICE = 6000    # السعر الوهمي
    EN_ULT_PS5_FULL_REAL_PRICE = 3800    # السعر الحقيقي
    
    # English Ultimate - PS5 - Primary
    EN_ULT_PS5_PRIMARY_ACTIVE = "no"    # yas = العرض شغال | no = مقفول
    EN_ULT_PS5_PRIMARY_FAKE_PRICE = 2800 # السعر الوهمي
    EN_ULT_PS5_PRIMARY_REAL_PRICE = 2000 # السعر الحقيقي
    
    # English Ultimate - PS5 - Secondary
    EN_ULT_PS5_SECONDARY_ACTIVE = "no"   # yas = العرض شغال | no = مقفول
    EN_ULT_PS5_SECONDARY_FAKE_PRICE = 2600 # السعر الوهمي
    EN_ULT_PS5_SECONDARY_REAL_PRICE = 1500 # السعر الحقيقي
    
    # English Ultimate - PS4 - Full
    EN_ULT_PS4_FULL_ACTIVE = "no"       # yas = العرض شغال | no = مقفول
    EN_ULT_PS4_FULL_FAKE_PRICE = 5800    # السعر الوهمي
    EN_ULT_PS4_FULL_REAL_PRICE = 3600    # السعر الحقيقي
    
    # English Ultimate - PS4 - Primary
    EN_ULT_PS4_PRIMARY_ACTIVE = "no"     # yas = العرض شغال | no = مقفول
    EN_ULT_PS4_PRIMARY_FAKE_PRICE = 2000 # السعر الوهمي
    EN_ULT_PS4_PRIMARY_REAL_PRICE = 1000 # السعر الحقيقي
    
    # English Ultimate - PS4 - Secondary
    EN_ULT_PS4_SECONDARY_ACTIVE = "no"  # yas = العرض شغال | no = مقفول
    EN_ULT_PS4_SECONDARY_FAKE_PRICE = 2400 # السعر الوهمي
    EN_ULT_PS4_SECONDARY_REAL_PRICE = 1700 # السعر الحقيقي
    
    # 🎮 ================ XBOX EDITIONS ================
    
    # Xbox Standard - Full
    XBOX_STD_FULL_ACTIVE = "no"          # yas = العرض شغال | no = مقفول
    XBOX_STD_FULL_FAKE_PRICE = 4500      # السعر الوهمي
    XBOX_STD_FULL_REAL_PRICE = 2800      # السعر الحقيقي
    
    # Xbox Ultimate - Full  
    XBOX_ULT_FULL_ACTIVE = "no"         # yas = العرض شغال | no = مقفول
    XBOX_ULT_FULL_FAKE_PRICE = 6200      # السعر الوهمي
    XBOX_ULT_FULL_REAL_PRICE = 3800      # السعر الحقيقي
    
    # 🖥️ ================ PC EDITIONS ================
    
    # PC Standard (شهر) - Full
    PC_STD_FULL_ACTIVE = "no"           # yas = العرض شغال | no = مقفول
    PC_STD_FULL_FAKE_PRICE = 200         # السعر الوهمي
    PC_STD_FULL_REAL_PRICE = 0           # السعر الحقيقي (مجاني)
    
    # PC Ultimate (سنة) - Full
    PC_ULT_FULL_ACTIVE = "yas"            # yas = العرض شغال | no = مقفول
    PC_ULT_FULL_FAKE_PRICE = 4000        # السعر الوهمي
    PC_ULT_FULL_REAL_PRICE = 2800        # السعر الحقيقي
    
    # 🖥️ ================ STEAM EDITIONS ================
    
    # Steam Standard - Full
    STEAM_STD_FULL_ACTIVE = "no"         # yas = العرض شغال | no = مقفول
    STEAM_STD_FULL_FAKE_PRICE = 2500     # السعر الوهمي
    STEAM_STD_FULL_REAL_PRICE = 1400     # السعر الحقيقي
    
    # Steam Ultimate - Full
    STEAM_ULT_FULL_ACTIVE = "no"        # yas = العرض شغال | no = مقفول
    STEAM_ULT_FULL_FAKE_PRICE = 4200     # السعر الوهمي
    STEAM_ULT_FULL_REAL_PRICE = 2600     # السعر الحقيقي
    
    # 📅 إعدادات العرض المنبثق
    # ========================
    SHOW_POPUP = "yas"                    # yas = يظهر البوب اب | no = مايظهرش
    POPUP_TITLE = "🔥 عروض حصرية - وفر حتى 50%!"
    POPUP_DESCRIPTION = "خصومات حقيقية لفترة محدودة - أسعار لن تتكرر!"
    
    # ⚠️ لا تغير الكود اللي تحت ده - ده بيطبق الإعدادات اللي فوق
    # ===============================================================
    
    def calculate_discount(fake_price, real_price):
        """حساب نسبة الخصم تلقائياً"""
        if fake_price <= 0 or real_price < 0 or real_price >= fake_price:
            return 0
        return round(((fake_price - real_price) / fake_price) * 100)
    
    # تجميع كل العروض النشطة
    active_offers = []
    eligible_games = []
    
    if ALL_OFFERS_ACTIVE == "yas":
        
        # Arabic Standard offers
        if AR_STD_PS5_FULL_ACTIVE == "yas":
            discount = calculate_discount(AR_STD_PS5_FULL_FAKE_PRICE, AR_STD_PS5_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Standard", "platform": "PS5", "account": "Full", 
                    "fake_price": AR_STD_PS5_FULL_FAKE_PRICE, "real_price": AR_STD_PS5_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Standard" not in eligible_games:
                    eligible_games.append("FC26_AR_Standard")
        
        if AR_STD_PS5_PRIMARY_ACTIVE == "yas":
            discount = calculate_discount(AR_STD_PS5_PRIMARY_FAKE_PRICE, AR_STD_PS5_PRIMARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Standard", "platform": "PS5", "account": "Primary",
                    "fake_price": AR_STD_PS5_PRIMARY_FAKE_PRICE, "real_price": AR_STD_PS5_PRIMARY_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Standard" not in eligible_games:
                    eligible_games.append("FC26_AR_Standard")
        
        if AR_STD_PS5_SECONDARY_ACTIVE == "yas":
            discount = calculate_discount(AR_STD_PS5_SECONDARY_FAKE_PRICE, AR_STD_PS5_SECONDARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Standard", "platform": "PS5", "account": "Secondary",
                    "fake_price": AR_STD_PS5_SECONDARY_FAKE_PRICE, "real_price": AR_STD_PS5_SECONDARY_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Standard" not in eligible_games:
                    eligible_games.append("FC26_AR_Standard")
        
        if AR_STD_PS4_FULL_ACTIVE == "yas":
            discount = calculate_discount(AR_STD_PS4_FULL_FAKE_PRICE, AR_STD_PS4_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Standard", "platform": "PS4", "account": "Full",
                    "fake_price": AR_STD_PS4_FULL_FAKE_PRICE, "real_price": AR_STD_PS4_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Standard" not in eligible_games:
                    eligible_games.append("FC26_AR_Standard")
        
        if AR_STD_PS4_PRIMARY_ACTIVE == "yas":
            discount = calculate_discount(AR_STD_PS4_PRIMARY_FAKE_PRICE, AR_STD_PS4_PRIMARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Standard", "platform": "PS4", "account": "Primary",
                    "fake_price": AR_STD_PS4_PRIMARY_FAKE_PRICE, "real_price": AR_STD_PS4_PRIMARY_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Standard" not in eligible_games:
                    eligible_games.append("FC26_AR_Standard")
        
        if AR_STD_PS4_SECONDARY_ACTIVE == "yas":
            discount = calculate_discount(AR_STD_PS4_SECONDARY_FAKE_PRICE, AR_STD_PS4_SECONDARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Standard", "platform": "PS4", "account": "Secondary",
                    "fake_price": AR_STD_PS4_SECONDARY_FAKE_PRICE, "real_price": AR_STD_PS4_SECONDARY_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Standard" not in eligible_games:
                    eligible_games.append("FC26_AR_Standard")
        
        # Arabic Ultimate offers
        if AR_ULT_PS5_FULL_ACTIVE == "yas":
            discount = calculate_discount(AR_ULT_PS5_FULL_FAKE_PRICE, AR_ULT_PS5_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Ultimate", "platform": "PS5", "account": "Full",
                    "fake_price": AR_ULT_PS5_FULL_FAKE_PRICE, "real_price": AR_ULT_PS5_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_AR_Ultimate")
        
        if AR_ULT_PS5_PRIMARY_ACTIVE == "yas":
            discount = calculate_discount(AR_ULT_PS5_PRIMARY_FAKE_PRICE, AR_ULT_PS5_PRIMARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Ultimate", "platform": "PS5", "account": "Primary",
                    "fake_price": AR_ULT_PS5_PRIMARY_FAKE_PRICE, "real_price": AR_ULT_PS5_PRIMARY_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_AR_Ultimate")
        
        if AR_ULT_PS5_SECONDARY_ACTIVE == "yas":
            discount = calculate_discount(AR_ULT_PS5_SECONDARY_FAKE_PRICE, AR_ULT_PS5_SECONDARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Ultimate", "platform": "PS5", "account": "Secondary",
                    "fake_price": AR_ULT_PS5_SECONDARY_FAKE_PRICE, "real_price": AR_ULT_PS5_SECONDARY_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_AR_Ultimate")
        
        if AR_ULT_PS4_FULL_ACTIVE == "yas":
            discount = calculate_discount(AR_ULT_PS4_FULL_FAKE_PRICE, AR_ULT_PS4_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Ultimate", "platform": "PS4", "account": "Full",
                    "fake_price": AR_ULT_PS4_FULL_FAKE_PRICE, "real_price": AR_ULT_PS4_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_AR_Ultimate")
        
        if AR_ULT_PS4_PRIMARY_ACTIVE == "yas":
            discount = calculate_discount(AR_ULT_PS4_PRIMARY_FAKE_PRICE, AR_ULT_PS4_PRIMARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Ultimate", "platform": "PS4", "account": "Primary",
                    "fake_price": AR_ULT_PS4_PRIMARY_FAKE_PRICE, "real_price": AR_ULT_PS4_PRIMARY_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_AR_Ultimate")
        
        if AR_ULT_PS4_SECONDARY_ACTIVE == "yas":
            discount = calculate_discount(AR_ULT_PS4_SECONDARY_FAKE_PRICE, AR_ULT_PS4_SECONDARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_AR_Ultimate", "platform": "PS4", "account": "Secondary",
                    "fake_price": AR_ULT_PS4_SECONDARY_FAKE_PRICE, "real_price": AR_ULT_PS4_SECONDARY_REAL_PRICE, "discount": discount
                })
                if "FC26_AR_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_AR_Ultimate")
        
        # English Standard offers
        if EN_STD_PS5_FULL_ACTIVE == "yas":
            discount = calculate_discount(EN_STD_PS5_FULL_FAKE_PRICE, EN_STD_PS5_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Standard", "platform": "PS5", "account": "Full",
                    "fake_price": EN_STD_PS5_FULL_FAKE_PRICE, "real_price": EN_STD_PS5_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Standard" not in eligible_games:
                    eligible_games.append("FC26_EN_Standard")
        
        if EN_STD_PS5_PRIMARY_ACTIVE == "yas":
            discount = calculate_discount(EN_STD_PS5_PRIMARY_FAKE_PRICE, EN_STD_PS5_PRIMARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Standard", "platform": "PS5", "account": "Primary",
                    "fake_price": EN_STD_PS5_PRIMARY_FAKE_PRICE, "real_price": EN_STD_PS5_PRIMARY_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Standard" not in eligible_games:
                    eligible_games.append("FC26_EN_Standard")
        
        if EN_STD_PS5_SECONDARY_ACTIVE == "yas":
            discount = calculate_discount(EN_STD_PS5_SECONDARY_FAKE_PRICE, EN_STD_PS5_SECONDARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Standard", "platform": "PS5", "account": "Secondary",
                    "fake_price": EN_STD_PS5_SECONDARY_FAKE_PRICE, "real_price": EN_STD_PS5_SECONDARY_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Standard" not in eligible_games:
                    eligible_games.append("FC26_EN_Standard")
        
        if EN_STD_PS4_FULL_ACTIVE == "yas":
            discount = calculate_discount(EN_STD_PS4_FULL_FAKE_PRICE, EN_STD_PS4_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Standard", "platform": "PS4", "account": "Full",
                    "fake_price": EN_STD_PS4_FULL_FAKE_PRICE, "real_price": EN_STD_PS4_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Standard" not in eligible_games:
                    eligible_games.append("FC26_EN_Standard")
        
        if EN_STD_PS4_PRIMARY_ACTIVE == "yas":
            discount = calculate_discount(EN_STD_PS4_PRIMARY_FAKE_PRICE, EN_STD_PS4_PRIMARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Standard", "platform": "PS4", "account": "Primary",
                    "fake_price": EN_STD_PS4_PRIMARY_FAKE_PRICE, "real_price": EN_STD_PS4_PRIMARY_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Standard" not in eligible_games:
                    eligible_games.append("FC26_EN_Standard")
        
        if EN_STD_PS4_SECONDARY_ACTIVE == "yas":
            discount = calculate_discount(EN_STD_PS4_SECONDARY_FAKE_PRICE, EN_STD_PS4_SECONDARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Standard", "platform": "PS4", "account": "Secondary",
                    "fake_price": EN_STD_PS4_SECONDARY_FAKE_PRICE, "real_price": EN_STD_PS4_SECONDARY_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Standard" not in eligible_games:
                    eligible_games.append("FC26_EN_Standard")
        
        # English Ultimate offers
        if EN_ULT_PS5_FULL_ACTIVE == "yas":
            discount = calculate_discount(EN_ULT_PS5_FULL_FAKE_PRICE, EN_ULT_PS5_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Ultimate", "platform": "PS5", "account": "Full",
                    "fake_price": EN_ULT_PS5_FULL_FAKE_PRICE, "real_price": EN_ULT_PS5_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_EN_Ultimate")
        
        if EN_ULT_PS5_PRIMARY_ACTIVE == "yas":
            discount = calculate_discount(EN_ULT_PS5_PRIMARY_FAKE_PRICE, EN_ULT_PS5_PRIMARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Ultimate", "platform": "PS5", "account": "Primary",
                    "fake_price": EN_ULT_PS5_PRIMARY_FAKE_PRICE, "real_price": EN_ULT_PS5_PRIMARY_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_EN_Ultimate")
        
        if EN_ULT_PS5_SECONDARY_ACTIVE == "yas":
            discount = calculate_discount(EN_ULT_PS5_SECONDARY_FAKE_PRICE, EN_ULT_PS5_SECONDARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Ultimate", "platform": "PS5", "account": "Secondary",
                    "fake_price": EN_ULT_PS5_SECONDARY_FAKE_PRICE, "real_price": EN_ULT_PS5_SECONDARY_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_EN_Ultimate")
        
        if EN_ULT_PS4_FULL_ACTIVE == "yas":
            discount = calculate_discount(EN_ULT_PS4_FULL_FAKE_PRICE, EN_ULT_PS4_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Ultimate", "platform": "PS4", "account": "Full",
                    "fake_price": EN_ULT_PS4_FULL_FAKE_PRICE, "real_price": EN_ULT_PS4_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_EN_Ultimate")
        
        if EN_ULT_PS4_PRIMARY_ACTIVE == "yas":
            discount = calculate_discount(EN_ULT_PS4_PRIMARY_FAKE_PRICE, EN_ULT_PS4_PRIMARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Ultimate", "platform": "PS4", "account": "Primary",
                    "fake_price": EN_ULT_PS4_PRIMARY_FAKE_PRICE, "real_price": EN_ULT_PS4_PRIMARY_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_EN_Ultimate")
        
        if EN_ULT_PS4_SECONDARY_ACTIVE == "yas":
            discount = calculate_discount(EN_ULT_PS4_SECONDARY_FAKE_PRICE, EN_ULT_PS4_SECONDARY_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_EN_Ultimate", "platform": "PS4", "account": "Secondary",
                    "fake_price": EN_ULT_PS4_SECONDARY_FAKE_PRICE, "real_price": EN_ULT_PS4_SECONDARY_REAL_PRICE, "discount": discount
                })
                if "FC26_EN_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_EN_Ultimate")
        
        # Xbox offers
        if XBOX_STD_FULL_ACTIVE == "yas":
            discount = calculate_discount(XBOX_STD_FULL_FAKE_PRICE, XBOX_STD_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_XBOX_Standard", "platform": "Xbox", "account": "Full",
                    "fake_price": XBOX_STD_FULL_FAKE_PRICE, "real_price": XBOX_STD_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_XBOX_Standard" not in eligible_games:
                    eligible_games.append("FC26_XBOX_Standard")
        
        if XBOX_ULT_FULL_ACTIVE == "yas":
            discount = calculate_discount(XBOX_ULT_FULL_FAKE_PRICE, XBOX_ULT_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_XBOX_Ultimate", "platform": "Xbox", "account": "Full",
                    "fake_price": XBOX_ULT_FULL_FAKE_PRICE, "real_price": XBOX_ULT_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_XBOX_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_XBOX_Ultimate")
        
        # PC offers
        if PC_STD_FULL_ACTIVE == "yas" and PC_STD_FULL_REAL_PRICE >= 0:  # PC مجاني ممكن يكون له عرض وهمي
            discount = calculate_discount(PC_STD_FULL_FAKE_PRICE, PC_STD_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_PC_Standard", "platform": "PC", "account": "Full",
                    "fake_price": PC_STD_FULL_FAKE_PRICE, "real_price": PC_STD_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_PC_Standard" not in eligible_games:
                    eligible_games.append("FC26_PC_Standard")
        
        if PC_ULT_FULL_ACTIVE == "yas":
            discount = calculate_discount(PC_ULT_FULL_FAKE_PRICE, PC_ULT_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_PC_Ultimate", "platform": "PC", "account": "Full",
                    "fake_price": PC_ULT_FULL_FAKE_PRICE, "real_price": PC_ULT_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_PC_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_PC_Ultimate")
        
        # Steam offers
        if STEAM_STD_FULL_ACTIVE == "yas":
            discount = calculate_discount(STEAM_STD_FULL_FAKE_PRICE, STEAM_STD_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_STEAM_Standard", "platform": "Steam", "account": "Full",
                    "fake_price": STEAM_STD_FULL_FAKE_PRICE, "real_price": STEAM_STD_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_STEAM_Standard" not in eligible_games:
                    eligible_games.append("FC26_STEAM_Standard")
        
        if STEAM_ULT_FULL_ACTIVE == "yas":
            discount = calculate_discount(STEAM_ULT_FULL_FAKE_PRICE, STEAM_ULT_FULL_REAL_PRICE)
            if discount > 0:
                active_offers.append({
                    "game": "FC26_STEAM_Ultimate", "platform": "Steam", "account": "Full",
                    "fake_price": STEAM_ULT_FULL_FAKE_PRICE, "real_price": STEAM_ULT_FULL_REAL_PRICE, "discount": discount
                })
                if "FC26_STEAM_Ultimate" not in eligible_games:
                    eligible_games.append("FC26_STEAM_Ultimate")
    
    return {
        "active_offer": {
            "id": f"smart_pricing_2025",
            "title": POPUP_TITLE,
            "description": POPUP_DESCRIPTION,
            "offers_list": active_offers,
            "show_popup": SHOW_POPUP == "yas" and ALL_OFFERS_ACTIVE == "yas" and len(active_offers) > 0,
            "popup_frequency": "once_per_session"
        } if active_offers else None,
        "offer_cards": eligible_games if active_offers else []
    }


# 🔥 دالة تطبيق الأسعار الذكية - حط الدالة دي بعد get_offers مباشرة
def apply_offer_discount(prices, offers):
    """تطبيق الأسعار الذكية مع الخصومات الوهمية"""
    if not offers.get("active_offer") or not offers["active_offer"].get("offers_list"):
        return prices
    
    offers_list = offers["active_offer"]["offers_list"]
    
    for offer in offers_list:
        game_id = offer["game"]
        target_platform = offer["platform"]
        target_account = offer["account"]
        fake_price = offer["fake_price"]
        real_price = offer["real_price"]
        discount_percent = offer["discount"]
        
        if game_id in prices["games"]:
            if target_platform in prices["games"][game_id]["platforms"]:
                platform_data = prices["games"][game_id]["platforms"][target_platform]
                if target_account in platform_data["accounts"]:
                    account = platform_data["accounts"][target_account]
                    
                    # تطبيق الأسعار الذكية
                    account["original_price"] = fake_price      # السعر الوهمي (اللي هيتشطب)
                    account["price"] = real_price               # السعر الحقيقي (اللي العميل هيدفعه)
                    account["discount_percentage"] = discount_percent  # نسبة الخصم المحسوبة
    
    return prices
# الأسعار الثابتة - مدمجة في الكود مباشرة
def get_prices():
    return {
        "games": {
            "FC26_EN_Standard": {
                "name": "Standard Edition (English) 🇺🇸",
                "platforms": {
                    "PS5": {
                        "name": "PlayStation PS/5",
                        "icon": '''<div style="text-align: center; margin: 8px auto;">
                            <i class="fab fa-playstation" style="color: #003087; font-size: 40px; line-height: 1;"></i>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل", "price": 3200},
                            "Primary": {"name": "Primary - تفعيل أساسي", "price": 1600},
                            "Secondary": {"name": "Secondary - تسجيل دخول مؤقت", "price": 1000}
                        }
                    },
                    "PS4": {
                        "name": "PlayStation PS/4",
                        "icon": '''<div style="text-align: center; margin: 8px auto;">
                            <i class="fab fa-playstation" style="color: #003087; font-size: 40px; line-height: 1;"></i>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل", "price": 3200},
                            "Primary": {"name": "Primary - تفعيل أساسي", "price": 1000},
                            "Secondary": {"name": "Secondary - تسجيل دخول مؤقت", "price": 1000}
                        }
                    }
                }
            },
            "FC26_EN_Ultimate": {
                "name": "Ultimate Edition (English) 🇺🇸",
                "platforms": {
                    "PS5": {
                        "name": "PlayStation PS/5",
                        "icon": '''<div style="text-align: center; margin: 8px auto; position: relative; display: inline-block;">
                            <i class="fab fa-playstation" style="color: #003087; font-size: 40px; line-height: 1;"></i>
                            <div style="position: absolute; top: -5px; right: -5px; background: #003087; color: white; font-size: 10px; padding: 2px 4px; border-radius: 10px; font-weight: bold; box-shadow: 0 0 8px rgba(0, 48, 135, 0.6);">ULT</div>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل", "price": 4300},
                            "Primary": {"name": "Primary - تفعيل أساسي", "price": 2000},
                            "Secondary": {"name": "Secondary - تسجيل دخول مؤقت", "price": 1900}
                        }
                    },
                    "PS4": {
                        "name": "PlayStation PS/4", 
                        "icon": '''<div style="text-align: center; margin: 8px auto; position: relative; display: inline-block;">
                            <i class="fab fa-playstation" style="color: #003087; font-size: 40px; line-height: 1;"></i>
                            <div style="position: absolute; top: -5px; right: -5px; background: #003087; color: white; font-size: 10px; padding: 2px 4px; border-radius: 10px; font-weight: bold; box-shadow: 0 0 8px rgba(0, 48, 135, 0.6);">ULT</div>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل", "price": 4300},
                            "Primary": {"name": "Primary - تفعيل أساسي", "price": 1200},
                            "Secondary": {"name": "Secondary - تسجيل دخول مؤقت", "price": 1900}
                        }
                    }
                }
            },
            "FC26_AR_Standard": {
                "name": "Standard Edition (Arabic) 🇸🇦",
                "platforms": {
                    "PS5": {
                        "name": "PlayStation PS/5",
                        "icon": '''<div style="text-align: center; margin: 8px auto;">
                            <i class="fab fa-playstation" style="color: #003087; font-size: 40px; line-height: 1;"></i>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل", "price": 3600},
                            "Primary": {"name": "Primary - تفعيل أساسي", "price": 2000},
                            "Secondary": {"name": "Secondary - تسجيل دخول مؤقت", "price": 1200}
                        }
                    },
                    "PS4": {
                        "name": "PlayStation PS/4",
                        "icon": '''<div style="text-align: center; margin: 8px auto;">
                            <i class="fab fa-playstation" style="color: #003087; font-size: 40px; line-height: 1;"></i>
                        </div>''', 
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل", "price": 3600},
                            "Primary": {"name": "Primary - تفعيل أساسي", "price": 1500},
                            "Secondary": {"name": "Secondary - تسجيل دخول مؤقت", "price": 1200}
                        }
                    }
                }
            },
            "FC26_AR_Ultimate": {
                "name": "Ultimate Edition (Arabic) 🇸🇦",
                "platforms": {
                    "PS5": {
                        "name": "PlayStation PS/5",
                        "icon": '''<div style="text-align: center; margin: 8px auto; position: relative; display: inline-block;">
                            <i class="fab fa-playstation" style="color: #003087; font-size: 40px; line-height: 1;"></i>
                            <div style="position: absolute; top: -5px; right: -5px; background: #7b1fa2; color: white; font-size: 10px; padding: 2px 4px; border-radius: 10px; font-weight: bold; box-shadow: 0 0 8px rgba(123, 31, 162, 0.6);">ULT</div>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل", "price": 5200},
                            "Primary": {"name": "Primary - تفعيل أساسي", "price": 2300},
                            "Secondary": {"name": "Secondary - تسجيل دخول مؤقت", "price": 2200}
                        }
                    },
                    "PS4": {
                        "name": "PlayStation PS/4",
                        "icon": '''<div style="text-align: center; margin: 8px auto; position: relative; display: inline-block;">
                            <i class="fab fa-playstation" style="color: #003087; font-size: 40px; line-height: 1;"></i>
                            <div style="position: absolute; top: -5px; right: -5px; background: #7b1fa2; color: white; font-size: 10px; padding: 2px 4px; border-radius: 10px; font-weight: bold; box-shadow: 0 0 8px rgba(123, 31, 162, 0.6);">ULT</div>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل", "price": 5200},
                            "Primary": {"name": "Primary - تفعيل أساسي", "price": 1700},
                            "Secondary": {"name": "Secondary - تسجيل دخول مؤقت", "price": 2200}
                        }
                    }
                }
            },
            "FC26_XBOX_Standard": {
                "name": "Xbox Standard Edition 🎮",
                "platforms": {
                    "Xbox": {
                        "name": "Xbox Series X/S & Xbox One",
                        "icon": '''<div style="text-align: center; margin: 8px auto;">
                            <i class="fab fa-xbox" style="color: #107C10; font-size: 40px; line-height: 1;"></i>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل", "price": 3200},

                        }
                    }
                }
            },
            "FC26_XBOX_Ultimate": {
                "name": "Xbox Ultimate Edition 🎮",
                "platforms": {
                    "Xbox": {
                        "name": "Xbox Series X/S & Xbox One",
                        "icon": '''<div style="text-align: center; margin: 8px auto; position: relative; display: inline-block;">
                            <i class="fab fa-xbox" style="color: #107C10; font-size: 40px; line-height: 1;"></i>
                            <div style="position: absolute; top: -5px; right: -5px; background: #ff8f00; color: white; font-size: 10px; padding: 2px 4px; border-radius: 10px; font-weight: bold; box-shadow: 0 0 8px rgba(255, 143, 0, 0.6);">ULT</div>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل", "price": 4200},
  
                        }
                    }
                }
            },
            "FC26_PC_Standard": {
                "name": "PC (شهر) (month)  🖥️",
                "platforms": {
                    "PC": {
                        "name": "PC (EA PRO)",
                        "icon": '''<svg width="40" height="40" viewBox="0 0 24 24" fill="#FF8C00" style="display: block; margin: 0 auto;">
                            <rect x="2" y="4" width="20" height="12" rx="2" fill="#FF8C00"/>
                            <rect x="4" y="6" width="16" height="8" fill="white"/>
                            <rect x="8" y="18" width="8" height="2" fill="#FF8C00"/>
                            <rect x="6" y="20" width="12" height="2" fill="#FF8C00"/>
                        </svg>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل على حسابك الشخصي 🔐", "price": 0}
                        }
                    }
                }
            },
            "FC26_PC_Ultimate": {
                "name": "PC (سنة) (year)  🖥️",
                "platforms": {
                    "PC": {
                        "name": "PC (EA PRO)",
                        "icon": '''<div style="text-align: center; margin: 8px auto; position: relative; display: inline-block;">
                            <svg width="40" height="40" viewBox="0 0 24 24" fill="#FF8C00" style="display: block; margin: 0 auto;">
                                <rect x="2" y="4" width="20" height="12" rx="2" fill="#FF8C00"/>
                                <rect x="4" y="6" width="16" height="8" fill="white"/>
                                <rect x="8" y="18" width="8" height="2" fill="#FF8C00"/>
                                <rect x="6" y="20" width="12" height="2" fill="#FF8C00"/>
                            </svg>
                            <div style="position: absolute; top: -5px; right: -5px; background: #25D366; color: white; font-size: 10px; padding: 2px 4px; border-radius: 10px; font-weight: bold; box-shadow: 0 0 8px rgba(37, 211, 102, 0.6);">PRO</div>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل على حسابك الشخصي 🔐", "price": 2800}
                        }
                    }
                }
            },
            "FC26_STEAM_Standard": {
                "name": "Steam Standard Edition 🖥️",
                "platforms": {
                    "Steam": {
                        "name": "PC (STEAM)",
                        "icon": '''<div style="text-align: center; margin: 8px auto;">
                            <i class="fab fa-steam-symbol" style="font-size: 40px; color: #ff0000; background: rgba(0, 0, 0, 0.8); padding: 8px; border-radius: 50%; border: 3px solid #ff0000; box-shadow: 0 0 20px rgba(255, 0, 0, 0.6); transition: transform 0.3s ease, box-shadow 0.3s ease; line-height: 1;"></i>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل مع First Email", "price": 1700}
                        }
                    }
                }
            },
            "FC26_STEAM_Ultimate": {
                "name": "Steam Ultimate Edition 🖥️",
                "platforms": {
                    "Steam": {
                        "name": "PC (STEAM)",
                        "icon": '''<div style="text-align: center; margin: 8px auto; position: relative; display: inline-block;">
                            <i class="fab fa-steam-symbol" style="font-size: 40px; color: #ff0000; background: rgba(0, 0, 0, 0.8); padding: 8px; border-radius: 50%; border: 3px solid #ff0000; box-shadow: 0 0 20px rgba(255, 0, 0, 0.6); transition: transform 0.3s ease, box-shadow 0.3s ease; line-height: 1;"></i>
                            <div style="position: absolute; top: -5px; right: -5px; background: #ff0000; color: white; font-size: 10px; padding: 2px 4px; border-radius: 10px; font-weight: bold; box-shadow: 0 0 8px rgba(255, 0, 0, 0.6);">ULT</div>
                        </div>''',
                        "accounts": {
                            "Full": {"name": "Full - حساب كامل مع First Email", "price": 3000}
                        }
                    }
                }
            }
        },
        "settings": {
            "currency": "جنيه مصري",
            "warranty": "1 سنة",
            "delivery_time": "15 ساعة كحد أقصى",
            "whatsapp_number": "+201094591331"
        }
    }

                       
# Headers أمنية قوية
@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://wa.me"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

# تنظيف المدخلات
def sanitize_input(text, max_length=100):
    if not text:
        return None
    
    text = str(text).strip()
    
    if len(text) > max_length:
        return None
    
    text = re.sub(r'[<>"\';\\&]', '', text)
    text = re.sub(r'(script|javascript|vbscript|onload|onerror)', '', text, flags=re.IGNORECASE)
    
    return text

# 🔥 الصفحة الرئيسية المحدثة - هنا بتغير الدالة دي
@app.route('/')
@rate_limit(max_requests=25, window=60)
def index():
    try:
        prices = get_prices()
        offers = get_offers()
        
        # تطبيق العروض على الأسعار
        prices = apply_offer_discount(prices, offers)
        
        logger.info("✅ تم تحميل الصفحة الرئيسية بنجاح مع العروض")
        return render_template('index.html', prices=prices, offers=offers)
    except Exception as e:
        logger.error(f"❌ خطأ في الصفحة الرئيسية: {e}")
        abort(500)

# إنشاء رابط واتساب مباشر
@app.route('/whatsapp', methods=['POST'])
@rate_limit(max_requests=8, window=60)
def create_whatsapp_link():
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    
    try:
        # فحص Anti-spam
        if not anti_spam_check(client_ip, user_agent):
            return jsonify({'error': 'تم تجاوز الحد المسموح - يرجى المحاولة لاحقاً'}), 429
        
        # تنظيف البيانات
        game_type = sanitize_input(request.form.get('game_type'))
        platform = sanitize_input(request.form.get('platform'))
        account_type = sanitize_input(request.form.get('account_type'))
        
        if not all([game_type, platform, account_type]):
            return jsonify({'error': 'يرجى اختيار جميع الخيارات أولاً'}), 400
        
        # 🔥 تحميل الأسعار والعروض هنا
        prices = get_prices()
        offers = get_offers()
        
        # تطبيق العروض على الأسعار
        prices = apply_offer_discount(prices, offers)
        
        if (game_type not in prices.get('games', {}) or
            platform not in prices['games'][game_type].get('platforms', {}) or
            account_type not in prices['games'][game_type]['platforms'][platform].get('accounts', {})):
            logger.warning(f"🚨 اختيار منتج غير صحيح من IP: {client_ip}")
            return jsonify({'error': 'اختيار المنتج غير صحيح'}), 400
        
        # بيانات المنتج
        game_name = prices['games'][game_type]['name']
        platform_name = prices['games'][game_type]['platforms'][platform]['name']
        account_name = prices['games'][game_type]['platforms'][platform]['accounts'][account_type]['name']
        price = prices['games'][game_type]['platforms'][platform]['accounts'][account_type]['price']
        currency = prices.get('settings', {}).get('currency', 'جنيه')
        
        # إنشاء ID مرجعي
        timestamp = str(int(time.time()))
        reference_id = hashlib.md5(f"{timestamp}{client_ip}{game_type}{platform}".encode()).hexdigest()[:8].upper()
        
        # إنشاء رسالة الواتساب - بدون وقت الاستفسار
        message = f"""🎮 *استفسار من {BUSINESS_NAME}*

🆔 *المرجع:* {reference_id}

🎯 *المطلوب:*
• اللعبة: {game_name}

• المنصة: {platform_name}

• نوع الحساب: {account_name}

• السعر: {format_number(price)} {currency}

👋 *السلام عليكم، أريد الاستفسار عن هذا المنتج*

شكراً 🌟"""
        
        # ترميز الرسالة للـ URL
        encoded_message = urllib.parse.quote(message)
        
        # رقم الواتساب
        whatsapp_number = prices.get('settings', {}).get('whatsapp_number', WHATSAPP_NUMBER)
        clean_number = whatsapp_number.replace('+', '').replace('-', '').replace(' ', '')
        
        # إنشاء رابط الواتساب
        whatsapp_url = f"https://wa.me/{clean_number}?text={encoded_message}"
        
        logger.info(f"✅ فتح واتساب: {reference_id} - {platform} {account_type} - {format_number(price)} {currency} - IP: {client_ip}")
        
        return jsonify({
            'success': True,
            'reference_id': reference_id,
            'whatsapp_url': whatsapp_url,
            'price': format_number(price),
            'currency': currency,
            'message': 'سيتم فتح الواتساب الآن...'
        })
        
    except Exception as e:
        logger.error(f"❌ خطأ في إنشاء رابط الواتساب: {e}")
        return jsonify({'error': 'حدث خطأ في النظام - يرجى المحاولة مرة أخرى'}), 500

# 🔥 API جديد للعروض - تضيف دي بعد get_prices_api
@app.route('/api/offers')
@rate_limit(max_requests=15, window=60)
def get_offers_api():
    try:
        offers = get_offers()
        return jsonify(offers)
    except Exception as e:
        logger.error(f"❌ خطأ في API العروض: {e}")
        return jsonify({'error': 'خطأ في النظام'}), 500

# API للحصول على الأسعار
@app.route('/api/prices')
@rate_limit(max_requests=15, window=60)
def get_prices_api():
    try:
        prices = get_prices()
        offers = get_offers()
        # تطبيق العروض على الأسعار
        prices = apply_offer_discount(prices, offers)
        return jsonify(prices)
    except Exception as e:
        logger.error(f"❌ خطأ في API الأسعار: {e}")
        return jsonify({'error': 'خطأ في النظام'}), 500

# Health check
@app.route('/health')
@app.route('/ping')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}, 200

# Robots.txt
@app.route('/robots.txt')
def robots():
    return '''User-agent: *
Disallow: /admin/
Disallow: /api/
Crawl-delay: 10''', 200, {'Content-Type': 'text/plain'}

# معالجات الأخطاء
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'طلب غير صحيح'}), 400

@app.errorhandler(404)
def not_found(error):
    return "الصفحة غير موجودة", 404

@app.errorhandler(429)
def too_many_requests(error):
    return "تم تجاوز عدد الطلبات المسموحة", 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"❌ خطأ داخلي: {error}")
    return f"خطأ داخلي: {error}", 500

# إضافة filter للـ Jinja2 لتنسيق الأرقام
@app.template_filter('format_number')
def format_number_filter(number):
    return format_number(number)

# تشغيل التطبيق
if __name__ == '__main__':
    logger.info("🚀 تم تشغيل التطبيق بنجاح - الأسعار مدمجة في الكود مع فاصلة عشرية والعروض")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    logger.info("🚀 تم تشغيل التطبيق عبر gunicorn - الأسعار مدمجة في الكود مع فاصلة عشرية والعروض")

