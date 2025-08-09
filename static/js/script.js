// FC 26 Profile Setup - كود JavaScript مدمج كامل
// دمج متقدم لكودين مع جميع الميزات والتحسينات + حل مشكلة الأزرار

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

// متغيرات البريد الإلكتروني
let emailAddresses = [];
const maxEmails = 6;

// 🔧 تهيئة التطبيق مع ضمان التحميل الكامل - حل مشكلة الأزرار
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Starting FC 26 Profile Setup - Fixed Buttons Version...');
    
    // انتظار قصير للتأكد من تحميل كامل عناصر DOM
    setTimeout(() => {
        initializeApp();
    }, 100);
});

function initializeApp() {
    console.log('🔧 Initializing app components...');
    
    try {
        // إنشاء الجسيمات المتحركة
        createParticles();
        
        // تهيئة جميع مستمعي الأحداث - الحل الرئيسي
        initializeEventListeners();
        
        // تحسين الأداء للهواتف
        if (window.innerWidth <= 768) {
            optimizeForMobile();
        }
        
        // تهيئة الميزات المتقدمة
        initializeAdvancedFeatures();
        
        console.log('✅ App initialized successfully with fixed buttons!');
        
    } catch (error) {
        console.error('❌ Error during app initialization:', error);
    }
}

// 🚀 الحل الرئيسي لمشكلة الأزرار - مأخوذ من كود صحبك
function initializeEventListeners() {
    console.log('🎯 Setting up event listeners with button fix...');
    
    // تهيئة أزرار المنصات - الحل الأساسي
    setupPlatformButtons();
    
    // تهيئة أزرار طرق الدفع - الحل الأساسي  
    setupPaymentButtons();
    
    // تهيئة حقل الواتساب
    setupWhatsAppInput();
    
    // تهيئة النموذج
    setupFormSubmission();
    
    // تهيئة زر التليجرام
    setupTelegramButton();
    
    // تهيئة الميزات الأخرى
    setupDynamicInputs();
    setupEnterKeyHandling();
    
    console.log('✅ All event listeners set up successfully with button fixes!');
}

// 🎮 حل مشكلة أزرار المنصات - مع إصلاح التمرير الكامل
function setupPlatformButtons() {
    console.log('🎮 Setting up platform buttons with SCROLL fix...');
    
    const platformCards = document.querySelectorAll('.platform-card');
    
    if (platformCards.length === 0) {
        console.warn('⚠️ No platform cards found!');
        return;
    }
    
    platformCards.forEach((card, index) => {
        console.log(`Setting up platform card ${index + 1}:`, card.dataset.platform);
        
        // إزالة مستمعين قدامى
        const newCard = card.cloneNode(true);
        card.parentNode.replaceChild(newCard, card);
        
        // ✅ متغيرات لتتبع اللمس
        let touchStartY = 0;
        let touchStartTime = 0;
        let hasMoved = false;
        
        // مستمع النقر العادي للكمبيوتر
        newCard.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            handlePlatformSelection(this);
        });
        
        // ✅ الحل الذكي: تتبع بداية اللمس
        newCard.addEventListener('touchstart', function(e) {
            // حفظ موضع اللمس والوقت
            touchStartY = e.touches[0].clientY;
            touchStartTime = Date.now();
            hasMoved = false;
            
            // تأثير بصري خفيف
            this.style.transition = 'transform 0.1s ease, opacity 0.1s ease';
            this.style.transform = 'scale(0.98)';
            this.style.opacity = '0.9';
            
        }, { passive: true }); // 🔥 passive: true = يسمح بالتمرير
        
        // ✅ تتبع حركة اللمس
        newCard.addEventListener('touchmove', function(e) {
            const currentY = e.touches[0].clientY;
            const moveDistance = Math.abs(currentY - touchStartY);
            
            // إذا تحرك أكثر من 10 بكسل = تمرير
            if (moveDistance > 10) {
                hasMoved = true;
                // إزالة التأثير البصري
                this.style.transform = '';
                this.style.opacity = '';
            }
        }, { passive: true });
        
        // ✅ معالجة نهاية اللمس
        newCard.addEventListener('touchend', function(e) {
            e.preventDefault(); // منع النقر المزدوج فقط
            
            const touchEndTime = Date.now();
            const touchDuration = touchEndTime - touchStartTime;
            
            // إزالة التأثير البصري
            this.style.transform = '';
            this.style.opacity = '';
            
            // ✅ شروط الاختيار الذكية
            if (!hasMoved && touchDuration < 300) {
                // لمسة سريعة بدون حركة = اختيار
                handlePlatformSelection(this);
            }
            // إذا تحرك = تمرير عادي ولا نفعل شيء
            
        }, { passive: false }); // نحتاج منع النقر المزدوج فقط
        
        // معالج الإلغاء (عند مغادرة المنطقة)
        newCard.addEventListener('touchcancel', function(e) {
            this.style.transform = '';
            this.style.opacity = '';
            hasMoved = false;
        }, { passive: true });
    });
    
    console.log(`✅ ${platformCards.length} platform buttons fixed for scrolling and clicking`);
}

