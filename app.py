from flask import Flask, render_template, request, jsonify
import re
import requests
import time

app = Flask(__name__)

def validate_egyptian_number(phone_number):
    clean_number = re.sub(r'[\s\-\(\)]', '', phone_number)
    
    egyptian_patterns = [
        r'^010\d{8}$',
        r'^011\d{8}$', 
        r'^012\d{8}$',
        r'^015\d{8}$'
    ]
    
    for pattern in egyptian_patterns:
        if re.match(pattern, clean_number):
            return True, f"20{clean_number}"
    
    return False, None

def check_whatsapp_number(formatted_number):
    try:
        # استخدام WhatsApp Web API للتحقق
        url = f"https://web.whatsapp.com/send?phone={formatted_number}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # إذا الرقم موجود على الواتساب، الصفحة هترجع status 200
        if response.status_code == 200:
            return True
        else:
            return False
            
    except:
        # في حالة حدوث خطأ في الاتصال
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_whatsapp', methods=['POST'])
def check_whatsapp():
    phone_number = request.form.get('phone_number', '').strip()
    
    if not phone_number:
        return jsonify({
            'success': False, 
            'message': 'من فضلك أدخل رقم الهاتف'
        })
    
    # التحقق من أن الرقم مصري
    is_valid, formatted_number = validate_egyptian_number(phone_number)
    
    if not is_valid:
        return jsonify({
            'success': False,
            'message': 'الرقم مش مصري أو غير صحيح'
        })
    
    # التحقق من وجود الرقم على الواتساب
    whatsapp_status = check_whatsapp_number(formatted_number)
    
    if whatsapp_status is True:
        return jsonify({
            'success': True,
            'message': '✅ الرقم موجود على الواتساب',
            'phone_number': f"+{formatted_number}",
            'whatsapp_link': f"https://wa.me/{formatted_number}"
        })
    elif whatsapp_status is False:
        return jsonify({
            'success': False,
            'message': '❌ الرقم مش موجود على الواتساب',
            'phone_number': f"+{formatted_number}"
        })
    else:
        return jsonify({
            'success': False,
            'message': '⚠️ مش قادر أتحقق من الرقم دلوقتي، حاول تاني',
            'phone_number': f"+{formatted_number}"
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
