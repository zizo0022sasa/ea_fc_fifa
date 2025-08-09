/**
 * 🤖 Telegram Integration Module - FC 26 Profile Setup
 * نظام ربط التليجرام المعزول والمستقل
 * 
 * @version 2.0.0
 * @author FC26 Team
 * @description صندوق أسود لكل ما يخص ربط التليجرام - لا يحتاج تعديلات مستقبلية
 */

// 🔒 متغيرات خاصة بالوحدة (Private Variables)
let isProcessingTelegram = false;
let telegramProcessTimeout = null;
let telegramMonitoringInterval = null;

/**
 * 🚀 الدالة الرئيسية المُصدَّرة - معالجة ربط التليجرام
 * هذه هي النقطة الوحيدة للتفاعل مع النظام الخارجي
 */
export async function handleTelegramLink() {
    console.log('🔍 بدء معالجة زر التليجرام...');
    
    const telegramBtn = document.getElementById('telegram-link-btn');
    if (!telegramBtn) {
        console.error('❌ زر التليجرام غير موجود');
        return;
    }
    
    // التحقق من حالة التحقق (نستورد من النظام الخارجي)
    const validationStates = await getValidationStatesFromMainSystem();
    
    // طباعة حالة التحقق للتشخيص
    console.log('📊 حالة التحقق الحالية:', validationStates);
    
    // ✅ التحقق من اكتمال البيانات
    if (!validationStates.platform || !validationStates.whatsapp) {
        console.log('❌ البيانات غير مكتملة');
        handleIncompleteDataError(telegramBtn);
        return;
    }
    
    console.log('✅ البيانات مكتملة، بدء عملية الربط...');
    
    // منع المعالجة المتكررة
    if (isProcessingTelegram) {
        showTelegramNotification('⏳ جاري المعالجة، يرجى الانتظار...', 'warning');
        return;
    }
    
    isProcessingTelegram = true;
    
    // تحديث الزر لحالة التحميل
    updateTelegramButtonToLoading(telegramBtn);
    
    try {
        // جمع البيانات للإرسال
        const formData = await collectFormDataForTelegram();
        console.log('📤 إرسال البيانات:', {
            platform: formData.platform,
            whatsapp: formData.whatsapp.substring(0, 5) + '***',
            paymentMethod: formData.paymentMethod
        });
        
        // إرسال الطلب للخادم
        const serverResponse = await sendTelegramLinkRequest(formData);
        
        if (serverResponse.success && serverResponse.telegram_web_url) {
            console.log('🔗 نجح الحصول على بيانات التليجرام:', serverResponse);
            
            // فتح التليجرام بالطريقة الذكية
            await openTelegramSmartly(serverResponse);
            
            // عرض الكود للنسخ اليدوي
            displayCopyableCode(telegramBtn, serverResponse);
            
            // بدء مراقبة الربط
            startTelegramLinkingMonitor(serverResponse.telegram_code);
            
            // تحديث الزر للنجاح
            updateTelegramButtonToSuccess(telegramBtn);
            
        } else {
            throw new Error(serverResponse.message || 'خطأ في الخادم');
        }
        
    } catch (error) {
        console.error('❌ خطأ في التليجرام:', error);
        handleTelegramError(telegramBtn, error.message);
        
    } finally {
        // تنظيف حالة المعالجة
        setTimeout(() => {
            isProcessingTelegram = false;
        }, 3000);
    }
}

/**
 * 📋 جمع بيانات النموذج للتليجرام
 */
// ✅✅✅ هذا هو الكود الصحيح بعد التعديل ✅✅✅
async function collectFormDataForTelegram() {
    const platform = document.getElementById('platform')?.value || '';
    const whatsapp = document.getElementById('whatsapp')?.value || '';
    const paymentMethod = document.getElementById('payment_method')?.value || '';
    const paymentDetails = getActivePaymentDetails();
    
    return {
        platform: platform,
        whatsapp: whatsapp, // <--- تم تصحيح الاسم هنا
        payment_method: paymentMethod,
        payment_details: paymentDetails
    };
}


/**
 * 💳 الحصول على تفاصيل الدفع النشطة
 */
function getActivePaymentDetails() {
    const paymentMethod = document.getElementById('payment_method')?.value || '';
    
    if (paymentMethod.includes('cash') || paymentMethod === 'bank_wallet') {
        return document.getElementById('mobile-number')?.value || '';
    } else if (paymentMethod === 'tilda') {
        return document.getElementById('card-number')?.value || '';
    } else if (paymentMethod === 'instapay') {
        return document.getElementById('payment-link')?.value || '';
    }
    
    return '';
}

