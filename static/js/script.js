// FC 26 Profile Setup - كود JavaScript مدمج كامل
// دمج متقدم لكودين مع جميع الميزات والتحسينات

// متغيرات عامة
let isSubmitting = false;
let lastSubmitTime = 0;
let validationTimeout = null;
let whatsappValidationTimer = null;

// حالات التحقق
let validationStates = {
    whatsapp: false,
    paymentMethod: false,
    platform: false
};

// تهيئة التطبيق
document.addEventListener('DOMContentLoaded', function() {
    // إنشاء الجسيمات المتحركة
    createParticles();
    
    // تهيئة جميع مستمعي الأحداث
    initializeEventListeners();
    
    // تحسين الأداء للهواتف
    if (window.innerWidth <= 768) {
        optimizeForMobile();
    }
    
    // تهيئة الميزات المتقدمة
    initializeAdvancedFeatures();
});

// إنشاء الجسيمات المتحركة للخلفية
function createParticles() {
    const container = document.getElementById('particlesBg');
    if (!container) return;
    
    const particleCount = window.innerWidth <= 768 ? 15 : 25;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 8 + 's';
        particle.style.animationDuration = (Math.random() * 4 + 6) + 's';
        container.appendChild(particle);
    }
}

// تحسين للهواتف المحمولة
function optimizeForMobile() {
    // تقليل عدد الجسيمات
    const particles = document.querySelectorAll('.particle');
    particles.forEach((particle, index) => {
        if (index > 10) {
            particle.remove();
        }
    });
    
    // تحسين الانيميشن
    document.body.style.setProperty('--animation-duration', '0.2s');
    
    // معالجة لوحة المفاتيح على الهواتف
    setupMobileKeyboardHandling();
}

// معالجة لوحة المفاتيح للهواتف
function setupMobileKeyboardHandling() {
    let viewportHeight = window.innerHeight;
    
    window.addEventListener('resize', function() {
        const currentHeight = window.innerHeight;
        const heightDifference = viewportHeight - currentHeight;
        
        if (heightDifference > 150) {
            document.body.classList.add('keyboard-open');
        } else {
            document.body.classList.remove('keyboard-open');
        }
    });
    
    // تركيز الحقول مع تمرير سلس
    document.querySelectorAll('input, textarea').forEach(input => {
        input.addEventListener('focus', function() {
            setTimeout(() => {
                this.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }, 300);
        });
    });
}

// التحقق الفوري والمتقدم من رقم الواتساب
async function validateWhatsAppReal(phone) {
    if (!phone || phone.length < 5) {
        return { is_valid: false, valid: false, error: 'رقم قصير جداً' };
    }

    try {
        // محاولة كلا الـ endpoints للتوافق
        let response;
        try {
            response = await fetch('/validate-whatsapp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ phone: phone, phone_number: phone })
            });
        } catch (e) {
            // محاولة بديلة
            response = await fetch('/validate_whatsapp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ phone: phone, phone_number: phone })
            });
        }

        if (!response.ok) {
            throw new Error('خطأ في الخادم');
        }

        const result = await response.json();
        
        // توحيد الاستجابة
        return {
            is_valid: result.is_valid || result.valid,
            valid: result.is_valid || result.valid,
            error: result.error || result.message,
            ...result
        };

    } catch (error) {
        console.error('خطأ في التحقق:', error);
        return { is_valid: false, valid: false, error: 'خطأ في الاتصال' };
    }
}

// عرض معلومات مبسطة للرقم
function showPhoneInfo(info, inputElement) {
    // إزالة معلومات سابقة
    const existingInfo = document.querySelector('.phone-info');
    if (existingInfo) {
        existingInfo.classList.remove('show');
        setTimeout(() => existingInfo.remove(), 300);
    }

    // التحقق من صحة البيانات
    if (!info.is_valid) {
        showPhoneInfoError(info.error || 'رقم غير صحيح', inputElement);
        return;
    }

    // إنشاء عنصر المعلومات المبسط
    const infoDiv = document.createElement('div');
    infoDiv.className = 'phone-info success-info';
    
    infoDiv.innerHTML = `
        <div class="info-content">
            <div class="info-header">
                <i class="fas fa-check-circle"></i>
                <span>رقم صحيح ومتاح على واتساب</span>
            </div>
            <div class="phone-display">
                <span class="formatted-number">${info.formatted || inputElement.value}</span>
            </div>
            <div class="validation-badge">
                <i class="fas fa-whatsapp"></i>
                <span>تم التحقق من الرقم</span>
            </div>
        </div>
    `;
    
    // إضافة العنصر وتطبيق الانيميشن
    const container = inputElement.closest('.form-group') || inputElement.parentNode;
    container.appendChild(infoDiv);
    
    setTimeout(() => {
        infoDiv.classList.add('show', 'animated');
    }, 100);

    // اهتزاز للنجاح (للهواتف)
    if (navigator.vibrate) {
        navigator.vibrate([100, 50, 100]);
    }
}

// عرض خطأ في معلومات الرقم
function showPhoneInfoError(errorMessage, inputElement) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'phone-info error-info';
    errorDiv.innerHTML = `
        <div class="info-content">
            <i class="fas fa-times-circle"></i>
            <span>${errorMessage}</span>
        </div>
    `;
    
    const container = inputElement.closest('.form-group') || inputElement.parentNode;
    container.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.classList.add('show');
    }, 100);
}

// عرض حالة التحميل لرقم الواتساب
function showPhoneInfoLoading(inputElement) {
    const existingInfo = document.querySelector('.phone-info');
    if (existingInfo) {
        existingInfo.remove();
    }
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'phone-info loading-info';
    loadingDiv.innerHTML = `
        <div class="phone-info-loading">
            <div class="loading-spinner-small"></div>
            <span>جاري التحقق من الرقم...</span>
        </div>
    `;
    
    const container = inputElement.closest('.form-group') || inputElement.parentNode;
    container.appendChild(loadingDiv);
    
    setTimeout(() => {
        loadingDiv.classList.add('show');
    }, 100);
}