// 💳 حل مشكلة أزرار الدفع - مع إصلاح التمرير الكامل
function setupPaymentButtons() {
    console.log('💳 Setting up payment buttons with SCROLL fix...');
    
    const paymentButtons = document.querySelectorAll('.payment-btn');
    
    if (paymentButtons.length === 0) {
        console.warn('⚠️ No payment buttons found!');
        return;
    }
    
    paymentButtons.forEach((btn, index) => {
        console.log(`Setting up payment button ${index + 1}:`, btn.dataset.value);
        
        // إزالة مستمعين قدامى
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
        
        // ✅ متغيرات لتتبع اللمس
        let touchStartY = 0;
        let touchStartTime = 0;
        let hasMoved = false;
        
        // مستمع النقر العادي للكمبيوتر
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            handlePaymentSelection(this);
        });
        
        // ✅ الحل الذكي: تتبع بداية اللمس
        newBtn.addEventListener('touchstart', function(e) {
            // حفظ موضع اللمس والوقت
            touchStartY = e.touches[0].clientY;
            touchStartTime = Date.now();
            hasMoved = false;
            
            // تأثير بصري خفيف
            this.style.transition = 'transform 0.1s ease, opacity 0.1s ease';
            this.style.transform = 'scale(0.98)';
            this.style.opacity = '0.9';
            
        }, { passive: true }); // 🔥 passive: true = يسمح بالتمرير
        
        // ✅ تتبع حركة اللمس  
        newBtn.addEventListener('touchmove', function(e) {
            const currentY = e.touches[0].clientY;
            const moveDistance = Math.abs(currentY - touchStartY);
            
            // إذا تحرك أكثر من 10 بكسل = تمرير
            if (moveDistance > 10) {
                hasMoved = true;
                // إزالة التأثير البصري
                this.style.transform = '';
                this.style.opacity = '';
            }
        }, { passive: true });
        
        // ✅ معالجة نهاية اللمس
        newBtn.addEventListener('touchend', function(e) {
            e.preventDefault(); // منع النقر المزدوج فقط
            
            const touchEndTime = Date.now();
            const touchDuration = touchEndTime - touchStartTime;
            
            // إزالة التأثير البصري
            this.style.transform = '';
            this.style.opacity = '';
            
            // ✅ شروط الاختيار الذكية
            if (!hasMoved && touchDuration < 300) {
                // لمسة سريعة بدون حركة = اختيار
                handlePaymentSelection(this);
            }
            // إذا تحرك = تمرير عادي ولا نفعل شيء
            
        }, { passive: false }); // نحتاج منع النقر المزدوج فقط
        
        // معالج الإلغاء (عند مغادرة المنطقة)
        newBtn.addEventListener('touchcancel', function(e) {
            this.style.transform = '';
            this.style.opacity = '';
            hasMoved = false;
        }, { passive: true });
    });
    
    console.log(`✅ ${paymentButtons.length} payment buttons fixed for scrolling and clicking`);
}


// 🎮 معالجة اختيار المنصة - محسن من كود صحبك
function handlePlatformSelection(card) {
    console.log('🎮 Platform selected:', card.dataset.platform);
    
    const platform = card.dataset.platform;
    
    // إزالة التحديد من جميع البطاقات
    document.querySelectorAll('.platform-card').forEach(c => {
        c.classList.remove('selected');
        c.style.transform = '';
        c.style.boxShadow = '';
    });
    
    // تحديد البطاقة المختارة
    card.classList.add('selected');
    card.style.transform = 'scale(1.05)';
    card.style.boxShadow = '0 8px 25px rgba(255, 144, 0, 0.4)';
    
    // حفظ القيمة
    const platformInput = document.getElementById('platform');
    if (platformInput) {
        platformInput.value = platform;
        console.log('✅ Platform saved:', platform);
    }
    
    // تحديث حالة التحقق
    validationStates.platform = true;
    checkFormValidity();
    
    // اهتزاز للهواتف
    if (navigator.vibrate) {
        navigator.vibrate([50, 30, 50]);
    }
    
    // إشعار بصري
    showNotification(`تم اختيار منصة ${getPlatformDisplayName(platform)}`, 'success');
}

// 💳 معالجة اختيار الدفع - محسن من كود صحبك
function handlePaymentSelection(btn) {
    console.log('💳 Payment selected:', btn.dataset.value);
    
    const paymentType = btn.dataset.type;
    const paymentValue = btn.dataset.value;
    
    // إزالة التحديد من جميع الأزرار
    document.querySelectorAll('.payment-btn').forEach(b => {
        b.classList.remove('selected');
        b.style.transform = '';
        b.style.background = '';
    });
    
    // تحديد الزر المختار
    btn.classList.add('selected');
    btn.style.transform = 'scale(1.03)';
    
    // حفظ القيمة
    const paymentMethodInput = document.getElementById('payment_method');
    if (paymentMethodInput) {
        paymentMethodInput.value = paymentValue;
        console.log('✅ Payment method saved:', paymentValue);
    }
    
    // إخفاء جميع الحقول الديناميكية
    document.querySelectorAll('.dynamic-input').forEach(input => {
        input.classList.remove('show');
        input.style.display = 'none';
    });
    
    // إظهار الحقل المناسب
    showPaymentInputField(paymentType);
    
    // تحديث حالة التحقق
    validationStates.paymentMethod = true;
    checkFormValidity();
    
    // اهتزاز للهواتف
    if (navigator.vibrate) {
        navigator.vibrate([30, 20, 30]);
    }
    
    // إشعار بصري
    showNotification(`تم اختيار ${paymentValue}`, 'success');
}

function showPaymentInputField(paymentType) {
    let targetInputId;
    
    switch(paymentType) {
        case 'mobile':
            targetInputId = 'mobile-input';
            break;
        case 'card':
            targetInputId = 'card-input';
            break;
        case 'link':
            targetInputId = 'link-input';
            break;
        default:
            console.warn('Unknown payment type:', paymentType);
            return;
    }
    
    const targetInput = document.getElementById(targetInputId);
    if (targetInput) {
        setTimeout(() => {
            targetInput.style.display = 'block';
            targetInput.classList.add('show');
            
            const inputField = targetInput.querySelector('input');
            if (inputField) {
                inputField.required = true;
                inputField.focus();
            }
        }, 200);
        
        console.log('✅ Payment input field shown:', targetInputId);
    }
}

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

// إعداد حقل رقم الواتساب
function setupWhatsAppInput() {
    const whatsappInput = document.getElementById('whatsapp');
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
    
    // نظام تيلدا المحسن - تنسيق متطور للبطاقات
    initializeTeldaCardSystem();
}