/**
 * 🌐 إرسال طلب ربط التليجرام للخادم
 */
async function sendTelegramLinkRequest(formData) {
    const response = await fetch('/generate-telegram-code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFTokenFromMainSystem()
        },
        body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
        throw new Error('خطأ في الاتصال بالخادم');
    }
    
    return await response.json();
}

/**
 * 📱 فتح التليجرام بالطريقة الذكية
 */
async function openTelegramSmartly(data) {
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isAndroid = /Android/.test(navigator.userAgent);
    
    console.log('📱 كشف نوع الجهاز:', { isMobile, isIOS, isAndroid });
    
    if (isMobile) {
        // للهواتف: محاولة التطبيق أولاً
        console.log('🚀 محاولة فتح تطبيق التليجرام...');
        
        if (data.telegram_app_url) {
            // إنشاء رابط مخفي للتطبيق
            const appLink = document.createElement('a');
            appLink.href = data.telegram_app_url;
            appLink.style.display = 'none';
            document.body.appendChild(appLink);
            
            // محاولة فتح التطبيق
            appLink.click();
            
            // تنظيف
            setTimeout(() => {
                if (document.body.contains(appLink)) {
                    document.body.removeChild(appLink);
                }
            }, 100);
        }
        
        // خطة بديلة: فتح في المتصفح
        setTimeout(() => {
            console.log('🌐 فتح المتصفح كخطة بديلة...');
            window.open(data.telegram_web_url, '_blank');
        }, 2000);
        
    } else {
        // للكمبيوتر: فتح في المتصفح مباشرة
        console.log('💻 فتح التليجرام في المتصفح...');
        window.open(data.telegram_web_url, '_blank');
    }
    
    // نسخ الكود تلقائياً للطوارئ
    setTimeout(() => {
        copyTelegramCodeToClipboard(data.telegram_code);
    }, 1500);
}

/**
 * 📋 عرض الكود القابل للنسخ
 */
function displayCopyableCode(telegramBtn, data) {
    // إزالة عرض سابق
    const existingCodeDisplay = document.querySelector('.telegram-code-display');
    if (existingCodeDisplay) {
        existingCodeDisplay.remove();
    }
    
    const codeDisplay = document.createElement('div');
    codeDisplay.className = 'telegram-code-display';
    codeDisplay.innerHTML = `
        <div style="background: linear-gradient(135deg, rgba(0, 136, 204, 0.1), rgba(0, 85, 153, 0.15)); 
                    padding: 15px; margin: 15px 0; border-radius: 12px; text-align: center; 
                    border: 2px solid #0088cc; backdrop-filter: blur(10px);">
            <div style="color: #0088cc; font-weight: 700; margin-bottom: 10px;">
                <i class="fas fa-copy"></i> الكود للنسخ اليدوي:
            </div>
            <code style="background: white; padding: 8px 12px; border-radius: 6px; 
                         font-weight: bold; color: #0088cc; font-size: 1.1em; 
                         word-break: break-all; display: inline-block; margin-bottom: 10px;">
                /start ${data.telegram_code}
            </code>
            <div style="font-size: 0.9em; color: rgba(255, 255, 255, 0.8);">
                <small>انسخ هذا النص والصقه في التليجرام إذا لم يظهر تلقائياً</small>
            </div>
            <button onclick="window.copyTelegramCodeManual('/start ${data.telegram_code}')" 
                    style="background: #0088cc; color: white; border: none; padding: 8px 16px; 
                           border-radius: 6px; margin-top: 10px; cursor: pointer; font-weight: 600;">
                📋 نسخ الكود
            </button>
        </div>
    `;
    
    // إدراج عنصر الكود بعد الزر مباشرة
    telegramBtn.parentNode.insertBefore(codeDisplay, telegramBtn.nextSibling);
    
    // إزالة تلقائية بعد 10 ثوان
    setTimeout(() => {
        if (codeDisplay && codeDisplay.parentNode) {
            codeDisplay.style.opacity = '0';
            setTimeout(() => {
                if (codeDisplay.parentNode) {
                    codeDisplay.remove();
                }
            }, 500);
        }
    }, 10000);
}

/**
 * 📋 نسخ كود التليجرام للحافظة
 */
function copyTelegramCodeToClipboard(code) {
    const fullCode = `/start ${code}`;
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(fullCode).then(() => {
            console.log('📋 تم نسخ الكود للحافظة:', fullCode);
            showTelegramNotification('تم نسخ الكود للحافظة! الصقه في التليجرام', 'success');
        }).catch(err => {
            console.warn('❌ فشل في نسخ الكود:', err);
            fallbackCopyToClipboard(fullCode);
        });
    } else {
        fallbackCopyToClipboard(fullCode);
    }
}