// إزالة معلومات الرقم
function clearPhoneInfo() {
    const phoneInfoElements = document.querySelectorAll('.phone-info');
    phoneInfoElements.forEach(element => {
        element.classList.remove('show', 'animated');
        setTimeout(() => {
            if (element.parentNode) {
                element.remove();
            }
        }, 300);
    });
}

// تهيئة جميع مستمعي الأحداث
function initializeEventListeners() {
    // عناصر النموذج الأساسية
    const platformCards = document.querySelectorAll('.platform-card');
    const paymentButtons = document.querySelectorAll('.payment-btn');
    const whatsappInput = document.getElementById('whatsapp');
    const form = document.getElementById('profileForm');

    // معالجة اختيار المنصة
    setupPlatformSelection(platformCards);
    
    // معالجة اختيار طريقة الدفع
    setupPaymentSelection(paymentButtons);
    
    // معالجة رقم الواتساب
    setupWhatsAppInput(whatsappInput);
    
    // معالجة الحقول الديناميكية
    setupDynamicInputs();
    
    // معالجة إرسال النموذج
    setupFormSubmission(form);
    
    // تهيئة الميزات المتقدمة
    initializeTooltips();
    initializeAnimations();
    
    // منع إرسال النموذج بالضغط على Enter
    setupEnterKeyHandling();
}

// إعداد اختيار المنصة
function setupPlatformSelection(platformCards) {
    platformCards.forEach(card => {
        card.addEventListener('click', function() {
            // إزالة التحديد من الكل
            platformCards.forEach(c => c.classList.remove('selected'));
            
            // تحديد البطاقة المضغوطة
            this.classList.add('selected');
            const platformInput = document.getElementById('platform');
            if (platformInput) {
                platformInput.value = this.dataset.platform;
            }
            
            // تحديث حالة التحقق
            validationStates.platform = true;
            
            // إضافة تأثير اهتزاز خفيف (للهواتف)
            if (navigator.vibrate) {
                navigator.vibrate(50);
            }
            
            checkFormValidity();
        });
    });
}

// إعداد اختيار طريقة الدفع
function setupPaymentSelection(paymentButtons) {
    paymentButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            paymentButtons.forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');
            
            const paymentType = this.dataset.type;
            const paymentValue = this.dataset.value;
            
            const paymentMethodInput = document.getElementById('payment_method');
            if (paymentMethodInput) {
                paymentMethodInput.value = paymentValue;
            }
            
            // إخفاء جميع الحقول الديناميكية
            document.querySelectorAll('.dynamic-input').forEach(input => {
                input.classList.remove('show');
                const inputField = input.querySelector('input');
                if (inputField) {
                    inputField.required = false;
                    inputField.value = '';
                }
            });
            
            // إخفاء رسائل الخطأ
            document.querySelectorAll('.error-message-field').forEach(error => {
                error.classList.remove('show');
            });
            
            // إظهار الحقل المناسب
            const targetInput = document.getElementById(paymentType + '-input');
            if (targetInput) {
                setTimeout(() => {
                    targetInput.classList.add('show');
                    const inputField = targetInput.querySelector('input');
                    if (inputField) {
                        inputField.required = true;
                        
                        // تركيز تلقائي للهواتف
                        if (window.innerWidth <= 768) {
                            setTimeout(() => {
                                inputField.focus();
                            }, 300);
                        }
                    }
                }, 150);
            }
            
            // اهتزاز للهواتف
            if (navigator.vibrate) {
                navigator.vibrate(30);
            }
            
            // إعادة التحقق من طرق الدفع
            setTimeout(validatePaymentMethod, 200);
        });
    });
}

// إعداد حقل رقم الواتساب
function setupWhatsAppInput(whatsappInput) {
    if (!whatsappInput) return;
    
    // معالجة الإدخال مع التحقق الفوري
    whatsappInput.addEventListener('input', function(e) {
        const inputValue = this.value;
        
        // تنظيف الرقم أولاً
        let cleanValue = formatPhoneInput(inputValue);
        this.value = cleanValue;
        
        // إزالة معلومات سابقة عند بدء الكتابة
        clearPhoneInfo();
        
        // إلغاء التحقق السابق
        if (validationTimeout) {
            clearTimeout(validationTimeout);
        }
        if (whatsappValidationTimer) {
            clearTimeout(whatsappValidationTimer);
        }
        
        // إعادة تعيين حالة التحقق
        validationStates.whatsapp = false;
        updateValidationUI(this, false, '');
        
        // تحقق فوري بعد توقف المستخدم عن الكتابة
        if (cleanValue.length >= 5) {
            // إضافة مؤشر التحميل
            this.classList.add('validating');
            showPhoneInfoLoading(this);
            
            validationTimeout = setTimeout(async () => {
                const result = await validateWhatsAppReal(cleanValue);
                
                // إزالة مؤشر التحميل
                this.classList.remove('validating');
                
                // تحديث حالة التحقق
                validationStates.whatsapp = result.is_valid || result.valid;
                
                // عرض النتيجة
                if (validationStates.whatsapp) {
                    updateValidationUI(this, true, 'رقم واتساب صحيح ✓');
                    showPhoneInfo(result, this);
                } else {
                    updateValidationUI(this, false, result.error || result.message || 'رقم غير صحيح');
                    showPhoneInfoError(result.error || result.message || 'رقم غير صحيح', this);
                }
                
                // تحديث حالة النموذج
                checkFormValidity();
                
            }, 800); // انتظار 800ms بعد توقف الكتابة
        } else {
            this.classList.remove('validating');
            checkFormValidity();
        }
    });
    
    // التحقق عند فقدان التركيز
    whatsappInput.addEventListener('blur', function() {
        const value = this.value.trim();
        if (value && !validationStates.whatsapp) {
            validateWhatsAppReal(value).then(result => {
                validationStates.whatsapp = result.is_valid || result.valid;
                if (validationStates.whatsapp) {
                    updateValidationUI(this, true, 'رقم واتساب صحيح ✓');
                    showPhoneInfo(result, this);
                } else {
                    updateValidationUI(this, false, result.error || result.message || 'رقم غير صحيح');
                }
                checkFormValidity();
            });
        }
    });
}