// نظام تيلدا المحسن - تنسيق متطور للبطاقات
function initializeTeldaCardSystem() {
    const teldaInput = document.getElementById('telda_card') || document.getElementById('card-number');
    if (!teldaInput) return;
    
    // إضافة أيقونة تيلدا
    const inputContainer = teldaInput.parentNode;
    if (!inputContainer.querySelector('.telda-icon')) {
        const teldaIcon = document.createElement('div');
        teldaIcon.className = 'telda-icon';
        teldaIcon.innerHTML = '<i class="fas fa-credit-card"></i>';
        inputContainer.style.position = 'relative';
        inputContainer.appendChild(teldaIcon);
    }
    
    // معالج الإدخال المحسن
    teldaInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/[^\d]/g, ''); // أرقام فقط
        let formattedValue = '';
        
        // تنسيق بصيغة 1234-5678-9012-3456
        for (let i = 0; i < value.length; i += 4) {
            if (i > 0) formattedValue += '-';
            formattedValue += value.substr(i, 4);
        }
        
        // تحديد طول مناسب (16 رقم + 3 شرطات = 19 حرف)
        if (formattedValue.length <= 19) {
            e.target.value = formattedValue;
        }
        
        // التحقق الفوري
        validateTeldaCard(e.target);
        addTeldaVisualEffects(e.target, value);
        checkFormValidity();
    });
    
    // معالج اللصق المحسن
    teldaInput.addEventListener('paste', function(e) {
        e.preventDefault();
        let pastedText = (e.clipboardData || window.clipboardData).getData('text');
        let numbers = pastedText.replace(/[^\d]/g, '');
        
        if (numbers.length <= 16) {
            this.value = numbers;
            this.dispatchEvent(new Event('input'));
        }
    });
    
    // تأثيرات التركيز
    teldaInput.addEventListener('focus', function() {
        this.parentNode.classList.add('telda-focused');
    });
    
    teldaInput.addEventListener('blur', function() {
        this.parentNode.classList.remove('telda-focused');
        finalTeldaValidation(this);
    });
}

// التحقق من صحة كارت تيلدا
function validateTeldaCard(input) {
    const value = input.value;
    const numbersOnly = value.replace(/[^\d]/g, '');
    const container = input.parentNode;
    
    // إزالة تأثيرات سابقة
    container.classList.remove('telda-valid', 'telda-invalid', 'telda-partial');
    
    if (numbersOnly.length === 0) {
        return;
    } else if (numbersOnly.length < 16) {
        container.classList.add('telda-partial');
        showTeldaStatus(input, 'جاري الكتابة...', 'partial');
    } else if (numbersOnly.length === 16) {
        container.classList.add('telda-valid');
        showTeldaStatus(input, '✅ رقم كارت صحيح', 'valid');
        
        // اهتزاز نجاح
        if (navigator.vibrate) {
            navigator.vibrate([50, 30, 50]);
        }
    } else {
        container.classList.add('telda-invalid');
        showTeldaStatus(input, '❌ رقم طويل جداً', 'invalid');
    }
}

// التحقق النهائي لكارت تيلدا
function finalTeldaValidation(input) {
    const numbersOnly = input.value.replace(/[^\d]/g, '');
    
    if (numbersOnly.length > 0 && numbersOnly.length !== 16) {
        showTeldaStatus(input, '⚠️ رقم كارت تيلدا يجب أن يكون 16 رقم', 'invalid');
    }
}

// عرض حالة تيلدا
function showTeldaStatus(input, message, type) {
    const existingStatus = input.parentNode.querySelector('.telda-status');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    if (!message) return;
    
    const statusDiv = document.createElement('div');
    statusDiv.className = `telda-status telda-${type}`;
    statusDiv.textContent = message;
    
    input.parentNode.appendChild(statusDiv);
    
    setTimeout(() => {
        statusDiv.classList.add('show');
    }, 100);
    
    // إزالة تلقائية بعد 3 ثوان للرسائل الجزئية
    if (type === 'partial') {
        setTimeout(() => {
            if (statusDiv.parentNode) {
                statusDiv.classList.remove('show');
                setTimeout(() => statusDiv.remove(), 300);
            }
        }, 3000);
    }
}

// تأثيرات بصرية لتيلدا
function addTeldaVisualEffects(input, numbersValue) {
    const container = input.parentNode;
    
    // تأثير النبض للأرقام الجديدة
    if (numbersValue.length > 0 && numbersValue.length % 4 === 0) {
        container.classList.add('telda-pulse');
        setTimeout(() => {
            container.classList.remove('telda-pulse');
        }, 200);
    }
    
    // شريط التقدم
    updateTeldaProgressBar(input, numbersValue.length);
}

// شريط تقدم تيلدا
function updateTeldaProgressBar(input, length) {
    let progressBar = input.parentNode.querySelector('.telda-progress');
    
    if (!progressBar) {
        progressBar = document.createElement('div');
        progressBar.className = 'telda-progress';
        progressBar.innerHTML = '<div class="telda-progress-fill"></div>';
        input.parentNode.appendChild(progressBar);
    }
    
    const progressFill = progressBar.querySelector('.telda-progress-fill');
    const percentage = Math.min((length / 16) * 100, 100);
    
    progressFill.style.width = percentage + '%';
    
    // ألوان مختلفة حسب التقدم
    if (percentage < 25) {
        progressFill.style.background = '#ef4444';
    } else if (percentage < 50) {
        progressFill.style.background = '#f97316';
    } else if (percentage < 75) {
        progressFill.style.background = '#eab308';
    } else if (percentage < 100) {
        progressFill.style.background = '#22c55e';
    } else {
        progressFill.style.background = '#10b981';
    }
}

// التحقق الشامل من طرق الدفع - FIXED للتيلدا وإنستا باي
function validatePaymentMethod() {
    console.log('🔍 Checking payment method validation...');
    
    // الحصول على طريقة الدفع المختارة
    const selectedPaymentMethod = document.getElementById('payment_method')?.value;
    console.log('Selected payment method:', selectedPaymentMethod);
    
    if (!selectedPaymentMethod) {
        console.log('❌ No payment method selected');
        validationStates.paymentMethod = false;
        return false;
    }
    
    // ✅ التحقق الذكي حسب نوع الدفع المختار
    let hasValidPayment = false;
    let activeInput = null;
    
    // البحث عن الحقل النشط بناءً على طريقة الدفع
    if (['vodafone_cash', 'etisalat_cash', 'orange_cash', 'we_cash', 'bank_wallet'].includes(selectedPaymentMethod)) {
        // محافظ إلكترونية - البحث في mobile-number
        activeInput = document.getElementById('mobile-number');
        console.log('Checking mobile wallet input:', activeInput?.value);
        
    } else if (selectedPaymentMethod === 'tilda') {
        // كارت تيلدا - البحث في card-number  
        activeInput = document.getElementById('card-number');
        console.log('Checking Telda card input:', activeInput?.value);
        
    } else if (selectedPaymentMethod === 'instapay') {
        // إنستا باي - البحث في payment-link
        activeInput = document.getElementById('payment-link');
        console.log('Checking InstaPay link input:', activeInput?.value);
    }
    
    // ✅ التحقق من الحقل النشط فقط
    if (activeInput && activeInput.closest('.dynamic-input').classList.contains('show')) {
        const inputValue = activeInput.value.trim();
        console.log('Active input value:', inputValue);
        
        if (inputValue) {
            // التحقق من صحة القيمة المدخلة
            const isInputValid = validatePaymentInput(activeInput);
            console.log('Input validation result:', isInputValid);
            
            if (isInputValid) {
                hasValidPayment = true;
                console.log('✅ Valid payment data found!');
            } else {
                console.log('❌ Invalid payment data');
            }
        } else {
            console.log('⚠️ Input is empty');
        }
    } else {
        console.log('❌ No active input found or input not visible');
    }
    
    // ✅ تحديث حالة التحقق
    validationStates.paymentMethod = hasValidPayment;
    console.log('Final payment validation state:', hasValidPayment);
    
    return hasValidPayment;
}