/**
 * 📋 طريقة بديلة للنسخ
 */
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showTelegramNotification('تم نسخ الكود بالطريقة البديلة!', 'success');
        }
    } catch (err) {
        console.error('فشل في النسخ:', err);
    }
    
    document.body.removeChild(textArea);
}

/**
 * 👁️ بدء مراقبة ربط التليجرام
 */
function startTelegramLinkingMonitor(telegramCode) {
    // إيقاف أي مراقبة سابقة
    if (telegramMonitoringInterval) {
        clearInterval(telegramMonitoringInterval);
    }
    
    console.log('🔍 بدء مراقبة ربط التليجرام للكود:', telegramCode);
    
    telegramMonitoringInterval = setInterval(async () => {
        try {
            const checkResponse = await fetch(`/check-telegram-status/${telegramCode}`);
            const checkResult = await checkResponse.json();
            
            if (checkResult.success && checkResult.linked) {
                // نجح الربط!
                clearInterval(telegramMonitoringInterval);
                telegramMonitoringInterval = null;
                
                console.log('✅ تم ربط التليجرام بنجاح!');
                showTelegramNotification('✅ تم ربط التليجرام بنجاح!', 'success');
                
                // الانتقال التلقائي بعد ثانية
                setTimeout(() => {
                    window.location.href = '/coins-order';
                }, 1000);
            }
        } catch (error) {
            console.error('خطأ في فحص الربط:', error);
        }
    }, 3000);
    
    // إيقاف المراقبة بعد دقيقة
    setTimeout(() => {
        if (telegramMonitoringInterval) {
            clearInterval(telegramMonitoringInterval);
            telegramMonitoringInterval = null;
            console.log('⏰ انتهى وقت مراقبة ربط التليجرام');
        }
    }, 60000);
}

/**
 * ⚠️ معالجة خطأ البيانات غير المكتملة
 */
function handleIncompleteDataError(telegramBtn) {
    const originalContent = telegramBtn.innerHTML;
    
    telegramBtn.innerHTML = `
        <div class="telegram-btn-content">
            <i class="fas fa-exclamation-circle telegram-icon" style="color: #ff4444;"></i>
            <div class="telegram-text">
                <span class="telegram-title">❌ خطأ - اضغط للمحاولة مرة أخرى</span>
                <span class="telegram-subtitle">يرجى اختيار المنصة والتحقق من رقم الواتساب أولاً</span>
            </div>
        </div>
    `;
    telegramBtn.classList.add('error');
    
    // إظهار رسالة خطأ
    showTelegramNotification('يرجى اختيار المنصة والتحقق من رقم الواتساب أولاً', 'error');
    
    // إعادة النص الأصلي بعد 3 ثوان
    setTimeout(() => {
        telegramBtn.innerHTML = originalContent;
        telegramBtn.classList.remove('error');
    }, 3000);
}

/**
 * ⏳ تحديث الزر لحالة التحميل
 */
function updateTelegramButtonToLoading(telegramBtn) {
    telegramBtn.disabled = true;
    telegramBtn.innerHTML = `
        <div class="telegram-btn-content">
            <i class="fas fa-spinner fa-spin telegram-icon"></i>
            <div class="telegram-text">
                <span class="telegram-title">⏳ جاري التحضير...</span>
                <span class="telegram-subtitle">يرجى الانتظار...</span>
            </div>
        </div>
    `;
    telegramBtn.classList.add('generating');
}

/**
 * ✅ تحديث الزر لحالة النجاح
 */
function updateTelegramButtonToSuccess(telegramBtn) {
    telegramBtn.innerHTML = `
        <div class="telegram-btn-content">
            <i class="fas fa-check-circle telegram-icon" style="color: #00d084;"></i>
            <div class="telegram-text">
                <span class="telegram-title">✅ تم فتح التليجرام</span>
                <span class="telegram-subtitle">أدخل للبوت واضغط /start</span>
            </div>
        </div>
    `;
    telegramBtn.classList.remove('generating');
    telegramBtn.classList.add('success');
    
    // إعادة الزر للوضع الطبيعي بعد 5 ثوان
    setTimeout(() => {
        const originalContent = `
            <div class="telegram-btn-content">
                <i class="fab fa-telegram telegram-icon"></i>
                <div class="telegram-text">
                    <span class="telegram-title">📱 ربط مع التليجرام</span>
                    <span class="telegram-subtitle">احصل على كود فوري وادخل للبوت</span>
                </div>
            </div>
        `;
        telegramBtn.innerHTML = originalContent;
        telegramBtn.classList.remove('success');
        telegramBtn.disabled = false;
    }, 5000);
}