// تنسيق إدخال رقم الهاتف
function formatPhoneInput(value) {
    // إزالة جميع الرموز غير الرقمية باستثناء + في البداية
    let cleaned = value.replace(/[^\d+]/g, '');
    
    // التأكد من أن + موجود فقط في البداية
    if (cleaned.includes('+')) {
        const parts = cleaned.split('+');
        cleaned = '+' + parts.join('');
    }
    
    return cleaned;
}

// إعداد الحقول الديناميكية لطرق الدفع
function setupDynamicInputs() {
    // جميع حقول طرق الدفع
    const paymentInputs = [
        'vodafone_cash', 'etisalat_cash', 'orange_cash', 'we_pay', 
        'fawry', 'aman', 'masary', 'bee', 'mobile-number',
        'telda_card', 'card-number', 'instapay_link', 'payment-link'
    ];

    paymentInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('input', function() {
                validatePaymentInput(this);
                checkFormValidity();
            });
            
            input.addEventListener('blur', function() {
                validatePaymentInput(this);
                checkFormValidity();
            });
        }
    });
    
    // معالجة خاصة لكارت تيلدا (تنسيق الأرقام)
    const teldaInput = document.getElementById('telda_card') || document.getElementById('card-number');
    if (teldaInput) {
        teldaInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '').replace(/[^0-9]/gi, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            if (formattedValue !== e.target.value) {
                e.target.value = formattedValue;
            }
            validatePaymentInput(this);
            checkFormValidity();
        });
    }
}

// التحقق من صحة حقول الدفع
function validatePaymentInput(input) {
    const value = input.value.trim();
    const inputId = input.id;
    let isValid = false;
    let errorMessage = '';
    
    if (!value) {
        updateValidationUI(input, true, ''); // فارغ = صحيح للحقول الاختيارية
        return true;
    }
    
    // التحقق من المحافظ الإلكترونية (11 رقم)
    if (['vodafone_cash', 'etisalat_cash', 'orange_cash', 'we_pay', 
         'fawry', 'aman', 'masary', 'bee', 'mobile-number'].includes(inputId)) {
        isValid = /^01[0125][0-9]{8}$/.test(value) && value.length === 11;
        errorMessage = isValid ? '' : 'رقم المحفظة يجب أن يكون 11 رقم ويبدأ بـ 010، 011، 012، أو 015';
    }
    // التحقق من كارت تيلدا (16 رقم)
    else if (['telda_card', 'card-number'].includes(inputId)) {
        const numbersOnly = value.replace(/\s/g, '');
        isValid = /^\d{16}$/.test(numbersOnly);
        errorMessage = isValid ? '' : 'رقم كارت تيلدا يجب أن يكون 16 رقم';
    }
    // التحقق من رابط إنستا باي
    else if (['instapay_link', 'payment-link'].includes(inputId)) {
        isValid = isValidInstaPayLink(value);
        errorMessage = isValid ? '' : 'رابط إنستا باي غير صحيح';
    }
    
    updateValidationUI(input, isValid, errorMessage);
    return isValid;
}

// التحقق الشامل من طرق الدفع
function validatePaymentMethod() {
    const paymentInputs = document.querySelectorAll('input[name$="_cash"], input[name="telda_card"], input[name="instapay_link"], .dynamic-input.show input');
    let hasValidPayment = false;
    
    paymentInputs.forEach(input => {
        if (validatePaymentInput(input)) {
            const value = input.value.trim();
            if (value) {
                hasValidPayment = true;
            }
        }
    });
    
    validationStates.paymentMethod = hasValidPayment;
    return hasValidPayment;
}

// التحقق من صحة رابط إنستا باي
function isValidInstaPayLink(link) {
    const instaPayPatterns = [
        /^https?:\/\/(www\.)?instapay\.com\.eg\//i,
        /^https?:\/\/(www\.)?instapay\.app\//i,
        /^instapay:\/\//i,
        /^https?:\/\/(www\.)?app\.instapay\.com\.eg\//i
    ];
    
    return instaPayPatterns.some(pattern => pattern.test(link));
}

// تحديث واجهة التحقق للحقول
function updateValidationUI(input, isValid, message) {
    const container = input.closest('.form-group');
    if (!container) return;
    
    // إزالة الكلاسات الموجودة
    container.classList.remove('valid', 'invalid');
    input.classList.remove('valid', 'invalid');
    
    // إزالة رسائل الخطأ الموجودة
    const existingError = container.querySelector('.error-message');
    const existingSuccess = container.querySelector('.success-message');
    if (existingError) existingError.remove();
    if (existingSuccess) existingSuccess.remove();
    
    if (message) {
        if (isValid) {
            container.classList.add('valid');
            input.classList.add('valid');
            if (message.includes('✓')) {
                const successMsg = document.createElement('div');
                successMsg.className = 'success-message';
                successMsg.textContent = message;
                container.appendChild(successMsg);
            }
        } else {
            container.classList.add('invalid');
            input.classList.add('invalid');
            const errorMsg = document.createElement('div');
            errorMsg.className = 'error-message';
            errorMsg.textContent = message;
            container.appendChild(errorMsg);
        }
    } else if (isValid) {
        container.classList.add('valid');
        input.classList.add('valid');
    }
}

