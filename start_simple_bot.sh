#!/bin/bash
echo "🔥 تشغيل البوت البسيط..."
echo "========================"

# تثبيت المتطلبات
pip3 install -r requirements_simple.txt -q

# إنشاء الملفات المطلوبة
touch accounts.json stats.json bot.log

# تشغيل البوت
python3 simple_telegram_bot.py