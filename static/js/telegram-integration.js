/**
 * 🤖 Telegram Integration Module - FC 26 Profile Setup
 * نظام ربط التليجرام المعزول والمستقل
 * 
 * @version 2.3.0 - CRITICAL CODE NAME FIX
 * @author FC26 Team
 * @description إصلاح مشكلة undefined - تغيير telegram_code إلى code
 */

// 🔒 متغيرات خاصة بالوحدة (Private Variables)
let isProcessingTelegram = false;
let telegramProcessTimeout = null;
let telegramMonitoringInterval = null;

/**
 * 🔗 الحصول على  حالات التحقق من النظام الرئيسي - محسّنة
 */
async function getValidationStatesFromMainSystem() {
    console.log('🔍 Starting enhanced validation check...');
    
    // محاولة الوصول للمتغيرات العامة من النافذة الرئيسية
    if (typeof window.validationStates !== 'undefined') {
        console.log('✅ Found validationStates in window:', window.validationStates);
        return window.validationStates;
    }
    
    // محاولة الوصول عبر الـ parent window
    if (window.parent && typeof window.parent.validationStates !== 'undefined') {
        console.log('✅ Found validationStates in parent:', window.parent.validationStates);
        return window.parent.validationStates;
    }
    
    // فحص يدوي مفصل للبيانات
    console.log('🔍 Manual validation check starting...');
    
    const platform = document.getElementById('platform')?.value || '';
    const whatsapp = document.getElementById('whatsapp')?.value || '';
    const phoneInfo = document.querySelector('.phone-info.success-info');
    const paymentMethod = document.getElementById('payment_method')?.value || '';
    
    console.log('📋 Raw data found:', {
        platform: platform || 'EMPTY',
        whatsapp: whatsapp ? whatsapp.substring(0, 5) + '***' : 'EMPTY',
        phoneInfoExists: !!phoneInfo,
        paymentMethod: paymentMethod || 'EMPTY'
    });
    
    // تحديد الحقل النشط للدفع
    let hasValidPaymentDetails = false;
    let activePaymentField = 'none';
    
    if (paymentMethod) {
        // فحص حقل الموبايل للمحافظ
        const mobileField = document.getElementById('mobile-number');
        if (mobileField && mobileField.closest('.dynamic-input').style.display !== 'none') {
            const mobileValue = mobileField.value.trim();
            hasValidPaymentDetails = /^01[0125][0-9]{8}$/.test(mobileValue);
            activePaymentField = 'mobile';
            console.log('📱 Mobile payment check:', {
                value: mobileValue,
                isValid: hasValidPaymentDetails,
                pattern: '/^01[0125][0-9]{8}$/'
            });
        }
        
        // فحص حقل الكارت لتيلدا
        const cardField = document.getElementById('card-number');
        if (cardField && cardField.closest('.dynamic-input').style.display !== 'none') {
            const cardValue = cardField.value.replace(/[-\s]/g, '');
            hasValidPaymentDetails = /^\d{16}$/.test(cardValue);
            activePaymentField = 'card';
            console.log('💳 Card payment check:', {
                value: cardValue ? cardValue.substring(0, 4) + '***' : 'EMPTY',
                isValid: hasValidPaymentDetails,
                length: cardValue.length
            });
        }
        
        // فحص حقل الرابط لإنستاباي
        const linkField = document.getElementById('payment-link');
        if (linkField && linkField.closest('.dynamic-input').style.display !== 'none') {
            const linkValue = linkField.value.trim();
            hasValidPaymentDetails = linkValue.includes('instapay') || linkValue.includes('ipn.eg');
            activePaymentField = 'link';
            console.log('🔗 Link payment check:', {
                hasInstapay: linkValue.includes('instapay'),
                hasIpn: linkValue.includes('ipn.eg'),
                isValid: hasValidPaymentDetails
            });
        }
    }
    
    const validationStates = {
        platform: !!platform,
        whatsapp: !!(whatsapp && phoneInfo),
        paymentMethod: !!(paymentMethod && hasValidPaymentDetails)
    };
    
    console.log('🎯 Final validation results:', validationStates);
    console.log('📊 Validation details:', {
        platform: {
            value: platform,
            isValid: validationStates.platform
        },
        whatsapp: {
            hasValue: !!whatsapp,
            hasValidation: !!phoneInfo,
            isValid: validationStates.whatsapp
        },
        payment: {
            method: paymentMethod,
            activeField: activePaymentField,
            hasDetails: hasValidPaymentDetails,
            isValid: validationStates.paymentMethod
        }
    });
    
    return validationStates;
}