// التحقق الشامل من صحة النموذج
function checkFormValidity() {
    // التحقق من جميع المتطلبات
    const platform = document.getElementById('platform')?.value;
    const whatsapp = document.getElementById('whatsapp')?.value;
    const paymentMethod = document.getElementById('payment_method')?.value;
    
    // تحديث حالات التحقق
    validationStates.platform = !!platform;
    
    // التحقق من صحة الواتساب من المعلومات المعروضة
    const phoneInfo = document.querySelector('.phone-info.success-info');
    validationStates.whatsapp = !!(whatsapp && phoneInfo);
    
    // التحقق من طرق الدفع
    validatePaymentMethod();
    
    // التحقق النهائي
    const isValid = validationStates.platform && validationStates.whatsapp && validationStates.paymentMethod;
    
    updateSubmitButton(isValid);
    return isValid;
}

// تحديث زر الإرسال
function updateSubmitButton(isValid = null) {
    const submitBtn = document.getElementById('submitBtn') || document.querySelector('.submit-btn');
    if (!submitBtn) return;
    
    if (isValid === null) {
        isValid = validationStates.platform && validationStates.whatsapp && validationStates.paymentMethod;
    }
    
    submitBtn.disabled = !isValid;
    submitBtn.classList.toggle('enabled', isValid);
    
    // تحديث النص والأيقونة
    if (isValid) {
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> إرسال البيانات';
        submitBtn.style.opacity = '1';
        submitBtn.style.transform = 'scale(1)';
    } else {
        submitBtn.innerHTML = '<i class="fas fa-lock"></i> أكمل البيانات المطلوبة';
        submitBtn.style.opacity = '0.6';
        submitBtn.style.transform = 'scale(0.98)';
    }
}

// إعداد إرسال النموذج
function setupFormSubmission(form) {
    if (!form) return;
    
    form.addEventListener('submit', handleFormSubmit);
}

// معالجة إرسال النموذج
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // منع الإرسال المتكرر
    const now = Date.now();
    if (isSubmitting || (now - lastSubmitTime < 3000)) {
        showNotification('يرجى الانتظار قبل المحاولة مرة أخرى', 'error');
        return;
    }
    
    // التحقق النهائي من النموذج
    if (!checkFormValidity()) {
        showNotification('يرجى إكمال جميع البيانات المطلوبة', 'error');
        return;
    }
    
    isSubmitting = true;
    lastSubmitTime = now;
    
    const loading = document.getElementById('loading');
    const loadingSpinner = document.getElementById('loading-spinner');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    const submitBtn = document.getElementById('submitBtn') || document.querySelector('.submit-btn');
    
    // إخفاء الرسائل السابقة
    if (successMessage) successMessage.classList.remove('show');
    if (errorMessage) errorMessage.classList.remove('show');
    
    // عرض شاشة التحميل
    if (loading) loading.classList.add('show');
    if (loadingSpinner) loadingSpinner.style.display = 'flex';
    
    // تحديث زر الإرسال
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الإرسال...';
    }
    
    // اهتزاز للهواتف
    if (navigator.vibrate) {
        navigator.vibrate([100, 50, 100]);
    }
    
    try {
        const formData = new FormData(e.target);
        
        // محاولة كلا الـ endpoints
        let response;
        try {
            response = await fetch('/update-profile', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
                }
            });
        } catch (e) {
            response = await fetch('/submit_profile', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
                }
            });
        }
        
        const result = await response.json();
        
        // إخفاء شاشة التحميل
        if (loading) loading.classList.remove('show');
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        
        if (response.ok && result.success) {
            // رسالة النجاح المحسنة
            let successText = '✅ تم حفظ بياناتك بنجاح!';
            if (result.data && result.data.whatsapp_info) {
                const info = result.data.whatsapp_info;
                successText += `<br><small>رقم الواتساب: ${result.data.whatsapp_number}<br>البلد: ${info.country} | الشركة: ${info.carrier}</small>`;
            }
            
            if (successMessage) {
                successMessage.innerHTML = successText;
                successMessage.classList.add('show');
            } else {
                showNotification('تم إرسال البيانات بنجاح! سيتم التواصل معك قريباً', 'success');
            }
            
            // اهتزاز نجاح
            if (navigator.vibrate) {
                navigator.vibrate([200, 100, 200]);
            }
            
            // إعادة تعيين النموذج بعد النجاح
            setTimeout(() => {
                console.log('تم حفظ البيانات بنجاح:', result.data);
                // يمكن إضافة إعادة توجيه هنا إذا لزم الأمر
            }, 2000);
            
        } else {
            const errorText = result.message || 'حدث خطأ غير متوقع';
            if (errorMessage) {
                errorMessage.textContent = errorText;
                errorMessage.classList.add('show');
            } else {
                showNotification(errorText, 'error');
            }
            
            // اهتزاز خطأ
            if (navigator.vibrate) {
                navigator.vibrate([300, 100, 300, 100, 300]);
            }
        }
        
    } catch (error) {
        console.error('خطأ في الشبكة:', error);
        
        // إخفاء شاشة التحميل
        if (loading) loading.classList.remove('show');
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        
        const errorText = 'خطأ في الاتصال، يرجى المحاولة مرة أخرى';
        if (errorMessage) {
            errorMessage.textContent = errorText;
            errorMessage.classList.add('show');
        } else {
            showNotification(errorText, 'error');
        }
        
        // اهتزاز خطأ شبكة
        if (navigator.vibrate) {
            navigator.vibrate([500, 200, 500]);
        }
    }
    
    isSubmitting = false;
    updateSubmitButton();
}

// معالجة مفتاح Enter
function setupEnterKeyHandling() {
    // منع إرسال النموذج بالضغط على Enter في الحقول
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const nextInput = getNextInput(input);
                if (nextInput) {
                    nextInput.focus();
                } else {
                    // إذا كان النموذج صحيح، قم بالإرسال
                    if (checkFormValidity()) {
                        const form = input.closest('form');
                        if (form) {
                            handleFormSubmit({ preventDefault: () => {}, target: form });
                        }
                    }
                }
            }
        });
    });
}

// الحصول على الحقل التالي
function getNextInput(currentInput) {
    const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]):not([disabled])'));
    const currentIndex = inputs.indexOf(currentInput);
    return inputs[currentIndex + 1] || null;
}