// ✅ أضف الدالة دي في أي مكان في الكود (بعد الدوال الموجودة)
function validatePaymentInput(input) {
    const value = input.value.trim();
    const inputId = input.id;
    let isValid = false;
    let errorMessage = '';
    
    console.log(`🔍 Validating ${inputId} with value:`, value);
    
    if (!value) {
        updateValidationUI(input, true, ''); // فارغ = صحيح للحقول الاختيارية
        return true;
    }
    
    // ✅ التحقق المحسن من المحافظ الإلكترونية (11 رقم)
    if (inputId === 'mobile-number') {
        isValid = /^01[0125][0-9]{8}$/.test(value) && value.length === 11;
        errorMessage = isValid ? '' : 'رقم المحفظة يجب أن يكون 11 رقم ويبدأ بـ 010، 011، 012، أو 015';
        console.log('Mobile validation:', isValid);
    }
    // ✅ التحقق المحسن من كارت تيلدا (16 رقم)
    else if (inputId === 'card-number') {
        // إزالة الشرطات والمسافات
        const numbersOnly = value.replace(/[-\s]/g, '');
        isValid = /^\d{16}$/.test(numbersOnly);
        errorMessage = isValid ? '' : 'رقم كارت تيلدا يجب أن يكون 16 رقم';
        console.log('Telda card validation:', isValid, 'Numbers only:', numbersOnly);
    }
    // ✅ التحقق الذكي من رابط إنستا باي (مع الاستخلاص)
    else if (inputId === 'payment-link') {
        const extractedLink = extractInstapayLink(value);
        isValid = !!extractedLink;
        errorMessage = isValid ? '' : 'لم يتم العثور على رابط InstaPay صحيح في النص';
        console.log('InstaPay validation:', isValid, 'Extracted:', extractedLink);
        
        // تحديث قيمة الحقل للرابط المستخلص إذا كان مختلف
        if (isValid && extractedLink && extractedLink !== value) {
            input.value = extractedLink;
            showInstapayExtractionNotice(input, value, extractedLink);
            console.log('Updated input value to extracted link');
        }
        
        // عرض معلومات الرابط
        if (isValid && extractedLink) {
            const linkInfo = extractInstapayInfo(extractedLink);
            showInstapayLinkInfo(input, linkInfo);
        }
    }
    
    updateValidationUI(input, isValid, errorMessage);
    console.log(`✅ ${inputId} validation result:`, isValid);
    return isValid;
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
    console.log('🔍 Checking complete form validity...');
    
    // التحقق من جميع المتطلبات
    const platform = document.getElementById('platform')?.value;
    const whatsapp = document.getElementById('whatsapp')?.value;
    const paymentMethod = document.getElementById('payment_method')?.value;
    
    // تحديث حالات التحقق
    validationStates.platform = !!platform;
    console.log('Platform valid:', validationStates.platform);
    
    // التحقق من صحة الواتساب من المعلومات المعروضة
    const phoneInfo = document.querySelector('.phone-info.success-info');
    validationStates.whatsapp = !!(whatsapp && phoneInfo);
    console.log('WhatsApp valid:', validationStates.whatsapp);
    
    // ✅ التحقق المحسن من طرق الدفع
    validatePaymentMethod();
    console.log('Payment method valid:', validationStates.paymentMethod);
    
    // التحقق النهائي
    const isValid = validationStates.platform && validationStates.whatsapp && validationStates.paymentMethod;
    console.log('🎯 Final form validity:', isValid);
    
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
function setupFormSubmission() {
    const form = document.getElementById('profileForm');
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
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الحفظ والربط...';
    }
    
    // اهتزاز للهواتف
    if (navigator.vibrate) {
        navigator.vibrate([100, 50, 100]);
    }
    
    try {
        const formData = new FormData(e.target);
        
        const response = await fetch('/update-profile', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        const result = await response.json();
        
        // إخفاء شاشة التحميل
        if (loading) loading.classList.remove('show');
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        
        // ✅ الكود الجديد المبسط - استبدل به الجزء المحذوف
        if (response.ok && result.success) {
            // عرض رسالة النجاح
            let successText = '✅ تم حفظ بياناتك بنجاح!';
            if (result.data && result.data.whatsapp_number) {
                successText += `<br><small>رقم الواتساب: ${result.data.whatsapp_number}</small>`;
            }
            
            if (successMessage) {
                successMessage.innerHTML = successText;
                successMessage.classList.add('show');
            } else {
                showNotification('تم إرسال البيانات بنجاح!', 'success');
            }
            
            // اهتزاز نجاح
            if (navigator.vibrate) {
                navigator.vibrate([200, 100, 200]);
            }
            
            // الانتقال التلقائي بعد ثانيتين
            setTimeout(() => {
                window.location.href = result.next_step || '/coins-order';
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

// 🔧 إعداد زر التليجرام - مع الحل المحسن
function setupTelegramButton() {
    console.log('📱 Setting up Telegram button with fix...');
    
    const telegramBtn = document.getElementById('telegram-link-btn');
    if (telegramBtn) {
        // إزالة مستمعين قدامى
        const newBtn = telegramBtn.cloneNode(true);
        telegramBtn.parentNode.replaceChild(newBtn, telegramBtn);
        
        // إضافة مستمع جديد
        newBtn.addEventListener('click', handleTelegramLink);
        console.log('✅ Telegram button fixed and initialized');
    } else {
        console.warn('⚠️ Telegram button not found');
    }
}

// معالجة زر التليجرام - النسخة المصححة النهائية
async function handleTelegramLink() {
    console.log('🔍 بدء معالجة زر التليجرام...');
    
    const telegramBtn = document.getElementById('telegram-link-btn');
    if (!telegramBtn) {
        console.error('❌ زر التليجرام غير موجود');
        return;
    }
    
    // طباعة حالة التحقق الحالية للتشخيص
    console.log('📊 حالة التحقق الحالية:');
    console.log('  - المنصة:', validationStates.platform);
    console.log('  - الواتساب:', validationStates.whatsapp);
    console.log('  - طريقة الدفع:', validationStates.paymentMethod);
    
    // ✅ التحقق الصحيح - استخدام whatsapp بدلاً من phone
    if (!validationStates.platform || !validationStates.whatsapp) {
        console.log('❌ البيانات غير مكتملة');
        
        // تغيير نص الزر للخطأ
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
        showNotification('يرجى اختيار المنصة والتحقق من رقم الواتساب أولاً', 'error');
        
        // إعادة النص الأصلي بعد 3 ثوان
        setTimeout(() => {
            telegramBtn.innerHTML = originalContent;
            telegramBtn.classList.remove('error');
        }, 3000);
        
        return;
    }
    
    console.log('✅ البيانات مكتملة، بدء عملية الربط...');
    
    // تعطيل الزر وإظهار التحميل
    telegramBtn.disabled = true;
    const originalContent = telegramBtn.innerHTML;
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
    
    try {
        // جمع البيانات للإرسال
        const platform = document.getElementById('platform').value;
        const whatsapp = document.getElementById('whatsapp').value;
        const paymentMethod = document.getElementById('payment_method').value;
        const paymentDetails = getActivePaymentDetails();
        
        console.log('📤 إرسال البيانات:', {
            platform,
            whatsapp: whatsapp.substring(0, 5) + '***',
            paymentMethod
        });
        
        // إرسال الطلب للخادم
        const response = await fetch('/generate-telegram-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                platform: platform,
                whatsapp_number: whatsapp,
                payment_method: paymentMethod,
                payment_details: paymentDetails
            })
        });
        
        const data = await response.json();
        console.log('📥 استجابة الخادم:', data);
        
        if (data.success && data.telegram_web_url) {
            // فتح التليجرام بالطريقة الذكية
            console.log('🔗 فتح التليجرام بالطريقة المتدرجة:', data);
            openTelegramSmartly(data); // ✅ هذا هو السطر الجديد والصحيح    

            // إرشادات إضافية للمستخدم
            const instructionText = `
               📱 إذا لم يظهر الكود تلقائياً:
               1️⃣ اكتب: /start
               2️⃣ ثم اكتب: ${data.telegram_code}
               3️⃣ أو انسخ هذا الكود: ${data.telegram_code}
    `;
            console.log(instructionText);
            // تحديث الزر للنجاح
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
            
            // مراقبة الربط
            monitorTelegramLinking(data.code);
            
            // إعادة الزر للوضع الطبيعي بعد 5 ثوان
            setTimeout(() => {
                telegramBtn.innerHTML = originalContent;
                telegramBtn.classList.remove('success');
                telegramBtn.disabled = false;
            }, 5000);
            
        } else {
            throw new Error(data.message || 'خطأ في الخادم');
        }
        
    } catch (error) {
        console.error('❌ خطأ في التليجرام:', error);
        
        // عرض رسالة الخطأ
        telegramBtn.innerHTML = `
            <div class="telegram-btn-content">
                <i class="fas fa-exclamation-triangle telegram-icon" style="color: #ff9000;"></i>
                <div class="telegram-text">
                    <span class="telegram-title">❌ خطأ - اضغط للمحاولة مرة أخرى</span>
                    <span class="telegram-subtitle">${error.message}</span>
                </div>
            </div>
        `;
        telegramBtn.classList.remove('generating');
        telegramBtn.classList.add('error');
        
        showNotification('خطأ في الاتصال، يرجى المحاولة مرة أخرى', 'error');
        
        // إعادة الزر للوضع الطبيعي بعد 3 ثوان
        setTimeout(() => {
            telegramBtn.innerHTML = originalContent;
            telegramBtn.classList.remove('error');
            telegramBtn.disabled = false;
        }, 3000);
    }
}

// دالة مساعدة للحصول على تفاصيل الدفع النشطة
function getActivePaymentDetails() {
    const paymentMethod = document.getElementById('payment_method').value;
    
    if (paymentMethod.includes('cash') || paymentMethod === 'bank_wallet') {
        return document.getElementById('mobile-number')?.value || '';
    } else if (paymentMethod === 'tilda') {
        return document.getElementById('card-number')?.value || '';
    } else if (paymentMethod === 'instapay') {
        return document.getElementById('payment-link')?.value || '';
    }
    
    return '';
}


function monitorTelegramLinking(telegramCode) {
    const checkInterval = setInterval(async () => {
        try {
            const checkResponse = await fetch(`/check-telegram-status/${telegramCode}`);
            const checkResult = await checkResponse.json();
            
            if (checkResult.success && checkResult.linked) {
                clearInterval(checkInterval);
                showNotification('✅ تم ربط التليجرام بنجاح!', 'success');
                setTimeout(() => {
                    window.location.href = '/coins-order';
                }, 1000);
            }
        } catch (error) {
            console.error('خطأ في فحص الربط:', error);
        }
    }, 3000);
    
    // إيقاف المراقبة بعد دقيقة
    setTimeout(() => clearInterval(checkInterval), 60000);
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

// دوال مساعدة إضافية
function getPlatformDisplayName(platform) {
    const names = {
        'playstation': 'PlayStation',
        'xbox': 'Xbox', 
        'pc': 'PC'
    };
    return names[platform] || platform;
}

// ═══════════════════════════════════════════════════════════════
// 🔗 نظام استخلاص روابط InstaPay الذكي المحسن
// ═══════════════════════════════════════════════════════════════

/**
 * 🎯 الدالة الرئيسية: استخلاص روابط InstaPay الذكي من النصوص المركبة
 */
function extractInstapayLink(inputText) {
    if (!inputText) {
        return null;
    }
    
    console.log('🔍 Extracting InstaPay link from text:', inputText);
    
    // تنظيف النص من الأسطر الجديدة والمسافات الزائدة
    const cleanText = inputText.trim().replace(/\n/g, ' ').replace(/\r/g, ' ').replace(/\s+/g, ' ');
    
    // 🔥 أنماط البحث المتقدمة لروابط InstaPay
    const instapayPatterns = [
        // النمط الأساسي لـ ipn.eg (الأكثر شيوعاً)
        /https?:\/\/(?:www\.)?ipn\.eg\/S\/[^\/\s]+\/instapay\/[A-Za-z0-9]+/gi,
        
        // أنماط أخرى
        /https?:\/\/(?:www\.)?instapay\.com\.eg\/[^\s<>"{}|\\^`\[\]]+/gi,
        /https?:\/\/(?:www\.)?app\.instapay\.com\.eg\/[^\s<>"{}|\\^`\[\]]+/gi,
        /https?:\/\/(?:www\.)?instapay\.app\/[^\s<>"{}|\\^`\[\]]+/gi,
        /https?:\/\/(?:www\.)?ipn\.eg\/[^\s<>"{}|\\^`\[\]]+/gi,
        /https?:\/\/(?:www\.)?pay\.instapay\.com\.eg\/[^\s<>"{}|\\^`\[\]]+/gi,
    ];
    
    let extractedLinks = [];
    
    // البحث باستخدام كل نمط
    for (const pattern of instapayPatterns) {
        const matches = cleanText.match(pattern) || [];
        extractedLinks = extractedLinks.concat(matches);
    }
    
    // إزالة المكررات
    const uniqueLinks = [...new Set(extractedLinks)];
    
    // تنظيف وفلترة الروابط
    const validLinks = [];
    for (const link of uniqueLinks) {
        // تنظيف العلامات من النهاية
        const cleanedLink = link.replace(/[.,;!?]+$/, '').trim();
        
        if (isValidInstapayUrl(cleanedLink)) {
            validLinks.push(cleanedLink);
        }
    }
    
    // إرجاع أفضل رابط
    if (validLinks.length > 0) {
        const bestLink = selectBestInstapayLink(validLinks);
        console.log('✅ Found InstaPay link:', bestLink);
        return bestLink;
    }
    
    console.log('❌ No valid InstaPay link found');
    return null;
}

/**
 * 🔍 التحقق من صحة رابط InstaPay
 */
function isValidInstapayUrl(url) {
    if (!url || (!url.startsWith('http://') && !url.startsWith('https://'))) {
        return false;
    }
    
    const validDomains = [
        'ipn.eg',
        'instapay.com.eg',
        'app.instapay.com.eg',
        'instapay.app',
        'pay.instapay.com.eg'
    ];
    
    try {
        const urlObj = new URL(url.toLowerCase());
        const domain = urlObj.hostname.replace('www.', '');
        
        // التحقق من النطاق والطول والمعرف
        const domainValid = validDomains.some(validDomain => domain.includes(validDomain));
        const lengthValid = url.length >= 20;
        const hasIdentifier = urlObj.pathname.length > 3;
        
        return domainValid && lengthValid && hasIdentifier;
        
    } catch (error) {
        console.warn('Error validating URL:', error);
        return false;
    }
}

/**
 * 🏆 اختيار أفضل رابط
 */
function selectBestInstapayLink(links) {
    if (!links || links.length === 0) {
        return "";
    }
    
    const priorityDomains = [
        'ipn.eg/S/',  // أولوية عليا
        'instapay.com.eg',
        'app.instapay.com.eg', 
        'instapay.app'
    ];
    
    // بحث حسب الأولوية
    for (const priority of priorityDomains) {
        for (const link of links) {
            if (link.toLowerCase().includes(priority)) {
                return link;
            }
        }
    }
    
    return links[0];
}

/**
 * 📊 استخلاص معلومات الرابط
 */
function extractInstapayInfo(url) {
    const info = {
        url: url,
        domain: '',
        username: '',
        code: '',
        type: 'unknown'
    };
    
    try {
        const urlObj = new URL(url);
        info.domain = urlObj.hostname.replace('www.', '');
        
        // استخلاص معلومات ipn.eg
        if (info.domain.includes('ipn.eg')) {
            const pathParts = urlObj.pathname.split('/').filter(part => part);
            if (pathParts.length >= 4 && pathParts[0] === 'S') {
                info.username = pathParts[1];
                info.code = pathParts[3] || '';
                info.type = 'standard';
            }
        }
        
    } catch (error) {
        console.warn('Error extracting InstaPay info:', error);
    }
    
    return info;
}

/**
 * ✅ التحقق من حقل InstaPay مع الاستخلاص الذكي
 */
function validateInstapayInput(inputElement) {
    const inputValue = inputElement.value.trim();
    console.log('🔍 Validating InstaPay input:', inputValue);
    
    if (!inputValue) {
        updateInstapayUI(inputElement, true, '');
        return true;
    }
    
    // محاولة استخلاص الرابط
    const extractedLink = extractInstapayLink(inputValue);
    
    if (extractedLink) {
        // رابط صحيح موجود
        if (extractedLink !== inputValue) {
            // تحديث الحقل وإظهار الإشعار
            inputElement.value = extractedLink;
            showInstapayExtractionNotice(inputElement, inputValue, extractedLink);
        }
        
        const linkInfo = extractInstapayInfo(extractedLink);
        updateInstapayUI(inputElement, true, '✅ رابط InstaPay صحيح');
        showInstapayLinkInfo(inputElement, linkInfo);
        return true;
        
    } else {
        // لا يوجد رابط صحيح
        updateInstapayUI(inputElement, false, 'لم يتم العثور على رابط InstaPay صحيح في النص');
        return false;
    }
}

/**
 * 💡 إشعار الاستخلاص الذكي
 */
function showInstapayExtractionNotice(inputElement, originalText, extractedLink) {
    const container = inputElement.closest('.form-group') || inputElement.parentNode;
    
    // إزالة إشعارات سابقة
    const existingNotice = container.querySelector('.instapay-extraction-notice');
    if (existingNotice) existingNotice.remove();
    
    const noticeDiv = document.createElement('div');
    noticeDiv.className = 'instapay-extraction-notice success-notice';
    noticeDiv.innerHTML = `
        <div class="extraction-content">
            <i class="fas fa-magic"></i>
            <span>تم استخلاص رابط InstaPay من النص بنجاح!</span>
            <div class="extraction-details">
                <small>النص الأصلي: "${originalText.substring(0, 50)}${originalText.length > 50 ? '...' : ''}"</small>
                <br>
                <small>الرابط المستخلص: "${extractedLink}"</small>
            </div>
        </div>
    `;
    
    // إضافة CSS للإشعار
    noticeDiv.style.cssText = `
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 8px;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        opacity: 0;
        transform: translateY(-10px);
        transition: all 0.3s ease;
    `;
    
    container.appendChild(noticeDiv);
    
    setTimeout(() => {
        noticeDiv.style.opacity = '1';
        noticeDiv.style.transform = 'translateY(0)';
    }, 100);
    
    // اهتزاز للهواتف
    if (navigator.vibrate) {
        navigator.vibrate([100, 50, 100]);
    }
    
    // إزالة تلقائية
    setTimeout(() => {
        noticeDiv.style.opacity = '0';
        noticeDiv.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            if (noticeDiv.parentNode) {
                noticeDiv.remove();
            }
        }, 300);
    }, 5000);
}

/**
 * 📋 عرض معلومات الرابط
 */
function showInstapayLinkInfo(inputElement, linkInfo) {
    const container = inputElement.closest('.form-group') || inputElement.parentNode;
    
    // إزالة معلومات سابقة
    const existingInfo = container.querySelector('.instapay-link-info');
    if (existingInfo) existingInfo.remove();
    
    const infoDiv = document.createElement('div');
    infoDiv.className = 'instapay-link-info';
    infoDiv.innerHTML = `
        <div class="link-info-content">
            <div class="info-header">
                <i class="fas fa-link"></i>
                <span>معلومات رابط InstaPay</span>
            </div>
            <div class="link-details">
                <div><strong>النطاق:</strong> ${linkInfo.domain}</div>
                ${linkInfo.username ? `<div><strong>اسم المستخدم:</strong> ${linkInfo.username}</div>` : ''}
                ${linkInfo.code ? `<div><strong>كود الدفع:</strong> ${linkInfo.code}</div>` : ''}
                <div><strong>نوع الرابط:</strong> ${linkInfo.type === 'standard' ? 'رابط قياسي' : 'رابط مخصص'}</div>
            </div>
        </div>
    `;
    
    // إضافة CSS للمعلومات
    infoDiv.style.cssText = `
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 10px;
        margin: 8px 0;
        font-size: 13px;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    container.appendChild(infoDiv);
    
    setTimeout(() => {
        infoDiv.style.opacity = '1';
    }, 200);
}

/**
 * 🎨 تحديث UI للحقل
 */
function updateInstapayUI(inputElement, isValid, message) {
    const container = inputElement.closest('.form-group');
    if (!container) return;
    
    // إزالة حالات سابقة
    container.classList.remove('valid', 'invalid');
    inputElement.classList.remove('valid', 'invalid');
    
    // إزالة رسائل سابقة
    const existingError = container.querySelector('.error-message');
    const existingSuccess = container.querySelector('.success-message');
    if (existingError) existingError.remove();
    if (existingSuccess) existingSuccess.remove();
    
    if (message) {
        if (isValid) {
            container.classList.add('valid');
            inputElement.classList.add('valid');
            if (message.includes('✅')) {
                const successMsg = document.createElement('div');
                successMsg.className = 'success-message';
                successMsg.textContent = message;
                successMsg.style.cssText = 'color: #10B981; font-size: 12px; margin-top: 4px;';
                container.appendChild(successMsg);
            }
        } else {
            container.classList.add('invalid');
            inputElement.classList.add('invalid');
            const errorMsg = document.createElement('div');
            errorMsg.className = 'error-message';
            errorMsg.textContent = message;
            errorMsg.style.cssText = 'color: #DC2626; font-size: 12px; margin-top: 4px;';
            container.appendChild(errorMsg);
        }
    } else if (isValid) {
        container.classList.add('valid');
        inputElement.classList.add('valid');
    }
}

console.log('🚀 InstaPay Smart Link Extraction System - Enhanced Version Loaded!');

// ✅ نظام ربط التليجرام المبسط - الكود الصحيح الكامل
function initializeTelegramButton() {
    const telegramButton = document.getElementById('telegram-link-btn');
    if (!telegramButton) return;
    
    telegramButton.addEventListener('click', async function() {
        const telegramBtn = this; // ✅ تعريف المتغير داخل النطاق الصحيح
        const originalContent = this.innerHTML; // ✅ حفظ المحتوى الأصلي
        
        telegramBtn.disabled = true;
        telegramBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الحصول على الكود...';
        
        try {
            const response = await fetch('/api/link_telegram', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });
            
            const result = await response.json();
            
            if (result.success && result.telegram_code) {
                // ✅ تعريف data في النطاق الصحيح
                const data = result;
                
                // فتح التليجرام بالطريقة الذكية
                console.log('🔗 فتح التليجرام بالطريقة المتدرجة:', data);
                openTelegramSmartly(data);
                
                // تحديث النص للمساعدة - ✅ داخل النطاق الصحيح
                telegramBtn.innerHTML = `
                    <div class="telegram-btn-content">
                        <i class="fas fa-paper-plane telegram-icon" style="color: #00d084;"></i>
                        <div class="telegram-text">
                            <span class="telegram-title">✅ تم فتح التليجرام</span>
                            <span class="telegram-subtitle">الكود: ${data.telegram_code} | اكتب /start إذا لم يظهر</span>
                        </div>
                    </div>
                `;
                telegramBtn.classList.add('success');
                
                // إضافة الكود كنص قابل للنسخ - ✅ داخل النطاق الصحيح
                let existingCodeDisplay = document.querySelector('.telegram-code-display');
                if (existingCodeDisplay) {
                    existingCodeDisplay.remove();
                }
                
                const codeDisplay = document.createElement('div');
                codeDisplay.className = 'telegram-code-display';
                codeDisplay.innerHTML = `
                    <div style="background: linear-gradient(135deg, rgba(0, 136, 204, 0.1), rgba(0, 85, 153, 0.15)); padding: 15px; margin: 15px 0; border-radius: 12px; text-align: center; border: 2px solid #0088cc; backdrop-filter: blur(10px);">
                        <div style="color: #0088cc; font-weight: 700; margin-bottom: 10px;">
                            <i class="fas fa-copy"></i> الكود للنسخ اليدوي:
                        </div>
                        <code style="background: white; padding: 8px 12px; border-radius: 6px; font-weight: bold; color: #0088cc; font-size: 1.1em; word-break: break-all; display: inline-block; margin-bottom: 10px;">/start ${data.telegram_code}</code>
                        <div style="font-size: 0.9em; color: rgba(255, 255, 255, 0.8);">
                            <small>انسخ هذا النص والصقه في التليجرام إذا لم يظهر تلقائياً</small>
                        </div>
                        <button onclick="copyToClipboard('/start ${data.telegram_code}')" style="background: #0088cc; color: white; border: none; padding: 8px 16px; border-radius: 6px; margin-top: 10px; cursor: pointer; font-weight: 600;">
                            📋 نسخ الكود
                        </button>
                    </div>
                `;
                
                // إدراج عنصر الكود بعد الزر مباشرة
                telegramBtn.parentNode.insertBefore(codeDisplay, telegramBtn.nextSibling);
                
                // نسخ الكود للحافظة تلقائياً - ✅ داخل النطاق الصحيح
                setTimeout(() => {
                    copyTelegramCodeToClipboard(data.telegram_code);
                }, 2000);
                
                // مراقبة الربط كل 3 ثوان
                const checkInterval = setInterval(async () => {
                    try {
                        const checkResponse = await fetch(`/check-telegram-status/${data.telegram_code}`);
                        const checkResult = await checkResponse.json();
                        
                        if (checkResult.success && checkResult.is_linked) {
                            clearInterval(checkInterval);
                            showNotification('✅ تم ربط التليجرام بنجاح!', 'success');
                            // الانتقال التلقائي فوراً
                            setTimeout(() => {
                                window.location.href = '/coins-order';
                            }, 1000);
                        }
                    } catch (error) {
                        console.error('خطأ في فحص الربط:', error);
                    }
                }, 3000);
                
                // إيقاف المراقبة بعد دقيقة
                setTimeout(() => clearInterval(checkInterval), 60000);
                
                // إعادة الزر للوضع الطبيعي بعد 10 ثوان
                setTimeout(() => {
                    telegramBtn.innerHTML = originalContent;
                    telegramBtn.classList.remove('success');
                    telegramBtn.disabled = false;
                    // إزالة عرض الكود
                    const codeDisplayElement = document.querySelector('.telegram-code-display');
                    if (codeDisplayElement) {
                        codeDisplayElement.style.opacity = '0';
                        setTimeout(() => codeDisplayElement.remove(), 500);
                    }
                }, 10000);
                
            } else {
                throw new Error(result.message || 'فشل في الحصول على الكود');
            }
            
        } catch (error) {
            console.error('خطأ:', error);
            telegramBtn.innerHTML = '❌ خطأ - اضغط للمحاولة مرة أخرى';
            telegramBtn.disabled = false;
        }
    });
}

// 🔥 الدوال المساعدة - ✅ في المكان الصحيح بعد الدالة الرئيسية

// نظام فتح التليجرام المتدرج الذكي
function openTelegramSmartly(data) {
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isAndroid = /Android/.test(navigator.userAgent);
    
    console.log('📱 Device Detection:', { isMobile, isIOS, isAndroid });
    
    if (isMobile) {
        // للهواتف: جرب التطبيق أولاً، ثم المتصفح
        console.log('🚀 محاولة فتح تطبيق التليجرام مباشرة...');
        
        // إنشاء رابط مخفي للتطبيق
        if (data.telegram_app_url) {
            const appLink = document.createElement('a');
            appLink.href = data.telegram_app_url;
            appLink.style.display = 'none';
            document.body.appendChild(appLink);
            
            // محاولة فتح التطبيق
            appLink.click();
            
            // إزالة الرابط
            setTimeout(() => {
                if (document.body.contains(appLink)) {
                    document.body.removeChild(appLink);
                }
            }, 100);
        }
        
        // خطة بديلة: فتح في المتصفح بعد ثانيتين
        setTimeout(() => {
            console.log('🌐 فتح رابط التليجرام في المتصفح كخطة بديلة...');
            window.open(data.telegram_web_url, '_blank');
        }, 2000);
        
    } else {
        // للكمبيوتر: فتح في المتصفح مباشرة
        console.log('💻 فتح التليجرام في المتصفح للكمبيوتر...');
        window.open(data.telegram_web_url, '_blank');
    }
}

// دالة الطوارئ: نسخ الكود للحافظة تلقائياً
function copyTelegramCodeToClipboard(code) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(`/start ${code}`).then(() => {
            console.log('📋 تم نسخ الكود للحافظة:', `/start ${code}`);
            showNotification('تم نسخ الكود للحافظة! الصقه في التليجرام', 'success');
        }).catch(err => {
            console.warn('❌ فشل في نسخ الكود:', err);
        });
    }
}

// دالة نسخ عامة للاستخدام مع الأزرار
function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('تم النسخ بنجاح!', 'success');
        }).catch(() => {
            // طريقة بديلة للنسخ
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                showNotification('تم النسخ بنجاح!', 'success');
            } catch (err) {
                showNotification('فشل في النسخ', 'error');
            }
            document.body.removeChild(textArea);
        });
    } else {
        // طريقة بديلة للمتصفحات القديمة
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showNotification('تم النسخ بنجاح!', 'success');
        } catch (err) {
            showNotification('فشل في النسخ', 'error');
        }
        document.body.removeChild(textArea);
    }
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
console.log('🎮 FC 26 Profile Setup - Fixed Buttons Version Loaded Successfully!');
console.log('✅ Platform buttons: FIXED');
console.log('✅ Payment buttons: FIXED');
console.log('✅ All original features: PRESERVED');
console.log('🔧 Ready for copy-paste: 2000+ lines maintained');

// ═══ النهاية - لا تضع أي شيء بعد هذا ═══