/**
 * 🚀 الدالة الرئيسية المُصدَّرة - معالجة ربط التليجرام - الإصدار النهائي
 */
export async function handleTelegramLink() {
    console.log('🔍 🔥 FINAL VERSION: بدء معالجة زر التليجرام - CODE NAME FIX...');
    
    const telegramBtn = document.getElementById('telegram-link-btn');
    if (!telegramBtn) {
        console.error('❌ زر التليجرام غير موجود - ID: telegram-link-btn');
        return;
    }
    
    console.log('✅ تم العثور على زر التليجرام');
    
    // منع المعالجة المتكررة
    if (isProcessingTelegram) {
        console.log('⏳ المعالجة جارية بالفعل - تجاهل النقر المتكرر');
        showTelegramNotification('⏳ جاري المعالجة، يرجى الانتظار...', 'warning');
        return;
    }
    
    isProcessingTelegram = true;
    console.log('🔒 تم قفل المعالجة لمنع التكرار');
    
    // تحديث الزر لحالة التحميل
    updateTelegramButtonToLoading(telegramBtn);
    
    try {
        // التحقق من حالة التحقق مع تشخيص مفصل
        console.log('🔍 Getting validation states...');
        const validationStates = await getValidationStatesFromMainSystem();
        
        // ✅ التحقق من اكتمال البيانات مع رسائل واضحة
        if (!validationStates.platform) {
            console.log('❌ فشل التحقق: المنصة غير مختارة');
            handleIncompleteDataError(telegramBtn, 'يرجى اختيار منصة اللعب أولاً');
            return;
        }
        
        if (!validationStates.whatsapp) {
            console.log('❌ فشل التحقق: الواتساب غير صحيح أو غير متحقق منه');
            handleIncompleteDataError(telegramBtn, 'يرجى إدخال رقم واتساب صحيح والتأكد من التحقق منه');
            return;
        }
        
        if (!validationStates.paymentMethod) {
            console.log('❌ فشل التحقق: طريقة الدفع غير صحيحة أو غير مكتملة');
            handleIncompleteDataError(telegramBtn, 'يرجى اختيار طريقة دفع وإدخال البيانات المطلوبة');
            return;
        }
        
        console.log('✅ جميع البيانات مكتملة، بدء عملية الربط...');
        
        // جمع البيانات للإرسال - ENHANCED VERSION
        const formData = await collectFormDataForTelegram();
        console.log('📤 🔥 CRITICAL: البيانات النهائية للإرسال:', {
            platform: formData.platform,
            whatsapp_number: formData.whatsapp_number ? formData.whatsapp_number.substring(0, 5) + '***' : 'MISSING',
            payment_method: formData.payment_method,
            has_payment_details: !!formData.payment_details
        });
        
        // إرسال الطلب للخادم - ENHANCED VERSION
        console.log('🌐 🔥 CRITICAL: إرسال طلب للخادم مع بيانات كاملة...');
        const serverResponse = await sendTelegramLinkRequest(formData);
        
        // 🚨 فحص حاسم للاستجابة - FIXED: البحث عن code بدلاً من telegram_code
        console.log('🔥 CRITICAL SERVER RESPONSE CHECK:', {
            success: serverResponse.success,
            hasCode: !!serverResponse.code,  // ✅ تم تغيير من telegram_code إلى code
            codeValue: serverResponse.code || 'UNDEFINED/NULL',  // ✅ تم تغيير
            codeType: typeof serverResponse.code,  // ✅ تم تغيير
            hasWebUrl: !!serverResponse.telegram_web_url,
            hasAppUrl: !!serverResponse.telegram_app_url,
            fullResponse: serverResponse
        });
        
        if (serverResponse.success && serverResponse.code) {  // ✅ تم تغيير من telegram_code إلى code
            console.log('✅ SUCCESS: تم الحصول على كود التليجرام بنجاح:', serverResponse.code.substring(0, 10) + '...');
            
            // فتح التليجرام بالطريقة الذكية
            await openTelegramSmartly(serverResponse);
            
            // عرض الكود للنسخ اليدوي
            displayCopyableCode(telegramBtn, serverResponse);
            
            // بدء مراقبة الربط
            startTelegramLinkingMonitor(serverResponse.code);  // ✅ تم تغيير
            
            // تحديث الزر للنجاح
            updateTelegramButtonToSuccess(telegramBtn);
            
        } else if (serverResponse.success && !serverResponse.code) {  // ✅ تم تغيير
            console.error('🚨 CRITICAL ERROR: Server returned success=true but code is missing!');
            console.error('🚨 Full server response:', JSON.stringify(serverResponse, null, 2));
            throw new Error('الخادم لم ينشئ كود التليجرام رغم نجاح العملية');
        } else {
            console.error('❌ Server returned failure:', serverResponse);
            throw new Error(serverResponse.message || 'خطأ في الخادم');
        }
        
    } catch (error) {
        console.error('❌ 🔥 CRITICAL ERROR in handleTelegramLink:', error);
        console.error('❌ Error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        handleTelegramError(telegramBtn, error.message);
        
    } finally {
        // تنظيف حالة المعالجة
        setTimeout(() => {
            isProcessingTelegram = false;
            console.log('🔓 تم إلغاء قفل المعالجة');
        }, 3000);
    }
}

/**
 * 📋 جمع بيانات النموذج للتليجرام - ENHANCED VERSION للتطابق الكامل
 */
async function collectFormDataForTelegram() {
    console.log('📋 🔥 ENHANCED: جمع بيانات النموذج مع التطابق الكامل...');
    
    const platform = document.getElementById('platform')?.value || '';
    const whatsapp = document.getElementById('whatsapp')?.value || '';
    const paymentMethod = document.getElementById('payment_method')?.value || '';
    const paymentDetails = getActivePaymentDetails();
    
    // 🔥 التطابق الكامل مع ما يتوقعه الخادم في app.py
    const formData = {
        platform: platform,
        whatsapp_number: whatsapp,        // ✅ يطابق data.get('whatsapp_number')
        payment_method: paymentMethod,    // ✅ يطابق data.get('payment_method')  
        payment_details: paymentDetails,  // ✅ يطابق data.get('payment_details')
        telegram_username: ''             // ✅ إضافة إضافية للتوافق
    };
    
    // 🔍 تشخيص مفصل للبيانات المرسلة
    console.log('📋 🔥 CRITICAL - البيانات المرسلة للخادم:', {
        platform: formData.platform || 'MISSING ❌',
        whatsapp_number: formData.whatsapp_number ? 
            formData.whatsapp_number.substring(0, 5) + '***' : 'MISSING ❌',
        payment_method: formData.payment_method || 'MISSING ❌',
        payment_details: formData.payment_details || 'MISSING ❌',
        telegram_username: formData.telegram_username || 'EMPTY (OK)',
        dataIntegrity: 'CHECKING...'
    });
    
    // 🚨 تحقق نهائي قبل الإرسال - منع إرسال بيانات ناقصة
    const validationErrors = [];
    
    if (!formData.platform) {
        validationErrors.push('Platform is missing');
    }
    if (!formData.whatsapp_number) {
        validationErrors.push('WhatsApp number is missing');
    }
    if (!formData.payment_method) {
        validationErrors.push('Payment method is missing');
    }
    if (!formData.payment_details) {
        validationErrors.push('Payment details are missing');
    }
    
    if (validationErrors.length > 0) {
        console.error('🚨 CRITICAL VALIDATION ERRORS:', validationErrors);
        throw new Error('بيانات مفقودة: ' + validationErrors.join(', '));
    }
    
    console.log('✅ All form data validation passed - ready to send');
    return formData;
}

/**
 * 💳 الحصول على تفاصيل الدفع النشطة - ENHANCED
 */
function getActivePaymentDetails() {
    const paymentMethod = document.getElementById('payment_method')?.value || '';
    
    console.log('💳 البحث عن تفاصيل الدفع لطريقة:', paymentMethod);
    
    if (paymentMethod.includes('cash') || paymentMethod === 'bank_wallet') {
        const mobileField = document.getElementById('mobile-number');
        const mobileValue = mobileField?.value?.trim() || '';
        console.log('📱 Mobile field details:', {
            fieldExists: !!mobileField,
            isVisible: mobileField ? mobileField.closest('.dynamic-input').style.display !== 'none' : false,
            value: mobileValue || 'EMPTY',
            isValid: /^01[0125][0-9]{8}$/.test(mobileValue)
        });
        return mobileValue;
        
    } else if (paymentMethod === 'tilda') {
        const cardField = document.getElementById('card-number');
        const cardValue = cardField?.value?.trim() || '';
        console.log('💳 Card field details:', {
            fieldExists: !!cardField,
            isVisible: cardField ? cardField.closest('.dynamic-input').style.display !== 'none' : false,
            value: cardValue ? cardValue.substring(0, 4) + '***' : 'EMPTY',
            cleanValue: cardValue.replace(/[-\s]/g, ''),
            isValid: /^\d{16}$/.test(cardValue.replace(/[-\s]/g, ''))
        });
        return cardValue;
        
    } else if (paymentMethod === 'instapay') {
        const linkField = document.getElementById('payment-link');
        const linkValue = linkField?.value?.trim() || '';
        console.log('🔗 Link field details:', {
            fieldExists: !!linkField,
            isVisible: linkField ? linkField.closest('.dynamic-input').style.display !== 'none' : false,
            value: linkValue || 'EMPTY',
            hasInstapay: linkValue.includes('instapay'),
            hasIpn: linkValue.includes('ipn.eg')
        });
        return linkValue;
    }
    
    console.log('❓ No matching payment method found for:', paymentMethod);
    return '';
}

/**
 * 🌐 إرسال طلب ربط التليجرام للخادم - ULTRA ENHANCED VERSION
 */
async function sendTelegramLinkRequest(formData) {
    console.log('🌐 🔥 FINAL VERSION: إرسال طلب إلى /generate-telegram-code...');
    console.log('📤 🔥 EXACT DATA BEING SENT:', JSON.stringify(formData, null, 2));
    
    try {
        const requestOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFTokenFromMainSystem(),
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(formData)
        };
        
        console.log('🔗 Request details:', {
            url: '/generate-telegram-code',
            method: requestOptions.method,
            headers: requestOptions.headers,
            bodySize: requestOptions.body.length + ' chars'
        });
        
        const response = await fetch('/generate-telegram-code', requestOptions);
        
        console.log('📡 🔥 RAW HTTP RESPONSE:', {
            status: response.status,
            statusText: response.statusText,
            ok: response.ok,
            headers: Object.fromEntries(response.headers.entries()),
            url: response.url,
            redirected: response.redirected
        });
        
        // 🔍 قراءة النص الخام أولاً للتشخيص الكامل
        const responseText = await response.text();
        console.log('📄 🔥 RAW RESPONSE TEXT:', responseText);
        console.log('📄 Response length:', responseText.length + ' chars');
        
        if (!response.ok) {
            console.error('❌ 🔥 HTTP ERROR DETAILS:', {
                status: response.status,
                statusText: response.statusText,
                responseText: responseText,
                url: response.url
            });
            throw new Error(`خطأ HTTP ${response.status}: ${responseText || response.statusText}`);
        }
        
        // 🔄 تحويل النص إلى JSON مع معالجة أخطاء متقدمة
        let result;
        try {
            result = JSON.parse(responseText);
        } catch (parseError) {
            console.error('❌ 🔥 JSON PARSE ERROR:', {
                error: parseError.message,
                responseText: responseText,
                responseType: typeof responseText,
                isEmptyResponse: responseText.length === 0
            });
            throw new Error('استجابة الخادم ليست JSON صالح: ' + parseError.message);
        }
        
        // 🔍 تحليل شامل للاستجابة - FIXED: البحث عن code
        console.log('📦 🔥 PARSED JSON RESPONSE:', {
            success: result.success,
            hasMessage: !!result.message,
            message: result.message,
            hasCode: !!result.code,  // ✅ تم تغيير من telegram_code إلى code
            codeType: typeof result.code,  // ✅ تم تغيير
            codeValue: result.code,  // ✅ تم تغيير
            codeLength: result.code ? result.code.length : 0,  // ✅ تم تغيير
            hasWebUrl: !!result.telegram_web_url,
            webUrl: result.telegram_web_url,
            hasAppUrl: !!result.telegram_app_url,
            appUrl: result.telegram_app_url,
            hasBotUsername: !!result.bot_username,
            botUsername: result.bot_username,
            allKeys: Object.keys(result),
            fullResponse: result
        });
        
        // 🚨 فحص حاسم للكود قبل الإرجاع - FIXED: البحث عن code
        if (result.success && (!result.code || result.code === 'undefined' || result.code === null)) {
            console.error('🚨 🔥 CRITICAL SERVER BUG: Success=true but code is invalid!');
            console.error('🚨 code value:', result.code);  // ✅ تم تغيير
            console.error('🚨 code type:', typeof result.code);  // ✅ تم تغيير
            console.error('🚨 Full server response:', JSON.stringify(result, null, 2));
            
            throw new Error('خطأ في الخادم: لم يتم إنشاء كود التليجرام صحيح (received: ' + result.code + ')');  // ✅ تم تغيير
        }
        
        if (result.success && result.code) {  // ✅ تم تغيير
            console.log('✅ 🔥 SUCCESS: Valid code received:', result.code.substring(0, 15) + '...');  // ✅ تم تغيير
        }
        
        return result;
        
    } catch (networkError) {
        console.error('🌐 🔥 NETWORK/FETCH ERROR:', {
            name: networkError.name,
            message: networkError.message,
            stack: networkError.stack,
            cause: networkError.cause
        });
        throw new Error('خطأ في الاتصال بالخادم: ' + networkError.message);
    }
}

