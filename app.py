from flask import Flask, render_template, request, jsonify
import requests
import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def check_whatsapp_with_selenium(phone_number):
    """فحص باستخدام Selenium (طريقة مجانية وحقيقية)"""
    try:
        clean_number = phone_number.replace('+', '')
        
        # إعداد Chrome بدون واجهة
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # الذهاب لـ WhatsApp Web
            wa_url = f"https://web.whatsapp.com/send?phone={clean_number}&text=test"
            driver.get(wa_url)
            
            # انتظار التحميل
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)  # انتظار إضافي
            
            # فحص العناصر في الصفحة
            page_source = driver.page_source.lower()
            
            # علامات تدل على وجود الرقم
            positive_indicators = [
                'chat',
                'conversation',
                'message',
                'send',
                'whatsapp web'
            ]
            
            # علامات تدل على عدم وجود الرقم
            negative_indicators = [
                'phone number shared via url is invalid',
                'number does not exist',
                'invalid phone number',
                'doesn\'t have whatsapp',
                'not on whatsapp'
            ]
            
            # فحص العلامات السلبية أولاً
            for indicator in negative_indicators:
                if indicator in page_source:
                    return False, "الرقم غير موجود على الواتساب"
            
            # فحص العلامات الإيجابية
            positive_count = sum(1 for indicator in positive_indicators if indicator in page_source)
            
            if positive_count >= 2:
                return True, "الرقم موجود على الواتساب"
            else:
                return False, "لا يمكن التأكد من وجود الرقم"
                
        finally:
            driver.quit()
            
    except Exception as e:
        return False, f"خطأ في الفحص: {str(e)}"

def check_whatsapp_simple(phone_number):
    """طريقة بسيطة بدون Selenium"""
    try:
        clean_number = phone_number.replace('+', '')
        
        # قائمة User Agents عشوائية
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # محاولة الوصول لـ wa.me
        wa_url = f"https://wa.me/{clean_number}"
        
        session = requests.Session()
        response = session.get(wa_url, headers=headers, timeout=10, allow_redirects=True)
        
        # فحص الـ response
        if response.status_code == 200:
            content = response.text.lower()
            
            # فحص وجود مؤشرات سلبية
            if any(indicator in content for indicator in [
                'phone number shared via url is invalid',
                'the phone number is not valid',
                'invalid phone number',
                'this phone number is not on whatsapp'
            ]):
                return False, "الرقم غير موجود على الواتساب"
            
            # فحص وجود مؤشرات إيجابية
            if any(indicator in content for indicator in [
                'whatsapp',
                'chat',
                'message',
                'continue to chat'
            ]):
                return True, "الرقم موجود على الواتساب"
        
        # طريقة إضافية: فحص Truecaller API (مجاني جزئياً)
        try:
            truecaller_url = f"https://www.truecaller.com/search/eg/{clean_number}"
            tc_response = session.get(truecaller_url, headers=headers, timeout=8)
            
            if tc_response.status_code == 200:
                tc_content = tc_response.text.lower()
                if 'whatsapp' in tc_content:
                    return True, "الرقم موجود على الواتساب (تأكيد من Truecaller)"
        except:
            pass
            
        return False, "لا يمكن التأكد من وجود الرقم"
        
    except Exception as e:
        return False, f"خطأ في الفحص: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_number():
    phone_number = request.json.get('phone_number', '')
    method = request.json.get('method', 'simple')  # simple أو selenium
    
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
    
    # اختيار طريقة الفحص
    if method == 'selenium':
        exists, message = check_whatsapp_with_selenium(formatted_number)
    else:
        exists, message = check_whatsapp_simple(formatted_number)
    
    return jsonify({
        'success': True,
        'phone_number': formatted_number,
        'exists': exists,
        'message': message,
        'whatsapp_link': f"https://wa.me/{formatted_number.replace('+', '')}" if exists else None
    })

if __name__ == '__main__':
    app.run(debug=True)
