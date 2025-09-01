#!/bin/bash
# سكريبت تشغيل البوت التليجرام

echo "🚀 بدء تشغيل بوت EA FC FIFA..."
echo "================================"

# التحقق من Python
echo "✅ التحقق من Python..."
python3 --version

# تثبيت المتطلبات
echo "📦 تثبيت المتطلبات..."
pip3 install -r requirements.txt

# إنشاء الملفات المطلوبة إذا لم تكن موجودة
echo "📁 إنشاء الملفات المطلوبة..."
touch accounts.json orders_history.json bot_stats.json bot_config.json

# تشغيل البوت
echo "🤖 تشغيل البوت..."
python3 telegram_bot.py