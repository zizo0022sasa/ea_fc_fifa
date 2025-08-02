from flask import Flask, render_template, request, jsonify
import requests
import re

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
    """التحقق من وجود رقم الواتساب"""
    try:
        # استخدام WhatsApp Business API للتحقق
        # ملحوظة: ده مثال - محتاج token حقيقي
        url = f"https://graph.facebook.com/v17.0/{phone_number}"
        
        # طريقة بديلة - فحص بسيط
        # في الواقع محتاج WhatsApp Business API مع access token
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # محاكاة الفحص (في التطبيق الحقيقي محتاج API صحيح)
        # هنا هنعمل فحص بسيط على صيغة الرقم
        if phone_number and len(phone_number) >= 10:
            return True, "الرقم صحيح ومن المحتمل أنه موجود"
        else:
            return False, "الرقم غير صحيح"
            
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
        'message': message
    })

if __name__ == '__main__':
    app.run(debug=True)
