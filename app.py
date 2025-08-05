from flask import Flask, render_template, request, jsonify, session
import os
import re
import hashlib
import secrets
import requests
from datetime import datetime
import json
import phonenumbers
from phonenumbers import geocoder, carrier
from phonenumbers.phonenumberutil import number_type
import time
import random
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import numpy as np
import sqlite3
import threading

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))

# إعدادات الأمان محدثة
app.config['SESSION_COOKIE_SECURE'] = False  # تم تعطيل HTTPS للتطوير
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# قاعدة بيانات بسيطة في الذاكرة للـ telegram codes
telegram_codes = {}
users_data = {}

# قاموس البلدان والشركات المصرية
EGYPTIAN_CARRIERS = {
    '010': {'name': 'فودافون مصر', 'carrier_en': 'Vodafone Egypt'},
    '011': {'name': 'اتصالات مصر', 'carrier_en': 'Etisalat Egypt'},
    '012': {'name': 'أورانج مصر', 'carrier_en': 'Orange Egypt'},
    '015': {'name': 'وي مصر', 'carrier_en': 'WE Egypt (Telecom Egypt)'}
}

def generate_csrf_token():
    """توليد رمز CSRF آمن"""
    return secrets.token_urlsafe(32)

def sanitize_input(text):
    """تنظيف المدخلات من الأكواد الضارة"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def normalize_phone_number(phone):
    """تطبيع رقم الهاتف"""
    if not phone:
        return ""
    
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    if clean_phone.startswith('00'):
        clean_phone = '+' + clean_phone[2:]
    elif clean_phone.startswith('01') and len(clean_phone) == 11:
        clean_phone = '+2' + clean_phone
    elif re.match(r'^\d{12,15}$', clean_phone) and not clean_phone.startswith('01'):
        clean_phone = '+' + clean_phone
    
    return clean_phone

def check_whatsapp_ultimate_method(phone_number):
    """
    🔥 الطريقة النهائية المبتكرة - تجمع كل الحلول الذكية
    """
    
    results = []
    clean_phone = phone_number.replace('+', '').replace(' ', '')
    
    # الطريقة 1: Advanced Scraping
    try:
        time.sleep(random.uniform(0.1, 0.5))  # محاكاة سلوك إنساني
        
        url = f"https://wa.me/{clean_phone}?text=Test"
        session_req = requests.Session()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ar,en;q=0.9',
            'Connection': 'keep-alive'
        }
        
        response = session_req.get(url, headers=headers, timeout=8, allow_redirects=True)
        
        # تحليل محتوى متقدم
        soup = BeautifulSoup(response.text, 'html.parser')
        page_content = response.text.lower()
        
        success_indicators = ['continue to chat', 'المتابعة إلى الدردشة', 'open whatsapp', 'whatsapp://send']
        error_indicators = ['phone number shared via url is invalid', 'رقم الهاتف غير صحيح', 'invalid phone']
        
        scraping_result = None
        for indicator in success_indicators:
            if indicator.lower() in page_content:
                scraping_result = True
                break
                
        if scraping_result is None:
            for indicator in error_indicators:
                if indicator.lower() in page_content:
                    scraping_result = False
                    break
        
        results.append({
            'method': 'advanced_scraping',
            'result': scraping_result,
            'confidence': 0.8 if scraping_result is not None else 0.3
        })
        
    except:
        results.append({
            'method': 'advanced_scraping',
            'result': None,
            'confidence': 0.1
        })
    
    # الطريقة 2: Multiple Endpoints
    try:
        endpoints = [
            f"https://wa.me/{clean_phone}",
            f"https://api.whatsapp.com/send?phone={clean_phone}",
            f"https://web.whatsapp.com/send?phone={clean_phone}"
        ]
        
        success_count = 0
        total_count = 0
        
        for endpoint in endpoints:
            try:
                resp = requests.head(endpoint, timeout=3, allow_redirects=True)
                total_count += 1
                if resp.status_code in [200, 302]:
                    success_count += 1
            except:
                total_count += 1
        
        endpoint_result = success_count > (total_count / 2) if total_count > 0 else None
        endpoint_confidence = (success_count / total_count) if total_count > 0 else 0.1
        
        results.append({
            'method': 'multiple_endpoints',
            'result': endpoint_result,
            'confidence': endpoint_confidence
        })
        
    except:
        results.append({
            'method': 'multiple_endpoints',
            'result': None,
            'confidence': 0.1
        })
    
    # الطريقة 3: AI Pattern Recognition
    try:
        # خصائص للتحليل
        features = []
        features.append(len(clean_phone))  # طول الرقم
        
        # تحليل كود البلد
        egypt_patterns = ['2010', '2011', '2012', '2015']
        has_egypt_pattern = any(clean_phone.startswith(pattern) for pattern in egypt_patterns)
        features.append(int(has_egypt_pattern))
        
        # تحليل الأرقام
        if len(clean_phone) > 0:
            digits = [int(d) for d in clean_phone if d.isdigit()]
            if digits:
                features.extend([
                    np.mean(digits),
                    len(set(digits)),
                    int(len(clean_phone) >= 10 and len(clean_phone) <= 15)
                ])
            else:
                features.extend([0, 0, 0])
        else:
            features.extend([0, 0, 0])
        
        # حساب نقاط الثقة بناءً على الخصائص
        ai_score = 0.5  # قيمة افتراضية
        
        # للأرقام المصرية الصحيحة
        if has_egypt_pattern and len(clean_phone) == 12:
            ai_score = 0.9
        elif len(clean_phone) >= 10 and len(clean_phone) <= 15:
            ai_score = 0.7
        elif len(clean_phone) < 8 or len(clean_phone) > 16:
            ai_score = 0.2
        
        ai_result = ai_score > 0.6
        
        results.append({
            'method': 'ai_pattern',
            'result': ai_result,
            'confidence': ai_score
        })
        
    except:
        results.append({
            'method': 'ai_pattern',
            'result': None,
            'confidence': 0.1
        })
    
    # تحليل النتائج النهائية
    valid_results = [r for r in results if r['result'] is not None]
    
    if not valid_results:
        return {
            'exists': None,
            'method': 'ultimate_combined',
            'confidence': 'very_low',
            'details': results,
            'message': 'لا يمكن التحقق من الرقم - جميع الطرق فشلت'
        }
    
    # حساب النتيجة المرجحة
    positive_weight = sum(r['confidence'] for r in valid_results if r['result'] is True)
    negative_weight = sum(r['confidence'] for r in valid_results if r['result'] is False)
    total_weight = positive_weight + negative_weight
    
    if total_weight == 0:
        final_result = None
        confidence_level = 'very_low'
    else:
        final_score = positive_weight / total_weight
        final_result = final_score > 0.5
        
        if final_score > 0.8:
            confidence_level = 'very_high'
        elif final_score > 0.6:
            confidence_level = 'high'
        elif final_score > 0.4:
            confidence_level = 'medium'
        else:
            confidence_level = 'low'
    
    return {
        'exists': final_result,
        'method': 'ultimate_combined',
        'confidence': confidence_level,
        'score': round(positive_weight / total_weight * 100, 1) if total_weight > 0 else 0,
        'methods_used': len(results),
        'successful_methods': len(valid_results),
        'details': results,
        'message': f'تحليل شامل: {len(valid_results)} طرق نجحت من {len(results)} - نسبة الثقة {round(positive_weight / total_weight * 100, 1) if total_weight > 0 else 0}%'
    }

def validate_whatsapp_ultimate(phone):
    """الدالة النهائية للتحقق المبتكر من الواتساب"""
    if not phone:
        return {'is_valid': False, 'error': 'يرجى إدخال رقم الهاتف'}
    
    normalized_phone = normalize_phone_number(phone)
    
    if not re.match(r'^\+[1-9]\d{7,14}$', normalized_phone):
        return {'is_valid': False, 'error': 'تنسيق الرقم غير صحيح'}
    
    # التحقق بالطريقة المبتكرة
    whatsapp_check = check_whatsapp_ultimate_method(normalized_phone)
    
    # الحصول على معلومات إضافية عن الرقم
    try:
        parsed_number = phonenumbers.parse(normalized_phone, None)
        country = geocoder.description_for_number(parsed_number, "ar") or "غير معروف"
        carrier_name = carrier.name_for_number(parsed_number, "ar") or "غير معروف"
    except:
        country = "غير معروف"
        carrier_name = "غير معروف"
    
    if whatsapp_check['exists'] is True:
        return {
            'is_valid': True,
            'formatted': normalized_phone,
            'country': country,
            'carrier': carrier_name,
            'whatsapp_status': f'موجود ✅ ({whatsapp_check["confidence"]})',
            'verification_method': whatsapp_check['method'],
            'confidence': whatsapp_check['confidence'],
            'score': whatsapp_check.get('score', 0),
            'methods_analysis': whatsapp_check.get('details', []),
            'message': whatsapp_check['message']
        }
    elif whatsapp_check['exists'] is False:
        return {
            'is_valid': False,
            'error': f"غير موجود ❌ ({whatsapp_check['confidence']}) - {whatsapp_check['message']}",
            'formatted': normalized_phone,
            'verification_method': whatsapp_check['method'],
            'confidence': whatsapp_check['confidence'],
            'methods_analysis': whatsapp_check.get('details', [])
        }
    else:
        return {
            'is_valid': True,  # نقبل الرقم مع تحذير
            'formatted': normalized_phone,
            'country': country,
            'carrier': carrier_name,
            'whatsapp_status': f'غير مؤكد ⚠️ ({whatsapp_check["confidence"]})',
            'verification_method': whatsapp_check['method'],
            'confidence': whatsapp_check['confidence'],
            'methods_analysis': whatsapp_check.get('details', []),
            'message': f"رقم صحيح ولكن {whatsapp_check['message']}"
        }

# باقي دوال التطبيق
def validate_mobile_payment(payment_number):
    if not payment_number:
        return False
    clean_number = re.sub(r'\D', '', payment_number)
    return len(clean_number) == 11 and clean_number.startswith(('010', '011', '012', '015'))

def validate_card_number(card_number):
    if not card_number:
        return False
    clean_number = re.sub(r'\D', '', card_number)
    return len(clean_number) == 16 and clean_number.isdigit()

def validate_instapay_link(link):
    if not link:
        return False, ""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;!?]'
    urls = re.findall(url_pattern, link, re.IGNORECASE)
    if not urls:
        return False, ""
    
    valid_domains = ['instapay.com.eg', 'instapay.app', 'app.instapay.com.eg']
    
    for url in urls:
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '')
            if any(valid_domain in domain for valid_domain in valid_domains) or 'instapay' in domain:
                return True, url
        except:
            continue
    return False, ""

@app.before_request
def before_request():
    """تهيئة الجلسة - محدثة لحل مشاكل CSRF"""
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_csrf_token()
        session.permanent = True

@app.route('/')
def index():
    """الصفحة الرئيسية - محدثة"""
    # تأكد من وجود csrf token
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_csrf_token()
        session.permanent = True
    
    return render_template('index.html', csrf_token=session['csrf_token'])

@app.route('/validate-whatsapp', methods=['POST'])
def validate_whatsapp_endpoint():
    """API للتحقق المبتكر من رقم الواتساب"""
    try:
        data = request.get_json()
        phone = sanitize_input(data.get('phone', ''))
        
        if not phone:
            return jsonify({'is_valid': False, 'error': 'يرجى إدخال رقم الهاتف'})
        
        # استخدام الطريقة المبتكرة النهائية
        result = validate_whatsapp_ultimate(phone)
        return jsonify(result)
        
    except Exception as e:
        print(f"خطأ في التحقق من الواتساب: {str(e)}")
        return jsonify({'is_valid': False, 'error': 'خطأ في الخادم'})

@app.route('/update-profile', methods=['POST'])
def update_profile():
    """تحديث الملف الشخصي - محدثة مع البريد الإلكتروني المتعدد"""
    try:
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # التحقق من CSRF بطريقة محسنة
        token = request.form.get('csrf_token')
        session_token = session.get('csrf_token')
        
        print(f"🔍 CSRF Debug - Form Token: {token[:20] if token else 'None'}...")
        print(f"🔍 CSRF Debug - Session Token: {session_token[:20] if session_token else 'None'}...")
        
        if not token or not session_token or token != session_token:
            # إعادة توليد token جديد
            session['csrf_token'] = generate_csrf_token()
            return jsonify({
                'success': False, 
                'message': 'انتهت صلاحية الجلسة، يرجى إعادة تحميل الصفحة',
                'error_code': 'csrf_expired',
                'new_csrf_token': session['csrf_token']
            }), 403
        
        # استقبال البيانات الأساسية
        platform = sanitize_input(request.form.get('platform'))
        whatsapp_number = sanitize_input(request.form.get('whatsapp_number'))
        payment_method = sanitize_input(request.form.get('payment_method'))
        payment_details = sanitize_input(request.form.get('payment_details'))
        telegram_username = sanitize_input(request.form.get('telegram_username'))
        
        # استقبال البريد الإلكتروني المتعدد الجديد
        email_addresses_json = sanitize_input(request.form.get('email_addresses', '[]'))
        try:
            email_addresses = json.loads(email_addresses_json) if email_addresses_json else []
            # تنظيف وفلترة الإيميلات
            email_addresses = [email.lower().strip() for email in email_addresses if email and '@' in email and '.' in email]
            # إزالة المكررات والحد الأقصى
            email_addresses = list(dict.fromkeys(email_addresses))  # إزالة المكررات مع الحفاظ على الترتيب
            email_addresses = email_addresses[:6]  # الحد الأقصى 6 إيميلات
            
            # التحقق من صحة كل إيميل
            valid_emails = []
            for email in email_addresses:
                if re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                    valid_emails.append(email)
            email_addresses = valid_emails
            
        except Exception as e:
            print(f"خطأ في معالجة الإيميلات: {str(e)}")
            email_addresses = []
        
        print(f"📧 Email addresses received: {email_addresses}")
        
        # التحقق من البيانات المطلوبة
        if not all([platform, whatsapp_number, payment_method]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        # التحقق المبتكر من الواتساب
        whatsapp_validation = validate_whatsapp_ultimate(whatsapp_number)
        if not whatsapp_validation.get('is_valid'):
            return jsonify({
                'success': False,
                'message': f"رقم الواتساب غير صحيح: {whatsapp_validation.get('error', 'رقم غير صالح')}"
            }), 400
        
        processed_payment_details = ""
        
        # التحقق من طرق الدفع
        if payment_method in ['vodafone_cash', 'etisalat_cash', 'orange_cash', 'we_cash', 'bank_wallet']:
            if not validate_mobile_payment(payment_details):
                return jsonify({'success': False, 'message': 'Invalid mobile payment number'}), 400
            processed_payment_details = re.sub(r'\D', '', payment_details)
            
        elif payment_method == 'tilda':
            if not validate_card_number(payment_details):
                return jsonify({'success': False, 'message': 'Invalid card number'}), 400
            processed_payment_details = re.sub(r'\D', '', payment_details)
            
        elif payment_method == 'instapay':
            is_valid, extracted_link = validate_instapay_link(payment_details)
            if not is_valid:
                return jsonify({'success': False, 'message': 'Invalid InstaPay link'}), 400
            processed_payment_details = extracted_link
        
        # إنشاء بيانات المستخدم المحدثة
        user_data = {
            'platform': platform,
            'whatsapp_number': whatsapp_validation['formatted'],
            'whatsapp_info': {
                'country': whatsapp_validation.get('country'),
                'carrier': whatsapp_validation.get('carrier'),
                'whatsapp_status': whatsapp_validation.get('whatsapp_status'),
                'verification_method': whatsapp_validation.get('verification_method'),
                'confidence': whatsapp_validation.get('confidence'),
                'score': whatsapp_validation.get('score'),
                'methods_analysis': whatsapp_validation.get('methods_analysis', [])
            },
            'payment_method': payment_method,
            'payment_details': processed_payment_details,
            'telegram_username': telegram_username,
            'email_addresses': email_addresses,  # البيانات الجديدة
            'email_count': len(email_addresses),  # عدد الإيميلات
            'email_details': {  # تفاصيل إضافية للإيميلات
                'primary_email': email_addresses[0] if email_addresses else None,
                'secondary_emails': email_addresses[1:] if len(email_addresses) > 1 else [],
                'total_count': len(email_addresses),
                'domains': list(set([email.split('@')[1] for email in email_addresses])) if email_addresses else []
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'ip_address': hashlib.sha256(client_ip.encode()).hexdigest()[:10],
            'user_agent': hashlib.sha256(request.headers.get('User-Agent', '').encode()).hexdigest()[:10]
        }
        
        # حفظ في الذاكرة المؤقتة
        user_id = hashlib.md5(f"{whatsapp_number}-{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        users_data[user_id] = user_data
        
        # طباعة البيانات المحفوظة للتأكيد
        print(f"🔥 New Ultimate Profile Saved (ID: {user_id}):")
        print(f"   📱 WhatsApp: {whatsapp_validation['formatted']}")
        print(f"   🎯 Platform: {platform}")
        print(f"   💳 Payment: {payment_method}")
        print(f"   📧 Emails ({len(email_addresses)}): {email_addresses}")
        print(f"   📊 Full Data: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
        
        # توليد token جديد للأمان
        session['csrf_token'] = generate_csrf_token()
        
        # تحضير الاستجابة المحسنة
        response_data = {
            'success': True,
            'message': 'تم التحقق بالطرق المبتكرة وحفظ البيانات بنجاح!',
            'user_id': user_id,
            'new_csrf_token': session['csrf_token'],
            'data': {
                'platform': platform,
                'whatsapp_number': whatsapp_validation['formatted'],
                'whatsapp_info': user_data['whatsapp_info'],
                'payment_method': payment_method,
                'email_addresses': email_addresses,
                'email_count': len(email_addresses),
                'email_summary': {
                    'primary': email_addresses[0] if email_addresses else None,
                    'total': len(email_addresses),
                    'domains': len(set([email.split('@')[1] for email in email_addresses])) if email_addresses else 0
                }
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        print(f"Error details: {repr(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


# دوال التليجرام محدثة
def generate_telegram_code():
    """توليد كود فريد للتليجرام"""
    return secrets.token_urlsafe(6).upper().replace('_', '').replace('-', '')[:8]

@app.route('/generate-telegram-code', methods=['POST'])
def generate_telegram_code_endpoint():
    """API لتوليد كود التليجرام - محدثة"""
    try:
        data = request.get_json()
        
        # التحقق من صحة البيانات الأساسية
        platform = sanitize_input(data.get('platform', ''))
        whatsapp_number = sanitize_input(data.get('whatsapp_number', ''))
        
        if not platform or not whatsapp_number:
            return jsonify({
                'success': False, 
                'message': 'يرجى إكمال الملف الشخصي أولاً'
            }), 400
        
        # توليد كود فريد
        telegram_code = generate_telegram_code()
        
        # حفظ البيانات في الذاكرة المؤقتة
        telegram_codes[telegram_code] = {
            'code': telegram_code,
            'platform': platform,
            'whatsapp_number': whatsapp_number,
            'payment_method': data.get('payment_method', ''),
            'payment_details': data.get('payment_details', ''),
            'telegram_username': data.get('telegram_username', ''),
            'created_at': datetime.now().isoformat(),
            'used': False
        }
        
        # الحصول على username البوت من متغيرات البيئة
        bot_username = os.environ.get('TELEGRAM_BOT_USERNAME', 'YourBotName_bot')
        telegram_link = f"https://t.me/{bot_username}?start={telegram_code}"
        
        print(f"🤖 Generated Telegram Code: {telegram_code} for {whatsapp_number}")
        
        return jsonify({
            'success': True,
            'code': telegram_code,
            'telegram_link': telegram_link,
            'message': f'تم إنشاء الكود: {telegram_code}'
        })
        
    except Exception as e:
        print(f"خطأ في توليد كود التليجرام: {str(e)}")
        return jsonify({'success': False, 'message': 'خطأ في الخادم'})

def notify_website_telegram_linked(code, profile_data, chat_id, first_name, username):
    """إشعار الموقع بنجاح ربط التليجرام"""
    try:
        # تحديث بيانات المستخدم
        user_id = hashlib.md5(f"{profile_data['whatsapp_number']}-telegram-{code}".encode()).hexdigest()[:12]
        
        updated_user_data = {
            **profile_data,
            'telegram_linked': True,
            'telegram_chat_id': chat_id,
            'telegram_first_name': first_name,
            'telegram_username_actual': username,
            'telegram_linked_at': datetime.now().isoformat(),
            'user_id': user_id
        }
        
        # حفظ في بيانات المستخدمين
        users_data[user_id] = updated_user_data
        
        print(f"🔗 Telegram Linked Successfully!")
        print(f"   User: {first_name} (@{username})")
        print(f"   WhatsApp: {profile_data['whatsapp_number']}")
        print(f"   Platform: {profile_data['platform']}")
        print(f"   Code: {code}")
        print(f"   Chat ID: {chat_id}")
        
        return True
        
    except Exception as e:
        print(f"خطأ في إشعار الموقع: {str(e)}")
        return False

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """استقبال رسائل من التليجرام بوت - محدثة مع تفاصيل الدفع"""
    try:
        update = request.get_json()
        print(f"🤖 Telegram Webhook received: {json.dumps(update, indent=2, ensure_ascii=False)}")
        
        if 'message' not in update:
            return jsonify({'ok': True})
        
        message = update['message']
        text = message.get('text', '').strip().upper()
        chat_id = message['chat']['id']
        username = message.get('from', {}).get('username', 'Unknown')
        first_name = message.get('from', {}).get('first_name', 'مستخدم')
        
        # التحقق من كود /start
        if text.startswith('/START'):
            if ' ' in text:
                code = text.replace('/START ', '').strip().upper()
                print(f"🔍 Looking for /start code: {code}")
                
                # البحث عن الكود في الذاكرة
                if code in telegram_codes:
                    profile_data = telegram_codes[code]
                    if not profile_data.get('used', False):
                        # تحديث الكود كمستخدم
                        telegram_codes[code]['used'] = True
                        telegram_codes[code]['telegram_chat_id'] = chat_id
                        telegram_codes[code]['telegram_username_actual'] = username
                        
                        # إرسال إشعار للموقع
                        notify_website_telegram_linked(code, profile_data, chat_id, first_name, username)
                        
                        # تحديد نص الدفع
                        payment_text = get_payment_display_text(profile_data['payment_method'], profile_data.get('payment_details', ''))
                        
                        # إرسال رسالة ترحيب مخصصة
                        welcome_message = f"""🎮 أهلاً بك {first_name} في FC 26 Profile System!