// إظهار إشعار مؤقت
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const iconClass = type === 'success' ? 'fa-check-circle' : 
                     type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${iconClass}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // تطبيق الأنماط
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'error' ? '#DC2626' : type === 'success' ? '#10B981' : '#3B82F6'};
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        z-index: 10000;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        max-width: 90%;
        opacity: 0;
        transition: all 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // إظهار الإشعار
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 100);
    
    // إخفاء تلقائي بعد 5 ثوان
    setTimeout(() => {
        hideNotification(notification);
    }, 5000);
    
    // زر الإغلاق
    notification.querySelector('.notification-close').addEventListener('click', () => {
        hideNotification(notification);
    });
}

// إخفاء الإشعار
function hideNotification(notification) {
    notification.style.opacity = '0';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// الحصول على رمز CSRF
function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]') || 
                  document.querySelector('input[name="csrfmiddlewaretoken"]');
    return token ? token.getAttribute('content') || token.value : '';
}

// تهيئة tooltips
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
        element.addEventListener('focus', showTooltip);
        element.addEventListener('blur', hideTooltip);
    });
}

// إظهار tooltip
function showTooltip(e) {
    const text = e.target.getAttribute('data-tooltip');
    if (!text) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        z-index: 10001;
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
        white-space: nowrap;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
    tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
    
    setTimeout(() => {
        tooltip.style.opacity = '1';
    }, 100);
    
    e.target._tooltip = tooltip;
}

// إخفاء tooltip
function hideTooltip(e) {
    const tooltip = e.target._tooltip;
    if (tooltip) {
        tooltip.style.opacity = '0';
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        }, 300);
        delete e.target._tooltip;
    }
}

// تهيئة الانيميشن
function initializeAnimations() {
    // انيميشن أقسام النموذج عند التمرير
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    document.querySelectorAll('.form-section, .form-group').forEach(section => {
        observer.observe(section);
    });
    
    // تمرير سلس للروابط
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// تهيئة الميزات المتقدمة
function initializeAdvancedFeatures() {
    // تهيئة tooltips والانيميشن
    initializeTooltips();
    initializeAnimations();
    
    // معالجة أحداث النافذة
    setupWindowEvents();
    
    // تحسينات اللمس للهواتف
    setupTouchOptimizations();
    
    // منع التكبير على iOS
    setupIOSOptimizations();
    
    console.log('FC 26 Profile Setup - تم تهيئة جميع الميزات المتقدمة');
}

// إعداد أحداث النافذة
function setupWindowEvents() {
    // تحسين الأداء عند تغيير حجم النافذة
    window.addEventListener('resize', debounce(function() {
        if (window.innerWidth <= 768) {
            optimizeForMobile();
        }
    }, 250));
}

// تحسينات اللمس للهواتف
function setupTouchOptimizations() {
    if ('ontouchstart' in window) {
        document.addEventListener('touchstart', function() {}, {passive: true});
        
        // تحسين التفاعل مع العناصر القابلة للنقر
        document.querySelectorAll('.platform-card, .payment-btn, button').forEach(element => {
            element.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            }, {passive: true});
            
            element.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('touch-active');
                }, 150);
            }, {passive: true});
        });
    }
}

// تحسينات iOS لمنع التكبير
function setupIOSOptimizations() {
    if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
        const viewport = document.querySelector('meta[name=viewport]');
        
        document.addEventListener('focusin', function(e) {
            if (e.target.matches('input, select, textarea')) {
                if (viewport) {
                    viewport.setAttribute('content', 
                        'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no'
                    );
                }
            }
        });
        
        document.addEventListener('focusout', function() {
            if (viewport) {
                viewport.setAttribute('content', 'width=device-width, initial-scale=1');
            }
        });
    }
}

// دالة تأخير التنفيذ
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// إعادة تعيين حالات التحقق
function clearValidationStates() {
    validationStates = {
        whatsapp: false,
        paymentMethod: false,
        platform: false
    };
    
    // إزالة جميع واجهات التحقق
    document.querySelectorAll('.form-group').forEach(group => {
        group.classList.remove('valid', 'invalid');
        const errorMsg = group.querySelector('.error-message');
        const successMsg = group.querySelector('.success-message');
        if (errorMsg) errorMsg.remove();
        if (successMsg) successMsg.remove();
    });
    
    // إزالة معلومات الهاتف
    clearPhoneInfo();
    
    // تحديث زر الإرسال
    updateSubmitButton();
}

// تسجيل Service Worker للـ PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js').then(function(registration) {
            console.log('ServiceWorker تم تسجيله بنجاح');
        }, function(err) {
            console.log('فشل تسجيل ServiceWorker');
        });
    });
}

// تصدير الوظائف للاستخدام الخارجي أو الاختبار
window.FC26ProfileSetup = {
    validateWhatsAppReal,
    validatePaymentMethod,
    showNotification,
    clearValidationStates,
    checkFormValidity,
    updateSubmitButton
};

// رسالة تأكيد التهيئة
console.log('FC 26 Profile Setup - تم تهيئة JavaScript المدمج بنجاح');

// متغيرات للتليجرام محدثة
let currentTelegramCode = null;
let telegramStatusChecker = null;
let correctBotUsername = null;

// تحميل username البوت الصحيح
async function loadBotUsername() {
    try {
        const response = await fetch('/get-bot-username');
        const result = await response.json();
        correctBotUsername = result.bot_username;
        console.log('✅ Bot username loaded:', correctBotUsername);
    } catch (error) {
        console.error('❌ Failed to load bot username:', error);
        correctBotUsername = 'YourBotName_bot'; // fallback
    }
}