/**
 * 📱 فتح التليجرام بالطريقة الذكية - مع حماية من undefined
 */
async function openTelegramSmartly(data) {
    // 🚨 فحص حاسم للكود قبل الفتح - FIXED: البحث عن code
    if (!data.code || data.code === 'undefined' || data.code === null) {
        console.error('🚨 🔥 CRITICAL: Cannot open Telegram - invalid code!', {
            code: data.code,  // ✅ تم تغيير
            codeType: typeof data.code,  // ✅ تم تغيير
            dataKeys: Object.keys(data)
        });
        throw new Error('لا يمكن فتح التليجرام - كود غير صالح: ' + data.code);  // ✅ تم تغيير
    }
    
    console.log('📱 🔥 Opening Telegram with VALID code:', data.code.substring(0, 10) + '...');  // ✅ تم تغيير
    
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    // الحصول على bot username من الاستجابة أو استخدام القيمة الافتراضية
    const botUsername = data.bot_username || 'ea_fc_fifa_bot';
    
    // إنشاء الروابط مع الكود المؤكد - FIXED: استخدام code
    const telegramAppUrl = `tg://resolve?domain=${botUsername}&start=${data.code}`;  // ✅ تم تغيير
    const telegramWebUrl = `https://t.me/${botUsername}?start=${data.code}`;  // ✅ تم تغيير
    
    console.log('🔗 🔥 FINAL TELEGRAM URLS:', {
        appUrl: telegramAppUrl,
        webUrl: telegramWebUrl,
        botUsername: botUsername,
        code: data.code.substring(0, 15) + '...'  // ✅ تم تغيير
    });
    
    if (isMobile) {
        console.log('📱 Mobile detected - trying app first...');
        
        // محاولة التطبيق أولاً
        const appLink = document.createElement('a');
        appLink.href = telegramAppUrl;
        appLink.style.display = 'none';
        document.body.appendChild(appLink);
        appLink.click();
        
        setTimeout(() => {
            if (document.body.contains(appLink)) {
                document.body.removeChild(appLink);
            }
        }, 100);
        
        // فتح الويب كبديل
        setTimeout(() => {
            console.log('🌐 Opening web as fallback...');
            window.open(telegramWebUrl, '_blank');
        }, 2000);
        
    } else {
        console.log('💻 Desktop detected - opening web directly...');
        // الكمبيوتر - ويب مباشرة
        window.open(telegramWebUrl, '_blank');
    }
    
    // نسخ تلقائي للكود
    setTimeout(() => {
        copyTelegramCodeToClipboard(data.code);  // ✅ تم تغيير
    }, 1500);
}