/**
 * ❌ معالجة خطأ التليجرام
 */
function handleTelegramError(telegramBtn, errorMessage) {
    const originalContent = telegramBtn.innerHTML;
    
    telegramBtn.innerHTML = `
        <div class="telegram-btn-content">
            <i class="fas fa-exclamation-triangle telegram-icon" style="color: #ff9000;"></i>
            <div class="telegram-text">
                <span class="telegram-title">❌ خطأ - اضغط للمحاولة مرة أخرى</span>
                <span class="telegram-subtitle">${errorMessage}</span>
            </div>
        </div>
    `;
    telegramBtn.classList.remove('generating');
    telegramBtn.classList.add('error');
    
    showTelegramNotification('خطأ في الاتصال، يرجى المحاولة مرة أخرى', 'error');
    
    // إعادة الزر للوضع الطبيعي بعد 3 ثوان
    setTimeout(() => {
        telegramBtn.innerHTML = originalContent;
        telegramBtn.classList.remove('error');
        telegramBtn.disabled = false;
    }, 3000);
}

/**
 * 📢 إظهار إشعار خاص بالتليجرام
 */
function showTelegramNotification(message, type = 'info') {
    // نستخدم النظام الموجود من الملف الرئيسي
    if (typeof showNotification === 'function') {
        showNotification(message, type);
    } else {
        // إشعار بسيط كبديل
        console.log(`🔔 ${type.toUpperCase()}: ${message}`);
        alert(message);
    }
}

/**
 * 🔗 الحصول على حالات التحقق من النظام الرئيسي
 */
async function getValidationStatesFromMainSystem() {
    // نحاول الوصول للمتغيرات العامة
    if (typeof validationStates !== 'undefined') {
        return validationStates;
    }
    
    // إذا لم توجد، نفحص البيانات يدوياً
    const platform = document.getElementById('platform')?.value || '';
    const whatsapp = document.getElementById('whatsapp')?.value || '';
    const phoneInfo = document.querySelector('.phone-info.success-info');
    const paymentMethod = document.getElementById('payment_method')?.value || '';
    
    return {
        platform: !!platform,
        whatsapp: !!(whatsapp && phoneInfo),
        paymentMethod: !!paymentMethod
    };
}

/**
 * 🔒 الحصول على CSRF token من النظام الرئيسي
 */
function getCSRFTokenFromMainSystem() {
    // نحاول استخدام الدالة الموجودة
    if (typeof getCSRFToken === 'function') {
        return getCSRFToken();
    }
    
    // محاولة بديلة
    const token = document.querySelector('meta[name="csrf-token"]') || 
                  document.querySelector('input[name="csrfmiddlewaretoken"]');
    return token ? (token.getAttribute('content') || token.value) : '';
}

/**
 * 🌐 دالة عامة للنسخ اليدوي (للاستخدام مع HTML)
 * هذه الدالة تُعرَّض للنظام العالمي
 */
window.copyTelegramCodeManual = function(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showTelegramNotification('تم النسخ بنجاح!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
};

/**
 * 🔧 دالة التهيئة للوحدة (يتم استدعاؤها من الملف الرئيسي)
 */
export function initializeTelegramModule() {
    console.log('🤖 تم تهيئة وحدة التليجرام المستقلة');
    
    // إعداد زر التليجرام
    const telegramBtn = document.getElementById('telegram-link-btn');
    if (telegramBtn) {
        // إزالة مستمعين قدامى
        const newBtn = telegramBtn.cloneNode(true);
        telegramBtn.parentNode.replaceChild(newBtn, telegramBtn);
        
        // إضافة المستمع الجديد
        newBtn.addEventListener('click', handleTelegramLink);
        console.log('✅ تم ربط زر التليجرام بالوحدة الجديدة');
    } else {
        console.warn('⚠️ زر التليجرام غير موجود');
    }
    
    // تنظيف أي مراقبة سابقة عند إعادة التهيئة
    if (telegramMonitoringInterval) {
        clearInterval(telegramMonitoringInterval);
        telegramMonitoringInterval = null;
    }
}

// 📝 تسجيل تحميل الوحدة
console.log('📦 Telegram Integration Module v2.0.0 - تم التحميل بنجاح');
console.log('🔒 الوحدة معزولة تماماً ولا تحتاج تعديلات مستقبلية');