// دالة توليد كود التليجرام - محدثة
async function generateTelegramCode() {
    const telegramBtn = document.getElementById('telegramBtn');
    const telegramCodeResult = document.getElementById('telegramCodeResult');
    
    // التحقق من البيانات الأساسية
    const platform = document.getElementById('platform')?.value;
    const whatsappNumber = document.getElementById('whatsapp')?.value;
    
    if (!platform || !whatsappNumber) {
        showNotification('يرجى إكمال الملف الشخصي أولاً (المنصة ورقم الواتساب)', 'error');
        return;
    }
    
    // حالة التحميل
    telegramBtn.classList.add('generating');
    telegramBtn.disabled = true;
    telegramBtn.innerHTML = `
        <div class="telegram-btn-content">
            <i class="fas fa-spinner fa-spin telegram-icon"></i>
            <div class="telegram-text">
                <span class="telegram-title">⚡ جاري إنشاء الرابط</span>
                <span class="telegram-subtitle">انتظر لحظة...</span>
            </div>
        </div>
    `;
    
    try {
        const formData = {
            platform: platform,
            whatsapp_number: whatsappNumber,
            payment_method: document.getElementById('payment_method')?.value || '',
            payment_details: document.querySelector('.dynamic-input.show input')?.value || ''
        };
        
        console.log('📤 Generating Telegram code with data:', formData);
        
        const response = await fetch('/generate-telegram-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        console.log('📥 Telegram code result:', result);
        
        if (result.success) {
            // حفظ الكود
            currentTelegramCode = result.code;
            document.getElementById('generatedCode').textContent = result.code;
            
            // تحديث زر التليجرام ليصبح زر فتح مباشر
            telegramBtn.innerHTML = `
                <div class="telegram-btn-content">
                    <i class="fab fa-telegram telegram-icon"></i>
                    <div class="telegram-text">
                        <span class="telegram-title">📱 فتح التليجرام والربط</span>
                        <span class="telegram-subtitle">اضغط للربط التلقائي</span>
                    </div>
                </div>
            `;
            
            // تغيير وظيفة الزر للفتح المباشر
            telegramBtn.onclick = function() {
                openTelegramAppDirect();
            };
            
            // إظهار منطقة الكود (بدون زر النسخ)
            telegramCodeResult.innerHTML = `
                <div class="code-container">
                    <div class="code-header">
                        <i class="fas fa-rocket"></i>
                        <span>جاهز للربط التلقائي</span>
                    </div>
                    <div class="generated-code">${result.code}</div>
                    <div class="telegram-actions">
                        <button type="button" class="telegram-open-btn-big" onclick="openTelegramAppDirect()">
                            <i class="fab fa-telegram"></i>
                            🚀 فتح التليجرام والربط الآن
                        </button>
                    </div>
                    <div class="telegram-instructions">
                        <div class="single-step">
                            ⚡ اضغط الزر وسيتم الربط التلقائي!
                        </div>
                    </div>
                </div>
            `;
            
            telegramCodeResult.style.display = 'block';
            setTimeout(() => {
                telegramCodeResult.classList.add('show');
                
                // تمرير تلقائي
                telegramCodeResult.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }, 100);
            
            // اهتزاز نجاح
            if (navigator.vibrate) {
                navigator.vibrate([100, 50, 100]);
            }
            
            showNotification(`✅ جاهز للربط! الكود: ${result.code}`, 'success');
            
        } else {
            showNotification(result.message || 'خطأ في إنشاء الكود', 'error');
            resetTelegramButton();
        }
        
    } catch (error) {
        console.error('خطأ في توليد كود التليجرام:', error);
        showNotification('خطأ في الاتصال، يرجى المحاولة مرة أخرى', 'error');
        resetTelegramButton();
    }
    
    // إزالة حالة التحميل
    telegramBtn.classList.remove('generating');
    telegramBtn.disabled = false;
}

// دالة فتح التليجرام المباشر - الربط التلقائي
function openTelegramAppDirect() {
    const code = currentTelegramCode || document.getElementById('generatedCode').textContent;
    
    if (!code) {
        showNotification('❌ لا يوجد كود للربط', 'error');
        return;
    }
    
    if (!correctBotUsername) {
        showNotification('جاري تحميل معلومات البوت...', 'info');
        loadBotUsername().then(() => {
            openTelegramAppDirect();
        });
        return;
    }
    
    // تجميد واجهة المستخدم
    const telegramCodeResult = document.getElementById('telegramCodeResult');
    const allButtons = document.querySelectorAll('button');
    
    if (telegramCodeResult) {
        telegramCodeResult.style.opacity = '0.6';
        telegramCodeResult.style.pointerEvents = 'none';
    }
    
    allButtons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.6';
    });
    
    // روابط التليجرام
    const telegramAppUrl = `tg://resolve?domain=${correctBotUsername}&start=${code}`;
    const telegramWebUrl = `https://t.me/${correctBotUsername}?start=${code}`;
    
    console.log('🚀 AUTO-LINKING Telegram:', correctBotUsername, 'Code:', code);
    
    // فتح التليجرام حسب النوع
    if (navigator.userAgent.match(/(iPhone|iPad|iPod|Android)/i)) {
        // للهواتف - محاولة التطبيق أولاً ثم الويب
        const tempLink = document.createElement('a');
        tempLink.href = telegramAppUrl;
        tempLink.style.display = 'none';
        document.body.appendChild(tempLink);
        tempLink.click();
        document.body.removeChild(tempLink);
        
        setTimeout(() => {
            window.open(telegramWebUrl, '_blank');
        }, 800);
    } else {
        // للكمبيوتر - فتح الرابط مباشرة
        window.open(telegramWebUrl, '_blank');
    }
    
    // رسائل الربط التلقائي
    showNotification('🚀 فتح التليجرام...', 'info');
    
    setTimeout(() => {
        showNotification('⚡ جاري الربط التلقائي...', 'info');
    }, 1500);
    
    setTimeout(() => {
        showNotification('🔗 انتظار تأكيد الربط...', 'info');
    }, 3000);
    
    // بدء فحص الربط التلقائي
    startAutoTelegramLinking(code);
}

