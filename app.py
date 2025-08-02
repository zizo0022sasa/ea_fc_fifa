from flask import Flask, render_template, request, jsonify
import requests
import re
import json
import time
import random

app = Flask(__name__)

def validate_egyptian_number(number):
    """التحقق من صحة الرقم المصري"""
    clean_number = re.sub(r'[^\d+]', '', number)
    
    egyptian_patterns = [
        r'^(\+20|0020|20)?0?(10|11|12|15)\d{8}$'
    ]
    
    for pattern in egyptian_patterns:
        if re.match(pattern, clean_number):
            if clean_number.startswith('+20'):
                return clean_number
            elif clean_number.startswith('0020'):
                return '+' + clean_number[2:]
            elif clean_number.startswith('20'):
                return '+' + clean_number
            elif clean_number.startswith('0'):
                return '+20' + clean_number[1:]
            else:
                return '+20' + clean_number
    
    return None

def check_whatsapp_exists(phone_number):
    """فحص حقيقي لوجود رقم الواتساب بدون Selenium"""
    try:
        clean_number = phone_number.replace('+', '').replace(' ', '')
        
        # قائمة User Agents مختلفة
        user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        session = requests.Session()
        
        # طريقة 1: فحص wa.me مع تحليل الاستجابة
        try:
            headers = {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            wa_url = f"https://wa.me/{clean_number}?text=test"
            response = session.get(wa_url, headers=headers, timeout=8, allow_redirects=False)
            
            # فحص الـ redirect و response
            if response.status_code in [200, 302, 301]:
                # إذا في redirect لـ WhatsApp Web يبقى الرقم موجود
                if 'Location' in response.headers:
                    location = response.headers['Location'].lower()
                    if 'web.whatsapp.com' in location or 'whatsapp://' in location:
                        return True, "الرقم موجود على الواتساب"
                
                # فحص محتوى الصفحة
                content = response.text.lower()
                
                # علامات تدل على وجود الرقم
                if any(word in content for word in ['whatsapp', 'continue to chat', 'message', 'chat']):
                    # فحص إضافي للتأكد
                    if not any(error in content for error in [
                        'phone number shared via url is invalid',
                        'invalid phone number',
                        'not found',
                        'error'
                    ]):
                        return True, "الرقم موجود على الواتساب"
            
        except Exception as e:
            pass
        
        # طريقة 2: فحص عبر WhatsApp API غير المباشر
        try:
            api_headers = {
                'User-Agent': random.choice(user_agents),
                'Referer': 'https://web.whatsapp.com/',
                'Origin': 'https://web.whatsapp.com'
            }
            
            # محاولة الوصول لـ WhatsApp Web
            check_url = f"https://web.whatsapp.com/send?phone={clean_number}&text=hello"
            response = session.head(check_url, headers=api_headers, timeout=5)
            
            if response.status_code == 200:
                return True, "الرقم موجود على الواتساب"
                
        except:
            pass
        
        # طريقة 3: فحص عبر خدمات خارجية مجانية
        try:
            # استخدام خدمة مجانية للفحص
            external_apis = [
                f"https://api.whatsapp.com/send?phone={clean_number}",
                f"https://wa.me/{clean_number}",
            ]
            
            for api_url in external_apis:
                try:
                    response = session.head(api_url, timeout=3)
                    if response.status_code == 200:
                        # فحص إضافي بـ GET request
                        get_response = session.get(api_url, timeout=3)
                        content = get_response.text.lower()
                        
                        # إذا مفيش أخطاء يبقى الرقم موجود غالباً
                        if not any(error in content for error in [
                            'invalid', 'error', 'not found', 'doesn\'t exist'
                        ]):
                            return True, "الرقم موجود على الواتساب"
                except:
                    continue
                    
        except:
            pass
        
        # إذا وصلنا هنا يبقى مش متأكدين
        return False, "لا يمكن التأكد من وجود الرقم أو الرقم غير موجود"
        
    except Exception as e:
        return False, f"خطأ في الفحص: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_number():
    phone_number = request.json.get('phone_number', '')
    
    if not phone_number:
        return jsonify({
            'success': False,
            'message': 'من فضلك أدخل رقم الهاتف'
        })
    
    # التحقق من صحة الرقم المصري
    formatted_number = validate_egyptian_number(phone_number)
    
    if not formatted_number:
        return jsonify({
            'success': False,
            'message': 'الرقم غير صحيح أو ليس مصري'
        })
    
    # التحقق من وجود الرقم على الواتساب
    exists, message = check_whatsapp_exists(formatted_number)
    
    return jsonify({
        'success': True,
        'phone_number': formatted_number,
        'exists': exists,
        'message': message,
        'whatsapp_link': f"https://wa.me/{formatted_number.replace('+', '')}" if exists else None
    })

if __name__ == '__main__':
    app.run(debug=True)
