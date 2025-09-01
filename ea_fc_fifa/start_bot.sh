#!/bin/bash
echo "🔥 تشغيل بوت التليجرام..."
echo "========================"

# التأكد من Python 3
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # التحقق من إصدار Python
    if python --version 2>&1 | grep -q "Python 3"; then
        PYTHON_CMD="python"
    else
        echo "❌ Python 3 مطلوب!"
        exit 1
    fi
else
    echo "❌ Python غير مثبت!"
    exit 1
fi

echo "✅ استخدام: $PYTHON_CMD"

# تثبيت المتطلبات
echo "📦 تثبيت المتطلبات..."
$PYTHON_CMD -m pip install python-telegram-bot requests --quiet

# إنشاء الملفات المطلوبة
touch tokens.json stats.json bot.log

# تشغيل البوت
echo "🚀 البوت شغال..."
$PYTHON_CMD telegram_bot.py