/**
 * ⚠️ معالجة خطأ البيانات غير المكتملة - محسّنة
 */
function handleIncompleteDataError(telegramBtn, customMessage) {
    console.log('⚠️ معالجة خطأ البيانات غير المكتملة:', customMessage);
    
    const originalContent = telegramBtn.innerHTML;
    
    telegramBtn.innerHTML = `
        <div class="telegram-btn-content">
            <i class="fas fa-exclamation-circle telegram-icon" style="color: #ff4444;"></i>
            <div class="telegram-text">
                <span class="telegram-title">❌ بيانات غير مكتملة</span>
                <span class="telegram-subtitle">${customMessage}</span>
            </div>
        </div>
    `;
    telegramBtn.classList.add('error');
    
    // إظهار رسالة خطأ مفصلة
    showTelegramNotification(customMessage, 'error');
    
    // إعادة النص الأصلي بعد 5 ثوان
    setTimeout(() => {
        telegramBtn.innerHTML = originalContent;
        telegramBtn.classList.remove('error');
        isProcessingTelegram = false; // إعادة تعيين حالة المعالجة
        console.log('🔄 تم إعادة تعيين زر التليجرام');
    }, 5000);
}

/**
 * 📋 عرض الكود القابل للنسخ
 */
function displayCopyableCode(telegramBtn, data) {
    console.log('📋 عرض الكود القابل للنسخ...');
    
    // إزالة عرض سابق
    const existingCodeDisplay = document.querySelector('.telegram-code-display');
    if (existingCodeDisplay) {
        existingCodeDisplay.remove();
    }
    
    if (!data.code || data.code === 'undefined') {  // ✅ تم تغيير
        console.warn('⚠️ لا يوجد كود صالح للعرض:', data.code);  // ✅ تم تغيير
        return;
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
                /start ${data.code}
            </code>
            <div style="font-size: 0.9em; color: rgba(255, 255, 255, 0.8);">
                <small>انسخ هذا النص والصقه في التليجرام إذا لم يظهر تلقائياً</small>
            </div>
            <button onclick="window.copyTelegramCodeManual('/start ${data.code}')" 
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
    if (!code || code === 'undefined') {
        console.warn('⚠️ Cannot copy invalid code:', code);
        return;
    }
    
    const fullCode = `/start ${code}`;
    
    console.log('📋 محاولة نسخ الكود:', fullCode.substring(0, 20) + '...');
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(fullCode).then(() => {
            console.log('✅ تم نسخ الكود للحافظة بنجاح');
            showTelegramNotification('تم نسخ الكود للحافظة! الصقه في التليجرام', 'success');
        }).catch(err => {
            console.warn('❌ فشل في نسخ الكود بالطريقة الحديثة:', err);
            fallbackCopyToClipboard(fullCode);
        });
    } else {
        console.log('📋 استخدام الطريقة البديلة للنسخ...');
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
            console.log('✅ تم نسخ الكود بالطريقة البديلة');
            showTelegramNotification('تم نسخ الكود بالطريقة البديلة!', 'success');
        } else {
            console.warn('❌ فشل النسخ بالطريقة البديلة');
        }
    } catch (err) {
        console.error('❌ خطأ في النسخ:', err);
    }
    
    document.body.removeChild(textArea);
}

