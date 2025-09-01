#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 بوت التليجرام الاحترافي للتحكم في نظام EA FC FIFA
👨‍💻 Developer: @zizo0022sasa
🔥 Version: 1.0.0 - النسخة المصرية الكاملة
"""

import json
import os
import random
import string
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

# مكتبات التليجرام
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode

# مكتبات إضافية
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==============================================================================
# 🔐 الإعدادات الأساسية
# ==============================================================================
TELEGRAM_BOT_TOKEN = "7958170099:AAHttiDXnc_aHcdPrmZUTnD-rn9w1LD4T6I"
ADMIN_ID = 1124247595  # معرف الأدمن (انت بس)

# إعدادات API
API_BASE_URL = "https://freefollower.net/api"
ACCOUNTS_FILE = "accounts.json"
ORDERS_FILE = "orders_history.json"
STATS_FILE = "bot_stats.json"
CONFIG_FILE = "bot_config.json"

# إعدادات الخدمة
FREE_SERVICE_ID = 196
DEFAULT_TIKTOK_PROFILE = "https://www.tiktok.com/@shahd.store.2?_t=ZS-8zKejIixJeT&_r=1"

# فترات الانتظار الذكية
MIN_WAIT_SECONDS = 5
MAX_WAIT_SECONDS = 10

# حالات المحادثة
(
    MAIN_MENU,
    WAITING_SERVICE,
    WAITING_LINK,
    WAITING_QUANTITY,
    SETTINGS_MENU,
    WAITING_CONFIG,
    ANALYTICS_MENU
) = range(7)

# ==============================================================================
# 🎨 الرموز والإيموجي
# ==============================================================================
EMOJIS = {
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'robot': '🤖',
    'fire': '🔥',
    'star': '⭐',
    'rocket': '🚀',
    'chart': '📊',
    'settings': '⚙️',
    'crown': '👑',
    'lock': '🔐',
    'user': '👤',
    'users': '👥',
    'clock': '⏰',
    'link': '🔗',
    'new': '🆕',
    'package': '📦',
    'money': '💰',
    'diamond': '💎',
    'gift': '🎁',
    'egypt': '🇪🇬',
    'heart': '❤️',
    'tick': '✔️',
    'cross': '✖️',
    'refresh': '🔄',
    'folder': '📁',
    'pin': '📌',
    'bell': '🔔',
    'shield': '🛡️',
    'key': '🔑',
    'target': '🎯',
    'trophy': '🏆',
    'medal': '🥇'
}

# ==============================================================================
# 🛠️ دوال مساعدة
# ==============================================================================

def setup_logging():
    """إعداد نظام السجلات"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler('telegram_bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def load_json_file(filename: str, default: Any = None) -> Any:
    """تحميل ملف JSON"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"خطأ في تحميل {filename}: {e}")
    return default if default is not None else {}

def save_json_file(filename: str, data: Any) -> bool:
    """حفظ ملف JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"خطأ في حفظ {filename}: {e}")
        return False

def is_admin(user_id: int) -> bool:
    """التحقق من صلاحيات الأدمن"""
    return user_id == ADMIN_ID

def format_number(number: int) -> str:
    """تنسيق الأرقام بشكل جميل"""
    if number >= 1000000:
        return f"{number/1000000:.1f}M"
    elif number >= 1000:
        return f"{number/1000:.1f}K"
    return str(number)

def get_random_wait_time() -> float:
    """الحصول على وقت انتظار عشوائي"""
    return random.uniform(MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)

# ==============================================================================
# 🔧 دوال API المحسنة
# ==============================================================================