// نظام الربط التلقائي المطور
function startAutoTelegramLinking(code) {
    let attemptCount = 0;
    const maxAttempts = 45; // 2.25 دقيقة
    
    const autoLinker = setInterval(async () => {
        attemptCount++;
        
        try {
            const response = await fetch(`/check-telegram-status/${code}`);
            const result = await response.json();
            
            if (result.success && result.linked) {
                // نجح الربط!
                clearInterval(autoLinker);
                console.log('🎉 AUTO-LINK SUCCESS!');
                
                // إظهار النجاح الفوري
                showUltimateSuccess();
                return;
            }
            
            // تحديثات الحالة
            if (attemptCount === 5) {
                showNotification('📡 البحث عن الربط...', 'info');
            } else if (attemptCount === 10) {
                showNotification('🔍 فحص حالة الاتصال...', 'info');
            } else if (attemptCount === 20) {
                showNotification('⏳ يرجى التأكد من إرسال الكود للبوت', 'info');
            } else if (attemptCount === 30) {
                showNotification('⚠️ تأكد من فتح التليجرام وإرسال الكود', 'info');
            }
            
        } catch (error) {
            console.error('خطأ في الربط التلقائي:', error);
        }
        
        // انتهاء المحاولات
        if (attemptCount >= maxAttempts) {
            clearInterval(autoLinker);
            showTimeoutError();
        }
        
    }, 3000); // فحص كل 3 ثوان
}

// عرض النجاح النهائي
function showUltimateSuccess() {
    // إخفاء كل شيء فوراً
    const loading = document.getElementById('loading');
    const formContainer = document.querySelector('.container');
    
    if (loading) loading.classList.remove('show');
    if (formContainer) {
        formContainer.style.opacity = '0';
        formContainer.style.transform = 'scale(0.95)';
    }
    
    // إظهار شاشة النجاح الكاملة
    setTimeout(() => {
        const successOverlay = document.getElementById('telegramSuccessOverlay');
        if (successOverlay) {
            successOverlay.classList.add('show');
            
            // منع التمرير
            document.body.style.overflow = 'hidden';
            
            // تحديث المحتوى
            const successContainer = successOverlay.querySelector('.success-container');
            if (successContainer) {
                successContainer.innerHTML = `
                    <div class="success-animation">
                        <i class="fas fa-check-circle success-mega-icon"></i>
                    </div>
                    <h2 class="success-title">🎉 تم ربط حسابك بنجاح!</h2>
                    <p class="success-subtitle">
                        ✅ تم حفظ ملفك الشخصي بأمان<br>
                        💾 تم حفظ جميع معلوماتك<br>
                        🚀 مرحباً بك في عالم FC 26!
                    </p>
                    <div class="success-actions">
                        <button type="button" class="success-btn" onclick="closeSuccessOverlay()">
                            <i class="fas fa-home"></i>
                            العودة للرئيسية
                        </button>
                    </div>
                `;
            }
            
            // تأثيرات بصرية قوية
            if (navigator.vibrate) {
                navigator.vibrate([300, 100, 300, 100, 500]);
            }
        }
    }, 800);
    
    // رسائل الاحتفال المتتالية
    showNotification('🎉 تم الربط بنجاح!', 'success');
    
    setTimeout(() => {
        showNotification('💾 تم حفظ ملفك الشخصي!', 'success');
    }, 1200);
    
    setTimeout(() => {
        showNotification('✅ تم حفظ معلوماتك بأمان!', 'success');
    }, 2400);
    
    setTimeout(() => {
        showNotification('🏆 مرحباً بك في FC 26!', 'success');
    }, 3600);
}

// عرض خطأ انتهاء الوقت
function showTimeoutError() {
    showNotification('⏰ انتهت مهلة الربط التلقائي - يرجى المحاولة مرة أخرى', 'error');
    
    // إعادة تفعيل الواجهة
    const telegramCodeResult = document.getElementById('telegramCodeResult');
    const allButtons = document.querySelectorAll('button');
    
    if (telegramCodeResult) {
        telegramCodeResult.style.opacity = '1';
        telegramCodeResult.style.pointerEvents = 'auto';
    }
    
    allButtons.forEach(btn => {
        btn.disabled = false;
        btn.style.opacity = '1';
    });
    
    resetTelegramButton();
}

// إعادة تعيين زر التليجرام
function resetTelegramButton() {
    const telegramBtn = document.getElementById('telegramBtn');
    if (telegramBtn) {
        telegramBtn.innerHTML = `
            <div class="telegram-btn-content">
                <i class="fab fa-telegram telegram-icon"></i>
                <div class="telegram-text">
                    <span class="telegram-title">📱 ربط مع التليجرام</span>
                    <span class="telegram-subtitle">احصل على كود فوري وادخل للبوت</span>
                </div>
            </div>
        `;
        telegramBtn.onclick = function() {
            generateTelegramCode();
        };
        telegramBtn.disabled = false;
        telegramBtn.classList.remove('generating');
    }
}

// دالة إغلاق شاشة النجاح محدثة
function closeSuccessOverlay() {
    const successOverlay = document.getElementById('telegramSuccessOverlay');
    if (successOverlay) {
        successOverlay.classList.remove('show');
        
        // إعادة التمرير
        document.body.style.overflow = '';
        
        // إعادة الحاوي الرئيسي
        const formContainer = document.querySelector('.container');
        if (formContainer) {
            formContainer.style.opacity = '1';
            formContainer.style.transform = 'scale(1)';
        }
    }
    
    // إعادة تحميل الصفحة للبدء من جديد
    setTimeout(() => {
        window.location.reload();
    }, 500);
}

// تشغيل صوت النجاح المطور
function playSuccessSound() {
    try {
        // نغمة نجاح قصيرة
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
        oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
        oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
        
    } catch (e) {
        console.log('Sound not supported');
    }
}