/**
 * 👁️ بدء مراقبة ربط التليجرام
 */
function startTelegramLinkingMonitor(code) {  // ✅ تم تغيير المعامل من telegramCode إلى code
    // إيقاف أي مراقبة سابقة
    if (telegramMonitoringInterval) {
        clearInterval(telegramMonitoringInterval);
    }
    
    if (!code || code === 'undefined') {  // ✅ تم تغيير
        console.warn('⚠️ Cannot monitor invalid code:', code);  // ✅ تم تغيير
        return;
    }
    
    console.log('🔍 بدء مراقبة ربط التليجرام للكود:', code.substring(0, 10) + '...');  // ✅ تم تغيير
    
    telegramMonitoringInterval = setInterval(async () => {
        try {
            console.log('🔍 فحص حالة الربط...');
            const checkResponse = await fetch(`/check-telegram-status/${code}`);  // ✅ تم تغيير من telegramCode
            const checkResult = await checkResponse.json();
            
            console.log('📊 نتيجة فحص الربط:', checkResult);
            
            if (checkResult.success && checkResult.linked) {
                // نجح الربط!
                clearInterval(telegramMonitoringInterval);
                telegramMonitoringInterval = null;
                
                console.log('✅ تم ربط التليجرام بنجاح!');
                showTelegramNotification('✅ تم ربط التليجرام بنجاح!', 'success');
                
                // الانتقال التلقائي بعد ثانية
                setTimeout(() => {
                    console.log('🚀 الانتقال إلى صفحة الكوينز...');
                    window.location.href = '/coins-order';
                }, 1000);
            }
        } catch (error) {
            console.error('❌ خطأ في فحص الربط:', error);
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
 * ⏳ تحديث الزر لحالة التحميل
 */
function updateTelegramButtonToLoading(telegramBtn) {
    console.log('⏳ تحديث الزر لحالة التحميل...');
    
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
    console.log('✅ تحديث الزر لحالة النجاح...');
    
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
    console.log('❌ معالجة خطأ التليجرام:', errorMessage);
    
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
        isProcessingTelegram = false; // إعادة تعيين حالة المعالجة
    }, 3000);
}

/**
 * 📢 إظهار إشعار خاص بالتليجرام
 */
function showTelegramNotification(message, type = 'info') {
    console.log(`📢 إشعار تليجرام (${type}):`, message);
    
    // نستخدم النظام الموجود من الملف الرئيسي
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
    } else if (typeof showNotification === 'function') {
        showNotification(message, type);
    } else {
        // إشعار بسيط كبديل
        console.log(`🔔 ${type.toUpperCase()}: ${message}`);
        alert(message);
    }
}

/**
 * 🔒 الحصول على CSRF token من النظام الرئيسي
 */
function getCSRFTokenFromMainSystem() {
    // نحاول استخدام الدالة الموجودة
    if (typeof window.getCSRFToken === 'function') {
        return window.getCSRFToken();
    } else if (typeof getCSRFToken === 'function') {
        return getCSRFToken();
    }
    
    // محاولة بديلة
    const token = document.querySelector('meta[name="csrf-token"]') || 
                  document.querySelector('input[name="csrfmiddlewaretoken"]');
    const tokenValue = token ? (token.getAttribute('content') || token.value) : '';
    
    console.log('🔒 CSRF Token obtained:', tokenValue ? 'EXISTS' : 'NOT_FOUND');
    return tokenValue;
}

/**
 * 🌐 دالة عامة للنسخ اليدوي (للاستخدام مع HTML)
 * هذه الدالة تُعرَّض للنظام العالمي
 */
window.copyTelegramCodeManual = function(text) {
    console.log('📋 نسخ يدوي للكود:', text.substring(0, 20) + '...');
    
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
    console.log('🤖 🔥 CRITICAL FIX: تهيئة وحدة التليجرام - code name fix');
    
    // إعداد زر التليجرام
    const telegramBtn = document.getElementById('telegram-link-btn');
    if (telegramBtn) {
        console.log('✅ تم العثور على زر التليجرام - ID: telegram-link-btn');
        
        // إزالة مستمعين قدامى
        const newBtn = telegramBtn.cloneNode(true);
        telegramBtn.parentNode.replaceChild(newBtn, telegramBtn);
        
        // إضافة المستمع الجديد
        newBtn.addEventListener('click', function(event) {
            console.log('👆 🔥 FINAL: تم النقر على زر التليجرام');
            event.preventDefault();
            handleTelegramLink();
        });
        
        console.log('✅ تم ربط زر التليجرام بالوحدة الجديدة');
    } else {
        console.warn('⚠️ زر التليجرام غير موجود - ID المطلوب: telegram-link-btn');
        
        // محاولة البحث عن أزرار أخرى
        const allButtons = document.querySelectorAll('button, [role="button"]');
        console.log('🔍 الأزرار الموجودة في الصفحة:', 
            Array.from(allButtons).map(btn => ({
                id: btn.id || 'NO_ID',
                className: btn.className || 'NO_CLASS',
                text: btn.textContent?.substring(0, 30) || 'NO_TEXT'
            }))
        );
    }
    
    // تنظيف أي مراقبة سابقة عند إعادة التهيئة
    if (telegramMonitoringInterval) {
        clearInterval(telegramMonitoringInterval);
        telegramMonitoringInterval = null;
    }
    
    // إعادة تعيين حالة المعالجة
    isProcessingTelegram = false;
    
    console.log('🔧 ✅ تم إعداد وحدة التليجرام بالكامل - CRITICAL FIX APPLIED');
}

// 📝 تسجيل تحميل الوحدة
console.log('📦 🔥 Telegram Integration Module v2.3.0 - CRITICAL CODE NAME FIX - تم التحميل بنجاح');
console.log('🔒 الوحدة معزولة تماماً ولا تحتاج تعديلات مستقبلية');
console.log('🚨 🔥 CRITICAL FIX APPLIED: تم تغيير telegram_code إلى code نهائياً');
console.log('🛠️ Enhanced debugging and server response matching enabled');