class APIManager:
    """مدير API محسن مع إعادة المحاولة والتعامل مع الأخطاء"""
    
    def __init__(self):
        self.session = self._create_session()
        self.stats = self._load_stats()
    
    def _create_session(self) -> requests.Session:
        """إنشاء جلسة مع إعادة المحاولة"""
        session = requests.Session()
        retry = Retry(
            total=3,
            read=3,
            connect=3,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 503, 504)
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def _load_stats(self) -> Dict:
        """تحميل الإحصائيات"""
        return load_json_file(STATS_FILE, {
            'total_accounts': 0,
            'total_orders': 0,
            'successful_orders': 0,
            'failed_orders': 0,
            'total_followers_sent': 0,
            'last_update': None
        })
    
    def _save_stats(self):
        """حفظ الإحصائيات"""
        self.stats['last_update'] = datetime.now().isoformat()
        save_json_file(STATS_FILE, self.stats)
    
    def generate_credentials(self) -> tuple:
        """توليد بيانات حساب جديد"""
        vowels = "aeiou"
        consonants = "bcdfghjklmnprstvwxyz"
        
        # توليد اسم عشوائي
        name_part1 = "".join(random.choices(consonants, k=2)) + random.choice(vowels)
        name_part2 = random.choice(consonants) + random.choice(vowels)
        base_name = (name_part1 + name_part2).capitalize()
        
        # توليد سنة الميلاد
        birth_year = random.randint(1988, 2005)
        
        # توليد اسم المستخدم
        username_style = random.choice(["year", "suffix_number"])
        if username_style == "year":
            username = f"{base_name.lower()}{birth_year}"
        else:
            username = f"{base_name.lower()}_{random.randint(10, 99)}"
        
        # توليد البريد الإلكتروني
        email_domains = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com"]
        email = f"{username}@{random.choice(email_domains)}"
        
        # توليد كلمة المرور
        pass_part = "".join(random.choices(string.ascii_lowercase, k=5))
        password_base = pass_part.capitalize()
        password_symbol = random.choice("!@#$*&")
        password = f"{password_base}{birth_year}{password_symbol}"
        
        logger.info(f"تم توليد بيانات: {username}")
        return username, email, password
    
    def create_account(self) -> Optional[Dict]:
        """إنشاء حساب جديد"""
        username, email, password = self.generate_credentials()
        payload = {
            "login": username,
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}/register",
                json=payload,
                timeout=20
            )
            
            if response.status_code == 201:
                data = response.json()
                api_token = data.get("api_token")
                
                if api_token:
                    account_info = {
                        "token": api_token,
                        "username": username,
                        "password": password,
                        "email": email,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # حفظ الحساب
                    accounts = load_json_file(ACCOUNTS_FILE, [])
                    accounts.append(account_info)
                    save_json_file(ACCOUNTS_FILE, accounts)
                    
                    # تحديث الإحصائيات
                    self.stats['total_accounts'] += 1
                    self._save_stats()
                    
                    logger.info(f"تم إنشاء حساب جديد: {username}")
                    return account_info
            
            logger.error(f"فشل إنشاء الحساب: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الحساب: {e}")
            return None
    
    def place_order(self, api_token: str, service_id: int, link: str, quantity: int) -> bool:
        """إرسال طلب جديد"""
        payload = {
            "key": api_token,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity
        }
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}/v2",
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "order" in data:
                    # حفظ الطلب
                    order_info = {
                        "order_id": data["order"],
                        "service_id": service_id,
                        "link": link,
                        "quantity": quantity,
                        "status": "success",
                        "created_at": datetime.now().isoformat()
                    }
                    
                    orders = load_json_file(ORDERS_FILE, [])
                    orders.append(order_info)
                    save_json_file(ORDERS_FILE, orders)
                    
                    # تحديث الإحصائيات
                    self.stats['total_orders'] += 1
                    self.stats['successful_orders'] += 1
                    self.stats['total_followers_sent'] += quantity
                    self._save_stats()
                    
                    logger.info(f"تم إرسال الطلب بنجاح: {data['order']}")
                    return True
                
                elif "error" in data:
                    logger.error(f"خطأ من API: {data['error']}")
                    self.stats['failed_orders'] += 1
                    self._save_stats()
                    return False
            
            logger.error(f"فشل إرسال الطلب: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"خطأ في إرسال الطلب: {e}")
            self.stats['failed_orders'] += 1
            self._save_stats()
            return False
    
    def get_stats(self) -> Dict:
        """الحصول على الإحصائيات"""
        return self.stats

# ==============================================================================
# 🤖 البوت الأساسي
# ==============================================================================

class EAFCBot:
    """البوت الرئيسي للتليجرام"""
    
    def __init__(self):
        self.api_manager = APIManager()
        self.config = self._load_config()
        self.active_tasks = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def _load_config(self) -> Dict:
        """تحميل الإعدادات"""
        default_config = {
            'auto_mode': False,
            'auto_interval': 60,
            'default_service': FREE_SERVICE_ID,
            'default_link': DEFAULT_TIKTOK_PROFILE,
            'default_quantity': 10,
            'max_accounts_per_day': 100,
            'notifications': True
        }
        return load_json_file(CONFIG_FILE, default_config)
    
    def _save_config(self):
        """حفظ الإعدادات"""
        save_json_file(CONFIG_FILE, self.config)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        user = update.effective_user
        
        if not is_admin(user.id):
            await update.message.reply_text(
                f"{EMOJIS['lock']} عذراً، هذا البوت خاص بالأدمن فقط!\n"
                f"{EMOJIS['egypt']} يا ريت تتواصل مع المطور @zizo0022sasa"
            )
            return ConversationHandler.END
        
        # إنشاء لوحة المفاتيح الرئيسية
        keyboard = [
            [
                InlineKeyboardButton(f"{EMOJIS['new']} طلب جديد", callback_data='new_order'),
                InlineKeyboardButton(f"{EMOJIS['robot']} تشغيل تلقائي", callback_data='auto_mode')
            ],
            [
                InlineKeyboardButton(f"{EMOJIS['chart']} الإحصائيات", callback_data='stats'),
                InlineKeyboardButton(f"{EMOJIS['settings']} الإعدادات", callback_data='settings')
            ],
            [
                InlineKeyboardButton(f"{EMOJIS['folder']} السجلات", callback_data='logs'),
                InlineKeyboardButton(f"{EMOJIS['info']} المساعدة", callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = (
            f"{EMOJIS['crown']} **أهلاً بيك يا كبير!**\n"
            f"{EMOJIS['egypt']} ده البوت المصري الاحترافي لنظام EA FC\n\n"
            f"{EMOJIS['fire']} **المميزات المتاحة:**\n"
            f"• إنشاء حسابات تلقائياً\n"
            f"• إرسال طلبات المتابعين\n"
            f"• تشغيل تلقائي ذكي\n"
            f"• إحصائيات مفصلة\n"
            f"• تحكم كامل في الإعدادات\n\n"
            f"{EMOJIS['rocket']} **اختار من القائمة:**"
        )
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return MAIN_MENU
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # طلب جديد
        if data == 'new_order':
            await self.new_order(update, context)
        
        # التشغيل التلقائي
        elif data == 'auto_mode':
            await self.toggle_auto_mode(update, context)
        
        # الإحصائيات
        elif data == 'stats':
            await self.show_stats(update, context)
        
        # الإعدادات
        elif data == 'settings':
            await self.show_settings(update, context)
        
        # السجلات
        elif data == 'logs':
            await self.show_logs(update, context)
        
        # المساعدة
        elif data == 'help':
            await self.show_help(update, context)
        
        # العودة للقائمة الرئيسية
        elif data == 'back_to_menu':
            await self.back_to_menu(update, context)
    
    async def new_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إنشاء طلب جديد"""
        query = update.callback_query
        
        loading_msg = await query.edit_message_text(
            f"{EMOJIS['clock']} جاري إنشاء حساب جديد..."
        )
        
        # إنشاء حساب جديد
        account = self.api_manager.create_account()
        
        if account:
            # إرسال الطلب
            success = self.api_manager.place_order(
                account['token'],
                self.config['default_service'],
                self.config['default_link'],
                self.config['default_quantity']
            )
            
            if success:
                message = (
                    f"{EMOJIS['success']} **تم بنجاح!**\n\n"
                    f"{EMOJIS['user']} الحساب: `{account['username']}`\n"
                    f"{EMOJIS['key']} كلمة السر: `{account['password']}`\n"
                    f"{EMOJIS['link']} الرابط: {self.config['default_link']}\n"
                    f"{EMOJIS['package']} الكمية: {self.config['default_quantity']}\n"
                )
            else:
                message = (
                    f"{EMOJIS['warning']} تم إنشاء الحساب لكن فشل الطلب!\n\n"
                    f"{EMOJIS['user']} الحساب: `{account['username']}`\n"
                )
        else:
            message = f"{EMOJIS['error']} فشل إنشاء الحساب! حاول تاني"
        
        # إضافة زر العودة
        keyboard = [[InlineKeyboardButton(f"{EMOJIS['refresh']} رجوع", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await loading_msg.edit_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return MAIN_MENU
    
    async def toggle_auto_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تشغيل/إيقاف الوضع التلقائي"""
        query = update.callback_query
        
        self.config['auto_mode'] = not self.config['auto_mode']
        self._save_config()
        
        if self.config['auto_mode']:
            # بدء التشغيل التلقائي
            context.job_queue.run_repeating(
                self.auto_create_orders,
                interval=self.config['auto_interval'],
                first=5,
                name='auto_orders'
            )
            
            message = (
                f"{EMOJIS['robot']} **التشغيل التلقائي مُفعّل!**\n\n"
                f"{EMOJIS['clock']} سيتم إنشاء طلب كل {self.config['auto_interval']} ثانية\n"
                f"{EMOJIS['target']} الحد الأقصى: {self.config['max_accounts_per_day']} حساب/يوم"
            )
        else:
            # إيقاف التشغيل التلقائي
            current_jobs = context.job_queue.get_jobs_by_name('auto_orders')
            for job in current_jobs:
                job.schedule_removal()
            
            message = f"{EMOJIS['warning']} **التشغيل التلقائي متوقف!**"
        
        keyboard = [[InlineKeyboardButton(f"{EMOJIS['refresh']} رجوع", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return MAIN_MENU
    
    async def auto_create_orders(self, context: ContextTypes.DEFAULT_TYPE):
        """إنشاء طلبات تلقائية"""
        if not self.config['auto_mode']:
            return
        
        # التحقق من الحد اليومي
        today_accounts = 0
        accounts = load_json_file(ACCOUNTS_FILE, [])
        today = datetime.now().date()
        
        for account in accounts:
            created_date = datetime.fromisoformat(account['created_at']).date()
            if created_date == today:
                today_accounts += 1
        
        if today_accounts >= self.config['max_accounts_per_day']:
            logger.warning("تم الوصول للحد الأقصى اليومي")
            return
        
        # إنشاء حساب وطلب
        account = self.api_manager.create_account()
        if account:
            self.api_manager.place_order(
                account['token'],
                self.config['default_service'],
                self.config['default_link'],
                self.config['default_quantity']
            )
            
            # إرسال إشعار للأدمن
            if self.config['notifications']:
                try:
                    await context.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=(
                            f"{EMOJIS['bell']} **طلب تلقائي جديد**\n"
                            f"{EMOJIS['user']} الحساب: `{account['username']}`\n"
                            f"{EMOJIS['tick']} تم إرسال {self.config['default_quantity']} متابع"
                        ),
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception as e:
                    logger.error(f"خطأ في إرسال الإشعار: {e}")
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإحصائيات"""
        query = update.callback_query
        stats = self.api_manager.get_stats()
        
        # حساب معدل النجاح
        success_rate = 0
        if stats['total_orders'] > 0:
            success_rate = (stats['successful_orders'] / stats['total_orders']) * 100
        
        message = (
            f"{EMOJIS['chart']} **الإحصائيات الكاملة**\n"
            f"{'='*30}\n\n"
            f"{EMOJIS['users']} **الحسابات:**\n"
            f"• إجمالي الحسابات: {format_number(stats['total_accounts'])}\n\n"
            f"{EMOJIS['package']} **الطلبات:**\n"
            f"• إجمالي الطلبات: {format_number(stats['total_orders'])}\n"
            f"• الطلبات الناجحة: {format_number(stats['successful_orders'])}\n"
            f"• الطلبات الفاشلة: {format_number(stats['failed_orders'])}\n"
            f"• معدل النجاح: {success_rate:.1f}%\n\n"
            f"{EMOJIS['gift']} **المتابعين:**\n"
            f"• إجمالي المتابعين المرسلين: {format_number(stats['total_followers_sent'])}\n\n"
            f"{EMOJIS['clock']} آخر تحديث: {stats.get('last_update', 'غير متاح')}"
        )
        
        keyboard = [
            [
                InlineKeyboardButton(f"{EMOJIS['refresh']} تحديث", callback_data='stats'),
                InlineKeyboardButton(f"{EMOJIS['refresh']} رجوع", callback_data='back_to_menu')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return MAIN_MENU
    
    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإعدادات"""
        query = update.callback_query
        
        auto_status = "مُفعّل" if self.config['auto_mode'] else "متوقف"
        notif_status = "مُفعّلة" if self.config['notifications'] else "متوقفة"
        
        message = (
            f"{EMOJIS['settings']} **الإعدادات الحالية**\n"
            f"{'='*30}\n\n"
            f"{EMOJIS['robot']} التشغيل التلقائي: **{auto_status}**\n"
            f"{EMOJIS['clock']} الفترة الزمنية: **{self.config['auto_interval']} ثانية**\n"
            f"{EMOJIS['target']} الحد اليومي: **{self.config['max_accounts_per_day']} حساب**\n\n"
            f"{EMOJIS['link']} الرابط الافتراضي:\n`{self.config['default_link']}`\n\n"
            f"{EMOJIS['package']} الكمية الافتراضية: **{self.config['default_quantity']}**\n"
            f"{EMOJIS['bell']} الإشعارات: **{notif_status}**"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("تغيير الفترة الزمنية", callback_data='change_interval'),
                InlineKeyboardButton("تغيير الحد اليومي", callback_data='change_limit')
            ],
            [
                InlineKeyboardButton("تغيير الرابط", callback_data='change_link'),
                InlineKeyboardButton("تغيير الكمية", callback_data='change_quantity')
            ],
            [
                InlineKeyboardButton("تبديل الإشعارات", callback_data='toggle_notifications'),
                InlineKeyboardButton(f"{EMOJIS['refresh']} رجوع", callback_data='back_to_menu')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return SETTINGS_MENU
    
    async def show_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض السجلات"""
        query = update.callback_query
        
        # آخر 10 طلبات
        orders = load_json_file(ORDERS_FILE, [])
        recent_orders = orders[-10:] if orders else []
        
        message = f"{EMOJIS['folder']} **آخر السجلات**\n{'='*30}\n\n"
        
        if recent_orders:
            for i, order in enumerate(reversed(recent_orders), 1):
                created_at = datetime.fromisoformat(order['created_at']).strftime('%Y-%m-%d %H:%M')
                status_emoji = EMOJIS['success'] if order['status'] == 'success' else EMOJIS['error']
                message += (
                    f"{i}. {status_emoji} Order #{order.get('order_id', 'N/A')}\n"
                    f"   الكمية: {order['quantity']} | {created_at}\n\n"
                )
        else:
            message += f"{EMOJIS['info']} لا توجد سجلات حتى الآن"
        
        keyboard = [[InlineKeyboardButton(f"{EMOJIS['refresh']} رجوع", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return MAIN_MENU
    
    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المساعدة"""
        query = update.callback_query
        
        message = (
            f"{EMOJIS['info']} **دليل الاستخدام**\n"
            f"{'='*30}\n\n"
            f"{EMOJIS['robot']} **الأوامر المتاحة:**\n"
            f"/start - بدء البوت\n"
            f"/stop - إيقاف البوت\n"
            f"/stats - عرض الإحصائيات\n"
            f"/help - عرض المساعدة\n\n"
            f"{EMOJIS['fire']} **المميزات:**\n"
            f"• إنشاء حسابات تلقائياً بدون تدخل\n"
            f"• إرسال طلبات متابعين لـ TikTok\n"
            f"• تشغيل تلقائي ذكي مع فترات عشوائية\n"
            f"• إحصائيات مفصلة وسجلات كاملة\n"
            f"• تحكم كامل في جميع الإعدادات\n"
            f"• إشعارات فورية للعمليات\n\n"
            f"{EMOJIS['shield']} **الأمان:**\n"
            f"• البوت محمي بصلاحيات الأدمن\n"
            f"• جميع البيانات محفوظة بشكل آمن\n"
            f"• توليد بيانات عشوائية ذكية\n\n"
            f"{EMOJIS['crown']} **المطور:** @zizo0022sasa\n"
            f"{EMOJIS['egypt']} **صنع بكل حب في مصر**"
        )
        
        keyboard = [[InlineKeyboardButton(f"{EMOJIS['refresh']} رجوع", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return MAIN_MENU
    
    async def back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """العودة للقائمة الرئيسية"""
        query = update.callback_query
        
        keyboard = [
            [
                InlineKeyboardButton(f"{EMOJIS['new']} طلب جديد", callback_data='new_order'),
                InlineKeyboardButton(f"{EMOJIS['robot']} تشغيل تلقائي", callback_data='auto_mode')
            ],
            [
                InlineKeyboardButton(f"{EMOJIS['chart']} الإحصائيات", callback_data='stats'),
                InlineKeyboardButton(f"{EMOJIS['settings']} الإعدادات", callback_data='settings')
            ],
            [
                InlineKeyboardButton(f"{EMOJIS['folder']} السجلات", callback_data='logs'),
                InlineKeyboardButton(f"{EMOJIS['info']} المساعدة", callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_message = (
            f"{EMOJIS['crown']} **القائمة الرئيسية**\n"
            f"{EMOJIS['fire']} اختار من الخيارات المتاحة:"
        )
        
        await query.edit_message_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return MAIN_MENU
    
    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إيقاف البوت"""
        user = update.effective_user
        
        if not is_admin(user.id):
            return ConversationHandler.END
        
        # إيقاف جميع المهام
        current_jobs = context.job_queue.jobs()
        for job in current_jobs:
            job.schedule_removal()
        
        await update.message.reply_text(
            f"{EMOJIS['warning']} تم إيقاف البوت!\n"
            f"استخدم /start للبدء من جديد"
        )
        
        return ConversationHandler.END
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأخطاء"""
        logger.error(f"خطأ: {context.error}")
        
        if update and update.effective_user and is_admin(update.effective_user.id):
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"{EMOJIS['error']} حدث خطأ:\n`{str(context.error)}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass

# ==============================================================================
# 🚀 التشغيل الرئيسي
# ==============================================================================

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    logger.info("بدء تشغيل البوت...")
    
    # إنشاء التطبيق
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # إنشاء البوت
    bot = EAFCBot()
    
    # إضافة معالج المحادثة
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', bot.start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(bot.handle_callback)
            ],
            SETTINGS_MENU: [
                CallbackQueryHandler(bot.handle_callback)
            ]
        },
        fallbacks=[CommandHandler('stop', bot.stop)]
    )
    
    # إضافة المعالجات
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('stats', bot.show_stats))
    application.add_handler(CommandHandler('help', bot.show_help))
    
    # معالج الأخطاء
    application.add_error_handler(bot.error_handler)
    
    # تعيين أوامر البوت
    commands = [
        BotCommand("start", "بدء البوت"),
        BotCommand("stop", "إيقاف البوت"),
        BotCommand("stats", "عرض الإحصائيات"),
        BotCommand("help", "المساعدة")
    ]
    
    async def post_init(application):
        await application.bot.set_my_commands(commands)
        logger.info(f"البوت جاهز! Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    
    application.post_init = post_init
    
    # بدء البوت
    logger.info("البوت شغال دلوقتي! 🚀")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()