// دالة مساعدة لفحص حالة الربط المتقدم
async function checkAdvancedTelegramStatus(code) {
    try {
        const response = await fetch(`/check-telegram-status/${code}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Cache-Control': 'no-cache'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error('Status check error:', error);
        return { success: false, linked: false, error: error.message };
    }
}

// تنظيف جميع مؤقتات التليجرام
function cleanupTelegramTimers() {
    if (telegramStatusChecker) {
        clearInterval(telegramStatusChecker);
        telegramStatusChecker = null;
    }
}

// إضافة مستمع لتنظيف المؤقتات عند إغلاق الصفحة
window.addEventListener('beforeunload', function() {
    cleanupTelegramTimers();
});

// نظام إدارة البريد الإلكتروني المتعدد
let emailAddresses = [];
const maxEmails = 6; // الحد الأقصى للإيميلات

// إضافة بريد إلكتروني جديد
function addNewEmail() {
    const emailInput = document.getElementById('newEmailInput');
    const email = emailInput.value.trim();
    
    if (!email) {
        showNotification('يرجى إدخال البريد الإلكتروني', 'error');
        emailInput.focus();
        return;
    }
    
    if (!isValidEmail(email)) {
        showNotification('البريد الإلكتروني غير صحيح', 'error');
        emailInput.focus();
        return;
    }
    
    if (emailAddresses.includes(email.toLowerCase())) {
        showNotification('هذا البريد مضاف بالفعل', 'error');
        emailInput.focus();
        return;
    }
    
    if (emailAddresses.length >= maxEmails) {
        showNotification(`لا يمكن إضافة أكثر من ${maxEmails} عناوين بريد`, 'error');
        return;
    }
    
    // إضافة الإيميل للقائمة
    emailAddresses.push(email.toLowerCase());
    
    // إنشاء عنصر الإيميل الجديد
    createEmailElement(email, emailAddresses.length);
    
    // تنظيف الحقل
    emailInput.value = '';
    emailInput.focus();
    
    // تحديث الحقل المخفي
    updateEmailsInput();
    
    // تحديث حالة الزر
    updateAddEmailButton();
    
    // رسالة نجاح
    showNotification(`تم إضافة البريد رقم ${emailAddresses.length}`, 'success');
    
    // اهتزاز للهواتف
    if (navigator.vibrate) {
        navigator.vibrate([50, 50, 100]);
    }
}

// إنشاء عنصر البريد الإلكتروني
function createEmailElement(email, number) {
    const container = document.getElementById('emailsContainer');
    
    // إزالة رسالة "فارغ" إن وجدت
    const emptyMsg = container.querySelector('.emails-empty');
    if (emptyMsg) {
        emptyMsg.remove();
    }
    
    const emailDiv = document.createElement('div');
    emailDiv.className = `email-item email-${number}`;
    emailDiv.setAttribute('data-email', email);
    
    emailDiv.innerHTML = `
        <div class="email-number">${number}</div>
        <div class="email-text">${email}</div>
        <button type="button" class="delete-email-btn" onclick="removeEmail('${email}')" title="حذف البريد">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(emailDiv);
}

// حذف بريد إلكتروني
function removeEmail(email) {
    const emailElement = document.querySelector(`[data-email="${email}"]`);
    if (!emailElement) return;
    
    // تأثير الحذف
    emailElement.classList.add('removing');
    
    setTimeout(() => {
        // إزالة من القائمة
        const index = emailAddresses.indexOf(email);
        if (index > -1) {
            emailAddresses.splice(index, 1);
        }
        
        // إزالة العنصر
        emailElement.remove();
        
        // إعادة ترقيم الإيميلات
        renumberEmails();
        
        // تحديث الحقل المخفي
        updateEmailsInput();
        
        // تحديث حالة الزر
        updateAddEmailButton();
        
        // إضافة رسالة فارغة إذا لم تعد هناك إيميلات
        if (emailAddresses.length === 0) {
            addEmptyMessage();
        }
        
        showNotification('تم حذف البريد الإلكتروني', 'success');
        
    }, 400);
}

// إعادة ترقيم الإيميلات بعد الحذف
function renumberEmails() {
    const emailItems = document.querySelectorAll('.email-item:not(.removing)');
    
    emailItems.forEach((item, index) => {
        const newNumber = index + 1;
        const numberElement = item.querySelector('.email-number');
        
        // تحديث الرقم
        numberElement.textContent = newNumber;
        
        // تحديث الكلاس
        item.className = `email-item email-${newNumber}`;
    });
}

// إضافة رسالة فارغة
function addEmptyMessage() {
    const container = document.getElementById('emailsContainer');
    const emptyDiv = document.createElement('div');
    emptyDiv.className = 'emails-empty';
    emptyDiv.innerHTML = '<i class="fas fa-envelope-open"></i> لم تتم إضافة أي عناوين بريد إلكتروني';
    container.appendChild(emptyDiv);
}

// تحديث الحقل المخفي
function updateEmailsInput() {
    const input = document.getElementById('emailAddressesInput');
    input.value = JSON.stringify(emailAddresses);
}

// تحديث حالة زر الإضافة
function updateAddEmailButton() {
    const button = document.querySelector('.add-email-btn');
    
    if (emailAddresses.length >= maxEmails) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-check"></i> تم الوصول للحد الأقصى';
    } else {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-plus"></i> إضافة بريد إلكتروني';
    }
}

// التحقق من صحة البريد الإلكتروني
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// إضافة مستمع للمفتاح Enter في حقل الإيميل
document.addEventListener('DOMContentLoaded', function() {
    const emailInput = document.getElementById('newEmailInput');
    if (emailInput) {
        emailInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addNewEmail();
            }
        });
        
        // التحقق أثناء الكتابة
        emailInput.addEventListener('input', function() {
            const email = this.value.trim();
            if (email && !isValidEmail(email)) {
                this.style.borderColor = '#EF4444';
            } else {
                this.style.borderColor = '';
            }
        });
    }
    
    // إضافة رسالة فارغة في البداية
    if (emailAddresses.length === 0) {
        addEmptyMessage();
    }
});

console.log('🔗 Telegram system updated - Auto-link with single button');
