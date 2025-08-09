// ===================================================
// TELEGRAM INTEGRATION MODULE
// All Telegram-related logic is handled here.
// ===================================================

// Note: This file assumes that 'showNotification' and 'getCSRFToken' are available globally
// from the main script.js file.

/**
 * 🚀 Main handler for the Telegram link button.
 * This function is exported to be used in the main script.
 */
export async function handleTelegramLink() {
    const btn = document.getElementById('telegram-link-btn');
    if (!btn || btn.disabled) return;

    // Direct DOM validation
    const selectedPlatformCard = document.querySelector('.platform-card.selected');
    const isWhatsappVerified = document.querySelector('.phone-info.success-info') !== null;

    if (!selectedPlatformCard || !isWhatsappVerified) {
        showNotification('❌ يرجى اختيار المنصة والتحقق من رقم الواتساب أولاً', 'error');
        return;
    }

    const originalContent = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري توليد الكود...';

    try {
        const platformValue = selectedPlatformCard.dataset.platform;
        const whatsappValue = document.getElementById('whatsapp').value;

        const response = await fetch('/generate-telegram-code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify({ platform: platformValue, whatsapp_number: whatsappValue })
        });

        const data = await response.json();

        if (data.success && data.telegram_web_url) {
            openTelegramSmartly(data);
            updateTelegramButtonOnSuccess(btn, data);
            displayCopyableCode(data);
            setTimeout(() => copyTelegramCodeToClipboard(data.telegram_code), 2000);
            monitorTelegramLinking(data.telegram_code);

            setTimeout(() => {
                btn.innerHTML = originalContent;
                btn.classList.remove('success');
                btn.disabled = false;
                document.querySelector('.telegram-code-display')?.remove();
            }, 10000);

        } else {
            throw new Error(data.message || 'فشل في الحصول على الرابط');
        }
    } catch (error) {
        console.error('خطأ في ربط التليجرام:', error);
        btn.innerHTML = '❌ خطأ - اضغط للمحاولة مرة أخرى';
        btn.disabled = false;
    }
}

/**
 * 🔥 Smart function to open Telegram link.
 */
function openTelegramSmartly(data) {
    const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    if (isMobile && data.telegram_app_url) {
        window.location.href = data.telegram_app_url;
    } else {
        window.open(data.telegram_web_url, '_blank');
    }
}

/**
 * 🚨 Emergency function: Copies the code to the clipboard.
 */
function copyTelegramCodeToClipboard(code) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(`/start ${code}`).then(() => {
            showNotification('تم نسخ كود التفعيل! الصقه في التليجرام إذا لزم الأمر', 'success');
        });
    }
}

/**
 * 💡 Displays the copyable code snippet below the button.
 */
function displayCopyableCode(data) {
    const telegramBtn = document.getElementById('telegram-link-btn');
    document.querySelector('.telegram-code-display')?.remove();

    const codeDisplay = document.createElement('div');
    codeDisplay.className = 'telegram-code-display';
    codeDisplay.innerHTML = `
        <div style="background: rgba(0, 136, 204, 0.1); padding: 12px; margin-top: 15px; border-radius: 8px; text-align: center; border: 1px dashed #0088cc;">
            <strong style="color: #0088cc; font-weight: 700; margin-bottom: 10px; display: block;">الكود للنسخ (للطوارئ):</strong>
            <code style="background: rgba(255,255,255,0.2); padding: 4px 8px; border-radius: 4px; font-weight: bold; color: #0088cc;">/start ${data.telegram_code}</code>
        </div>
    `;
    telegramBtn.parentNode.insertBefore(codeDisplay, telegramBtn.nextSibling);
}

/**
 * 🔄 Monitors the linking status in the background.
 */
function monitorTelegramLinking(code) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/check-telegram-status/${code}`);
            const result = await response.json();
            if (result.linked) {
                clearInterval(interval);
                showNotification('✅ تم ربط التليجرام بنجاح!', 'success');
                setTimeout(() => window.location.href = '/coins-order', 1000);
            }
        } catch (error) {
            console.error('Error checking Telegram status:', error);
        }
    }, 3000);
    setTimeout(() => clearInterval(interval), 60000);
}

/**
 * ✨ Updates the button UI on success.
 */
function updateTelegramButtonOnSuccess(btn, data) {
    btn.innerHTML = `
        <div class="telegram-btn-content">
            <i class="fas fa-paper-plane telegram-icon" style="color: #00d084;"></i>
            <div class="telegram-text">
                <span class="telegram-title">✅ تم فتح التليجرام</span>
                <span class="telegram-subtitle">الكود: ${data.telegram_code}</span>
            </div>
        </div>
    `;
    btn.classList.add('success');
}
