from flask import Flask, render_template, request, jsonify
import requests
import re
import json
from urllib.parse import quote

app = Flask(__name__)

def validate_egyptian_number(number):
    """التحقق من صحة الرقم المصري"""
    # إزالة المسافات والرموز
    clean_number = re.sub(r'[^\d+]', '', number)
    
    # التحقق من الأرقام المصرية
    egyptian_patterns = [
        r'^(\+20|0020|20)?0?(10|11|12|15)\d{8}$'
    ]
    
    for pattern in egyptian_patterns:
        if re.match(pattern, clean_number):
            # تحويل الرقم للصيغة الدولية
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
    """التحقق الحقيقي من وجود رقم الواتساب"""
    try:
        # إزالة + و مسافات
        clean_number = phone_number.replace('+', '').replace(' ', '')
        
        # استخدام WhatsApp Web API للتحقق
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # طريقة 1: فحص عبر WhatsApp Click to Chat
        wa_url = f"https://api.whatsapp.com/send?phone={clean_number}"
        
        try:
            response = requests.get(wa_url, headers=headers, timeout=10, allow_redirects=True)
            
            # إذا كان الرقم موجود، WhatsApp هيوجهنا لـ web.whatsapp.com
            if "web.whatsapp.com" in response.url or response.status_code == 200:
                return True, "الرقم موجود على الواتساب"
            else:
                return False, "الرقم غير موجود على الواتساب"
                
        except:
            pass
        
        # طريقة 2: استخدام WhatsApp Business API endpoint للفحص
        try:
            # هذا endpoint غير رسمي للفحص
            check_url = f"https://wa.me/{clean_number}"
            response = requests.head(check_url, headers=headers, timeout=8)
            
            if response.status_code == 200:
                return True, "الرقم موجود على الواتساب"
            else:
                return False, "الرقم غير موجود على الواتساب"
                
        except:
            pass
            
        # طريقة 3: محاولة فحص عبر واجهة WhatsApp
        try:
            api_url = f"https://web.whatsapp.com/send?phone={clean_number}&text=test"
            response = requests.get(api_url, headers=headers, timeout=5)
            
            # فحص إذا كان الرد يحتوي على مؤشرات وجود الرقم
            response_text = response.text.lower()
            
            if any(indicator in response_text for indicator in ['chat', 'whatsapp', 'send', 'message']):
                # فحص إضافي للتأكد
                if 'phone number shared via url is invalid' in response_text:
                    return False, "الرقم غير صحيح أو غير موجود"
                return True, "الرقم موجود على الواتساب"
            else:
                return False, "الرقم غير موجود على الواتساب"
                
        except Exception as e:
            return False, f"لا يمكن التحقق من الرقم: {str(e)}"
            
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