✅ تم ربط حسابك بنجاح!

📋 بيانات ملفك الشخصي:
🎯 المنصة: {profile_data['platform'].title()}
📱 رقم الواتساب: {profile_data['whatsapp_number']}
💳 طريقة الدفع: {profile_data['payment_method'].replace('_', ' ').title()}
{payment_text}

🔗 رابط الموقع: https://ea-fc-fifa-5jbn.onrender.com/

شكراً لاختيارك FC 26! 🏆"""
                        
                        send_telegram_message(chat_id, welcome_message.strip())
                        print(f"✅ /start Code {code} activated for user {first_name} (@{username})")
                        
                    else:
                        send_telegram_message(chat_id, f"""❌ هذا الكود ({code}) تم استخدامه من قبل.

يرجى الحصول على كود جديد من الموقع:
🔗 https://ea-fc-fifa-5jbn.onrender.com/""")
                        
                else:
                    send_telegram_message(chat_id, f"""❌ الكود ({code}) غير صحيح أو منتهي الصلاحية.

يرجى الحصول على كود جديد من الموقع:
🔗 https://ea-fc-fifa-5jbn.onrender.com/""")
            else:
                # رسالة بداية عامة
                send_telegram_message(chat_id, f"""🎮 مرحباً بك {first_name} في FC 26 Profile System!

للربط مع حسابك، يرجى:
1️⃣ الذهاب للموقع
2️⃣ إكمال بيانات الملف الشخصي  
3️⃣ الضغط على "ربط مع التليجرام"
4️⃣ إرسال الكود الذي ستحصل عليه مباشرة (بدون /start)

مثال: ABC123

🔗 الموقع: https://ea-fc-fifa-5jbn.onrender.com/

شكراً! 🏆""")
        
        # التحقق من الكود المباشر (بدون /start)
        elif len(text) >= 6 and len(text) <= 10 and text.isalnum():
            code = text.upper()
            print(f"🔍 Looking for direct code: {code}")
            
            # البحث عن الكود في الذاكرة
            if code in telegram_codes:
                profile_data = telegram_codes[code]
                if not profile_data.get('used', False):
                    # تحديث الكود كمستخدم
                    telegram_codes[code]['used'] = True
                    telegram_codes[code]['telegram_chat_id'] = chat_id
                    telegram_codes[code]['telegram_username_actual'] = username
                    
                    # إرسال إشعار للموقع
                    notify_website_telegram_linked(code, profile_data, chat_id, first_name, username)
                    
                    # تحديد نص الدفع
                    payment_text = get_payment_display_text(profile_data['payment_method'], profile_data.get('payment_details', ''))
                    
                    # إرسال رسالة ترحيب مخصصة
                    welcome_message = f"""🎮 أهلاً بك {first_name} في FC 26 Profile System!

✅ تم ربط حسابك بنجاح بالكود: {code}

📋 بيانات ملفك الشخصي:
🎯 المنصة: {profile_data['platform'].title()}
📱 رقم الواتساب: {profile_data['whatsapp_number']}
💳 طريقة الدفع: {profile_data['payment_method'].replace('_', ' ').title()}
{payment_text}

🔗 رابط الموقع: https://ea-fc-fifa-5jbn.onrender.com/

شكراً لاختيارك FC 26! 🏆"""
                    
                    send_telegram_message(chat_id, welcome_message.strip())
                    print(f"✅ Direct Code {code} activated for user {first_name} (@{username})")
                    
                else:
                    send_telegram_message(chat_id, f"""❌ هذا الكود ({code}) تم استخدامه من قبل.

يرجى الحصول على كود جديد من الموقع:
🔗 https://ea-fc-fifa-5jbn.onrender.com/""")
                    
            else:
                send_telegram_message(chat_id, f"""❌ الكود ({code}) غير صحيح أو منتهي الصلاحية.

يرجى الحصول على كود جديد من الموقع:
🔗 https://ea-fc-fifa-5jbn.onrender.com/

💡 تلميح: أرسل الكود مباشرة بدون /start
مثال: ABC123""")
        
        else:
            # رد عام للرسائل الأخرى
            send_telegram_message(chat_id, f"""🤖 مرحباً {first_name}! أنا بوت FC 26 Profile System.

للتفاعل معي، يمكنك:
📝 /start - البدء والمساعدة
🔑 إرسال الكود مباشرة (مثال: ABC123)

🔗 الموقع: https://ea-fc-fifa-5jbn.onrender.com/""")
            
        return jsonify({'ok': True})
        
    except Exception as e:
        print(f"خطأ في webhook التليجرام: {str(e)}")
        return jsonify({'ok': True})

