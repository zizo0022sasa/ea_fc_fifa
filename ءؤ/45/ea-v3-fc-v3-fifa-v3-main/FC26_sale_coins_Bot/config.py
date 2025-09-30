# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                🎮 FC26 GAMING BOT - CONFIGURATION                        ║
# ║                     بوت FC26 للألعاب - الإعدادات                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import os
from typing import Dict

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║ 🔧 [ BOT CONFIGURATION ]                                                ║
# ║ 🔐 الإعدادات الأساسية والتوكن                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# Bot Token - يفضل استخدام متغير البيئة
BOT_TOKEN = os.getenv('BOT_TOKEN', '7607085569:AAHKE8SNOTYycRRzOCCddmm8QPDTOnEx144')

# Database Configuration
DATABASE_CONFIG = {
    'name': 'fc26_bot.db',
    'path': './database/',
    'backup_path': './database/backups/'
}

# ┌──────────────────────────────────────────────────────────────────────┐
# │ 🎮 GAMING PLATFORMS - منصات الألعاب                                 │
# └──────────────────────────────────────────────────────────────────────┘

GAMING_PLATFORMS = {
    "playstation": {"name": "🎮 PlayStation (PS4/PS5)", "emoji": "🎮"},
    "xbox": {"name": "❎ Xbox (One/Series)", "emoji": "❎"},
    "pc": {"name": "💻 PC (Origin/Steam)", "emoji": "💻"},
}

# ────────────────────────────────────────────────────────────────────────
# 💳 PAYMENT METHODS - طرق الدفع الكاملة
# ────────────────────────────────────────────────────────────────────────

PAYMENT_METHODS = {
    "vodafone_cash": "⭕️ فودافون كاش",
    "etisalat_cash": "🟢 اتصالات كاش",
    "orange_cash": "🍊 أورانج كاش",
    "we_cash": "🟣 وي كاش",
    "bank_wallet": "🏦 محفظة بنكية",
    "telda": "💳 تيلدا",
    "instapay": "🔗 إنستا باي",
}

# ────────────────────────────────────────────────────────────────────────
# 📝 LOGGING CONFIGURATION - إعداد السجلات
# ────────────────────────────────────────────────────────────────────────

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': './logs/fc26_bot.log',
    'max_bytes': 5 * 1024 * 1024,  # 5MB
    'backup_count': 5,
    'encoding': 'utf-8'
}

# ────────────────────────────────────────────────────────────────────────
# 🛡️ SECURITY SETTINGS - إعدادات الأمان
# ────────────────────────────────────────────────────────────────────────

SECURITY_CONFIG = {
    'max_input_length': 500,
    'allowed_phone_patterns': [r'^01[0125][0-9]{8}$'],
    'blocked_chars': ['<', '>', '"', "'", '&', 'script', 'javascript'],
    'rate_limit': {
        'messages_per_minute': 10,
        'registration_attempts': 3
    }
}

# ────────────────────────────────────────────────────────────────────────
# 🎨 UI CONFIGURATION - إعدادات واجهة المستخدم
# ────────────────────────────────────────────────────────────────────────

UI_CONFIG = {
    'messages': {
        'timeout': 300,  # 5 minutes
        'auto_delete': True,
        'max_buttons_per_row': 2
    },
    'emojis': {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'loading': '⏳'
    }
}

# ────────────────────────────────────────────────────────────────────────
# 📊 STATISTICS CONFIGURATION - إعدادات الإحصائيات
# ────────────────────────────────────────────────────────────────────────

STATS_CONFIG = {
    'enabled': True,
    'daily_reports': True,
    'metrics': ['users', 'registrations', 'errors', 'response_times']
}

# ────────────────────────────────────────────────────────────────────────
# 🔄 BACKUP CONFIGURATION - إعدادات النسخ الاحتياطية
# ────────────────────────────────────────────────────────────────────────

BACKUP_CONFIG = {
    'enabled': True,
    'interval_hours': 6,
    'max_backups': 10,
    'compress': True
}

# ────────────────────────────────────────────────────────────────────────
# 🌐 ENVIRONMENT SETTINGS - إعدادات البيئة
# ────────────────────────────────────────────────────────────────────────

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Development/Production specific settings
if ENVIRONMENT == 'production':
    LOGGING_CONFIG['level'] = 'WARNING'
    DEBUG = False
    SECURITY_CONFIG['rate_limit']['messages_per_minute'] = 5
else:
    LOGGING_CONFIG['level'] = 'DEBUG'
    DEBUG = True

# ┌────────────────────────────────────────────────────────────────────────────┐
# │                           🎉 END OF CONFIGURATION 🎉                      │
# │                      ✨ إعدادات شاملة ومنظمة ✨                            │
# └────────────────────────────────────────────────────────────────────────────┘