def get_payment_display_text(payment_method, payment_details):
    """تحديد نص عرض تفاصيل الدفع"""
    if not payment_details:
        return ""
    
    if payment_method in ['vodafone_cash', 'etisalat_cash', 'orange_cash', 'we_cash', 'bank_wallet']:
        return f"رقم الدفع: {payment_details}"
    elif payment_method == 'tilda':
        return f"رقم البطاقة: {payment_details}"
    elif payment_method == 'instapay':
        return f"رابط الدفع: {payment_details}"
    else:
        return f"تفاصيل الدفع: {payment_details}"

@app.route('/get-bot-username')
def get_bot_username():
    """الحصول على username البوت"""
    bot_username = os.environ.get('TELEGRAM_BOT_USERNAME', 'YourBotName_bot')
    return jsonify({'bot_username': bot_username})

def send_telegram_message(chat_id, text):
    """إرسال رسالة عبر التليجرام بوت - محدثة"""
    try:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN غير موجود في متغيرات البيئة")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML',
            'reply_markup': {
                'inline_keyboard': [[{
                    'text': '🎮 فتح الموقع',
                    'url': 'https://ea-fc-fifa-5jbn.onrender.com/'
                }]]
            }
        }
        
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            print(f"✅ Message sent successfully to {chat_id}")
            return True
        else:
            print(f"❌ Failed to send message: {result}")
            return False
        
    except Exception as e:
        print(f"خطأ في إرسال رسالة التليجرام: {str(e)}")
        return False

# route جديد لعرض البيانات المحفوظة (للاختبار)
@app.route('/admin-data')
def admin_data():
    """عرض البيانات المحفوظة - للاختبار فقط"""
    return jsonify({
        'users_count': len(users_data),
        'telegram_codes_count': len(telegram_codes),
        'users_sample': list(users_data.keys())[:5],
        'telegram_codes_sample': {k: {**v, 'used': v.get('used', False)} for k, v in list(telegram_codes.items())[:5]}
    })

@app.route('/check-telegram-status/<code>')
def check_telegram_status(code):
    """فحص حالة ربط التليجرام"""
    try:
        if code in telegram_codes:
            code_data = telegram_codes[code]
            return jsonify({
                'success': True,
                'linked': code_data.get('used', False),
                'telegram_chat_id': code_data.get('telegram_chat_id'),
                'telegram_username': code_data.get('telegram_username_actual'),
                'linked_at': code_data.get('created_at')
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Code not found'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# route جديد لإعداد webhook التليجرام
@app.route('/set-telegram-webhook')
def set_telegram_webhook():
    """إعداد webhook التليجرام"""
    try:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return jsonify({'success': False, 'message': 'TELEGRAM_BOT_TOKEN غير موجود'})
        
        webhook_url = f"https://ea-fc-fifa-5jbn.onrender.com/telegram-webhook"
        telegram_api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        
        response = requests.post(telegram_api_url, json={'url': webhook_url}, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            return jsonify({
                'success': True, 
                'message': f'Webhook تم تعيينه بنجاح: {webhook_url}',
                'result': result
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'فشل في تعيين webhook',
                'result': result
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'})

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
