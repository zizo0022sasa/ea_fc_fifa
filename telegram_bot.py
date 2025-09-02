#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 بوت تيليجرام مصري - النسخة النهائية الكاملة
👨‍💻 Dev: @zizo0022sasa
🇪🇬 Made in Egypt with ❤️
📅 آخر تحديث: 2024
✨ نظام البروكسيات المدمج بالكامل
"""

import os
import subprocess
import sys
import threading
import time


# ==============================================================================
# 🚀 تشغيل مدير البروكسيات تلقائياً في الخلفية
# ==============================================================================
def start_proxy_manager():
    """تشغيل proxy_manager.py كعملية منفصلة في الخلفية"""
    try:
        # التحقق من وجود الملف
        if not os.path.exists("proxy_manager.py"):
            print("⚠️ تحذير: ملف proxy_manager.py غير موجود!")
            print("📝 يرجى التأكد من وجود الملف في نفس المجلد")
            return None

        print("🌐 بدء تشغيل مدير البروكسيات...")

        # تشغيل proxy_manager.py كعملية منفصلة
        try:
            if sys.platform == "win32":
                # Windows - محاولة أخرى
                process = subprocess.Popen(
                    [sys.executable, "proxy_manager.py"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            else:
                # Linux/Mac
                process = subprocess.Popen(
                    [sys.executable, "proxy_manager.py"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setsid,
                )

            # انتظار قليل للتأكد من بدء العملية
            time.sleep(2)

            # التحقق من أن العملية تعمل
            if process.poll() is None:
                print(f"✅ مدير البروكسيات يعمل! PID: {process.pid}")
                return process
            else:
                print("❌ فشل تشغيل مدير البروكسيات - سيعمل البوت بدون بروكسي خارجي")
                return None

        except Exception as e:
            print(f"⚠️ لا يمكن تشغيل مدير البروكسيات تلقائياً: {e}")
            print("📝 يمكنك تشغيله يدوياً في نافذة أخرى: python proxy_manager.py")
            return None

    except Exception as e:
        print(f"⚠️ خطأ في تشغيل مدير البروكسيات: {e}")
        return None


# تشغيل مدير البروكسيات عند بدء البوت
proxy_manager_process = start_proxy_manager()

# انتظار 3 ثواني حتى يبدأ مدير البروكسيات في جمع البروكسيات
if proxy_manager_process:
    print("⏳ انتظار 3 ثواني لبدء جمع البروكسيات...")
    time.sleep(3)

# ==============================================================================
# الكود الأصلي للبوت مع إصلاح الأخطاء
# ==============================================================================

import asyncio
import json
import logging
import os
import random
import re
import string
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, urlparse

import aiohttp
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# ألوان للترمينال
try:
    from colorama import Back, Fore, Style
    from colorama import init as colorama_init

    colorama_init(autoreset=True)
    COLORAMA_OK = True
except ImportError:
    COLORAMA_OK = False

# حل مشكلة event loop على ويندوز
try:
    import nest_asyncio

    nest_asyncio.apply()
except Exception:
    pass

# ==============================================================================
# 🔐 الإعدادات المباشرة
# ==============================================================================
TELEGRAM_BOT_TOKEN = "7958170099:AAGmgK-AMlx1VyymR3yfUuvtOdnaj1POs_M"
ADMIN_ID = 1124247595
GROUP_ID = -4872486359  # جروب الإشعارات

# API Settings
API_BASE_URL = "https://freefollower.net/api"
FOLLOWERS_SERVICE_ID = 196  # خدمة المتابعين
LIKES_SERVICE_ID = 188  # خدمة اللايكات

# Files
ACCOUNTS_JSON = "accounts.json"
ACCOUNTS_TXT = "accounts.txt"
STATS_FILE = "stats.json"
QUEUE_FILE = "queue.json"
FOLLOWERS_CACHE_FILE = "followers_cache.json"
CANCELED_ORDERS_FILE = "canceled_orders.json"

# ملفات البروكسيات
PROXY_FILE = "working_proxies_freefollower.json"
PROXY_FILE_TXT = "working_proxies.txt"
PROXY_FILE_JSON = "working_proxies.json"

# Timing
TOKEN_COOLDOWN_HOURS = 25
MIN_WAIT_SECONDS = 5
MAX_WAIT_SECONDS = 10
MAX_ACCOUNT_CREATION_ATTEMPTS = 3

# Smart Mode
SMART_IDLE_ENABLED = False
SMART_DEFAULT_LINK = ""

# Live Updates Settings
UPDATE_INTERVAL = 5.0
GROUP_NOTIFY_ENABLED = True
MAX_UPDATE_ATTEMPTS = 3

# TikTok Analyzer Settings
TIKTOK_CACHE_DURATION = 300
TIKTOK_REQUEST_TIMEOUT = 10
TIKTOK_RATE_LIMIT_DELAY = 2
TIKTOK_MAX_RETRIES = 3

# Proxy Settings
PROXY_TIMEOUT = 20
PROXY_MAX_FAILURES = 3
PROXY_ROTATION_ENABLED = True
PROXY_AUTO_REMOVE = True
PROXY_TEST_ON_START = True
PROXY_REFRESH_INTERVAL = 3600  # ساعة واحدة


# ==============================================================================
# 🎨 نظام اللوجز الملون المحسن - للترمينال فقط
# ==============================================================================
class SuperColoredFormatter(logging.Formatter):
    """نظام لوجز احترافي بألوان واضحة للترمينال فقط"""

    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        message = record.getMessage()

        if "✅" in message or "نجح" in message or "SUCCESS" in message.upper():
            if COLORAMA_OK:
                return f"{Fore.BLACK}{Back.GREEN} ✅ SUCCESS {Style.RESET_ALL} {Fore.GREEN}{timestamp} ➜ {message}{Style.RESET_ALL}"
            return f"[✅ SUCCESS] {timestamp} ➜ {message}"

        if (
            "❌" in message
            or "فشل" in message
            or "FAILED" in message.upper()
            or "ERROR" in record.levelname
        ):
            if COLORAMA_OK:
                return f"{Fore.WHITE}{Back.RED} ❌ FAILED {Style.RESET_ALL} {Fore.RED}{timestamp} ➜ {message}{Style.RESET_ALL}"
            return f"[❌ FAILED] {timestamp} ➜ {message}"

        if "⚠️" in message or "WARNING" in record.levelname:
            if COLORAMA_OK:
                return f"{Fore.BLACK}{Back.YELLOW} ⚠️ WARNING {Style.RESET_ALL} {Fore.YELLOW}{timestamp} ➜ {message}{Style.RESET_ALL}"
            return f"[⚠️ WARNING] {timestamp} ➜ {message}"

        if "🔄" in message or "معالجة" in message:
            if COLORAMA_OK:
                return f"{Fore.WHITE}{Back.BLUE} 🔄 PROCESS {Style.RESET_ALL} {Fore.CYAN}{timestamp} ➜ {message}{Style.RESET_ALL}"
            return f"[🔄 PROCESS] {timestamp} ➜ {message}"

        if "🌐" in message or "بروكسي" in message or "proxy" in message.lower():
            if COLORAMA_OK:
                return f"{Fore.BLACK}{Back.CYAN} 🌐 PROXY {Style.RESET_ALL} {Fore.CYAN}{timestamp} ➜ {message}{Style.RESET_ALL}"
            return f"[🌐 PROXY] {timestamp} ➜ {message}"

        if "📊" in message or "إحصائيات" in message:
            if COLORAMA_OK:
                return f"{Fore.WHITE}{Back.MAGENTA} 📊 STATS {Style.RESET_ALL} {Fore.MAGENTA}{timestamp} ➜ {message}{Style.RESET_ALL}"
            return f"[📊 STATS] {timestamp} ➜ {message}"

        if COLORAMA_OK:
            level_colors = {"INFO": Fore.WHITE, "DEBUG": Fore.CYAN}
            color = level_colors.get(record.levelname, Fore.WHITE)
            return (
                f"{color}[{record.levelname}] {timestamp} ➜ {message}{Style.RESET_ALL}"
            )
        return f"[{record.levelname}] {timestamp} ➜ {message}"


# إعداد اللوجز للترمينال فقط - بدون ملفات
console_handler = logging.StreamHandler()
console_handler.setFormatter(SuperColoredFormatter())

# تكوين اللوجز بدون ملف
logging.basicConfig(level=logging.INFO, handlers=[console_handler])
logger = logging.getLogger("EgyptianBot")

# إضافة مستوى SUCCESS
logging.addLevelName(25, "SUCCESS")


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(25):
        self._log(25, message, args, **kwargs)


logging.Logger.success = success


# ==============================================================================
# 🌐 نظام البروكسيات المتقدم المدمج
# ==============================================================================
@dataclass
class ProxyData:
    """بيانات البروكسي"""

    ip: str
    port: int
    protocol: str = "http"
    response_time: float = field(default=0.0)
    working: bool = field(default=False)
    last_check: Optional[datetime] = field(default=None)
    success_targets: List[str] = field(default_factory=list)
    fail_count: int = field(default=0)
    success_count: int = field(default=0)

    @property
    def proxy_url(self) -> str:
        """الحصول على URL البروكسي"""
        if self.protocol in ["socks4", "socks5"]:
            return f"{self.protocol}://{self.ip}:{self.port}"
        return f"http://{self.ip}:{self.port}"

    @property
    def proxy_dict(self) -> dict:
        """الحصول على dictionary للـ requests"""
        url = self.proxy_url
        return {"http": url, "https": url}

    def to_json(self) -> dict:
        """تحويل لـ JSON"""
        return {
            "ip": self.ip,
            "port": self.port,
            "protocol": self.protocol,
            "response_time": self.response_time,
            "working": self.working,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "success_targets": self.success_targets,
            "fail_count": self.fail_count,
            "success_count": self.success_count,
        }

    @classmethod
    def from_json(cls, data: dict) -> "ProxyData":
        """إنشاء من JSON"""
        data = data.copy()
        if "last_check" in data and data["last_check"]:
            data["last_check"] = datetime.fromisoformat(data["last_check"])
        return cls(**data)


class ProxyManager:
    """مدير البروكسيات المتقدم"""

    def __init__(self):
        self.proxies: List[ProxyData] = []
        self.working_proxies: List[ProxyData] = []
        self.lock = threading.Lock()
        self.last_refresh = None
        self.proxy_sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://www.proxy-list.download/api/v1/get?type=https",
            "https://www.proxy-list.download/api/v1/get?type=socks4",
            "https://www.proxy-list.download/api/v1/get?type=socks5",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
        ]
        self.load_proxies()

    def load_proxies(self):
        """تحميل البروكسيات من الملفات"""
        loaded_proxies = []

        # تحميل من ملف JSON الرئيسي
        if os.path.exists(PROXY_FILE):
            try:
                with open(PROXY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "proxies" in data:
                        for proxy_data in data["proxies"]:
                            proxy = ProxyData.from_json(proxy_data)
                            loaded_proxies.append(proxy)
                    elif isinstance(data, list):
                        for proxy_data in data:
                            if isinstance(proxy_data, dict):
                                proxy = ProxyData(**proxy_data)
                                loaded_proxies.append(proxy)
                    logger.info(
                        f"🌐 تم تحميل {len(loaded_proxies)} بروكسي من {PROXY_FILE}"
                    )
            except Exception as e:
                logger.error(f"❌ خطأ في تحميل {PROXY_FILE}: {e}")

        # تحميل من ملف JSON إضافي
        if os.path.exists(PROXY_FILE_JSON) and len(loaded_proxies) == 0:
            try:
                with open(PROXY_FILE_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                try:
                                    proxy = ProxyData(
                                        ip=item.get(
                                            "ip", item.get("proxy", "").split(":")[0]
                                        ),
                                        port=int(
                                            item.get(
                                                "port",
                                                item.get("proxy", ":0").split(":")[1],
                                            )
                                        ),
                                        protocol=item.get("protocol", "http"),
                                    )
                                    loaded_proxies.append(proxy)
                                except:
                                    pass
                    logger.info(
                        f"🌐 تم تحميل {len(loaded_proxies)} بروكسي من {PROXY_FILE_JSON}"
                    )
            except Exception as e:
                logger.error(f"❌ خطأ في تحميل {PROXY_FILE_JSON}: {e}")

        # تحميل من ملف TXT
        if os.path.exists(PROXY_FILE_TXT) and len(loaded_proxies) == 0:
            try:
                with open(PROXY_FILE_TXT, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and ":" in line and not line.startswith("#"):
                            parts = line.split(":")
                            if len(parts) == 2:
                                try:
                                    proxy = ProxyData(
                                        ip=parts[0], port=int(parts[1]), protocol="http"
                                    )
                                    loaded_proxies.append(proxy)
                                except:
                                    pass
                logger.info(
                    f"🌐 تم تحميل {len(loaded_proxies)} بروكسي من {PROXY_FILE_TXT}"
                )
            except Exception as e:
                logger.error(f"❌ خطأ في تحميل {PROXY_FILE_TXT}: {e}")

        with self.lock:
            self.proxies = loaded_proxies
            self.working_proxies = [p for p in loaded_proxies if p.working]

        if len(self.proxies) == 0:
            logger.warning("⚠️ لا توجد بروكسيات محملة! سيعمل البوت بدون بروكسي")
        else:
            logger.info(f"✅ إجمالي البروكسيات المحملة: {len(self.proxies)}")

    def save_proxies(self):
        """حفظ البروكسيات للملف"""
        try:
            data = {
                "total": len(self.proxies),
                "working": len(self.working_proxies),
                "last_update": datetime.now().isoformat(),
                "proxies": [p.to_json() for p in self.proxies],
            }

            with open(PROXY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 تم حفظ {len(self.proxies)} بروكسي")
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ البروكسيات: {e}")

    async def test_proxy(
        self, proxy: ProxyData, target_url: str = "https://freefollower.net/"
    ) -> bool:
        """اختبار البروكسي"""
        try:
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    target_url,
                    proxy=(
                        proxy.proxy_url
                        if proxy.protocol != "http"
                        else f"http://{proxy.ip}:{proxy.port}"
                    ),
                    timeout=aiohttp.ClientTimeout(total=PROXY_TIMEOUT),
                    ssl=False,
                ) as response:
                    if response.status == 200:
                        proxy.response_time = time.time() - start_time
                        proxy.working = True
                        proxy.last_check = datetime.now()
                        proxy.success_count += 1
                        if target_url not in proxy.success_targets:
                            proxy.success_targets.append(target_url)
                        return True
        except Exception:
            proxy.fail_count += 1
            proxy.working = False

        return False

    async def refresh_proxies(self):
        """تحديث البروكسيات من المصادر"""
        logger.info("🔄 بدء تحديث البروكسيات...")
        new_proxies = []

        async with aiohttp.ClientSession() as session:
            for source in self.proxy_sources:
                try:
                    async with session.get(source, timeout=10) as response:
                        if response.status == 200:
                            text = await response.text()
                            lines = text.strip().split("\n")

                            for line in lines:
                                if ":" in line:
                                    parts = line.strip().split(":")
                                    if len(parts) == 2:
                                        try:
                                            proxy = ProxyData(
                                                ip=parts[0],
                                                port=int(parts[1]),
                                                protocol=self._detect_protocol(source),
                                            )
                                            new_proxies.append(proxy)
                                        except:
                                            pass
                except Exception:
                    continue

        # اختبار البروكسيات الجديدة
        logger.info(f"🔍 اختبار {len(new_proxies)} بروكسي جديد...")
        working = []

        for proxy in new_proxies[:100]:  # اختبر أول 100 فقط
            if await self.test_proxy(proxy):
                working.append(proxy)

        with self.lock:
            # دمج البروكسيات الجديدة مع القديمة
            existing = {(p.ip, p.port) for p in self.proxies}
            for proxy in working:
                if (proxy.ip, proxy.port) not in existing:
                    self.proxies.append(proxy)

            self.working_proxies = [p for p in self.proxies if p.working]
            self.last_refresh = datetime.now()

        self.save_proxies()
        logger.info(
            f"✅ تم تحديث البروكسيات: {len(self.working_proxies)} شغال من {len(self.proxies)}"
        )

    def _detect_protocol(self, source: str) -> str:
        """تحديد البروتوكول من المصدر"""
        if "socks4" in source.lower():
            return "socks4"
        elif "socks5" in source.lower():
            return "socks5"
        elif "https" in source.lower():
            return "https"
        return "http"

    def get_best_proxy(self) -> Optional[ProxyData]:
        """الحصول على أفضل بروكسي"""
        with self.lock:
            if not self.working_proxies:
                # جرب كل البروكسيات مرة أخرى
                self.working_proxies = [
                    p for p in self.proxies if p.fail_count < PROXY_MAX_FAILURES
                ]

            if not self.working_proxies:
                return None

            # رتب حسب السرعة والنجاح
            self.working_proxies.sort(
                key=lambda p: (-p.success_count, p.fail_count, p.response_time)
            )

            return self.working_proxies[0]

    def use_proxy(
        self, proxy: ProxyData, url: str, **kwargs
    ) -> Optional[requests.Response]:
        """استخدام البروكسي لطلب HTTP"""
        try:
            response = requests.request(
                kwargs.pop("method", "GET"),
                url,
                proxies=proxy.proxy_dict,
                timeout=kwargs.pop("timeout", PROXY_TIMEOUT),
                verify=False,
                **kwargs,
            )

            if response.status_code == 200:
                proxy.success_count += 1
                return response
            else:
                proxy.fail_count += 1

        except Exception:
            proxy.fail_count += 1

        # حذف البروكسي إذا فشل كثيراً
        if PROXY_AUTO_REMOVE and proxy.fail_count >= PROXY_MAX_FAILURES:
            with self.lock:
                if proxy in self.working_proxies:
                    self.working_proxies.remove(proxy)
                if proxy in self.proxies:
                    self.proxies.remove(proxy)
            logger.warning(f"🗑️ تم حذف البروكسي الفاشل: {proxy.ip}:{proxy.port}")
            self.save_proxies()

        return None

    def get_statistics(self) -> dict:
        """إحصائيات البروكسيات"""
        with self.lock:
            total = len(self.proxies)
            working = len(self.working_proxies)
            failed = len(
                [p for p in self.proxies if p.fail_count >= PROXY_MAX_FAILURES]
            )

            protocols = {}
            for p in self.proxies:
                protocols[p.protocol] = protocols.get(p.protocol, 0) + 1

            # أفضل المواقع
            sites = {}
            for p in self.working_proxies:
                for site in p.success_targets:
                    sites[site] = sites.get(site, 0) + 1

            top_sites = sorted(sites.items(), key=lambda x: x[1], reverse=True)

            # متوسط السرعة
            speeds = [
                p.response_time * 1000
                for p in self.working_proxies
                if p.response_time > 0
            ]
            avg_speed = sum(speeds) / len(speeds) if speeds else 0

            return {
                "total": total,
                "working": working,
                "failed": failed,
                "protocols": protocols,
                "top_sites": top_sites,
                "avg_speed_ms": avg_speed,
                "last_refresh": (
                    self.last_refresh.isoformat() if self.last_refresh else None
                ),
            }


# ==============================================================================
# 🔍 TikTok Analyzer Fortress - مع دعم البروكسيات
# ==============================================================================
class TikTokAnalyzer:
    """قلعة معزولة لفحص متابعين TikTok بذكاء"""

    def __init__(self, proxy_manager: ProxyManager = None):
        self.cache: Dict[str, Dict] = {}
        self.last_request_time = 0
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ]
        self.proxy_manager = proxy_manager
        self.load_cache()

    def load_cache(self):
        """تحميل الكاش من الملف"""
        try:
            if os.path.exists(FOLLOWERS_CACHE_FILE):
                with open(FOLLOWERS_CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    now = time.time()
                    self.cache = {
                        k: v
                        for k, v in data.items()
                        if now - v.get("timestamp", 0) < TIKTOK_CACHE_DURATION
                    }
                    logger.info(f"📂 تم تحميل كاش المتابعين: {len(self.cache)} مدخل")
        except Exception as e:
            logger.warning(f"⚠️ خطأ في تحميل الكاش: {e}")
            self.cache = {}

    def save_cache(self):
        """حفظ الكاش للملف"""
        try:
            with open(FOLLOWERS_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ الكاش: {e}")

    def extract_username(self, link: str) -> Optional[str]:
        """استخراج اسم المستخدم من الرابط"""
        link = link.strip()

        if link.startswith("@"):
            return link[1:]

        patterns = [
            r"tiktok\.com/@([a-zA-Z0-9._]+)/video",
            r"tiktok\.com/@([a-zA-Z0-9._]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                return match.group(1)

        if any(short in link for short in ["vm.tiktok", "vt.tiktok"]):
            resolved = self._resolve_short_link(link)
            if resolved:
                return resolved

        return None

    def _resolve_short_link(self, short_link: str) -> Optional[str]:
        """حل الرابط المختصر مع البروكسي"""
        try:
            headers = {"User-Agent": random.choice(self.user_agents)}

            # استخدام بروكسي إذا كان متاحاً
            if self.proxy_manager:
                proxy = self.proxy_manager.get_best_proxy()
                if proxy:
                    resp = self.proxy_manager.use_proxy(
                        proxy,
                        short_link,
                        method="HEAD",
                        allow_redirects=True,
                        timeout=5,
                        headers=headers,
                    )
                    if resp:
                        final_url = resp.url
                    else:
                        # جرب بدون بروكسي
                        resp = requests.head(
                            short_link, allow_redirects=True, timeout=5, headers=headers
                        )
                        final_url = resp.url
                else:
                    resp = requests.head(
                        short_link, allow_redirects=True, timeout=5, headers=headers
                    )
                    final_url = resp.url
            else:
                resp = requests.head(
                    short_link, allow_redirects=True, timeout=5, headers=headers
                )
                final_url = resp.url

            patterns = [
                r"tiktok\.com/@([a-zA-Z0-9._]+)/video",
                r"tiktok\.com/@([a-zA-Z0-9._]+)",
            ]

            for pattern in patterns:
                match = re.search(pattern, final_url)
                if match:
                    return match.group(1)

            return None
        except Exception as e:
            logger.debug(f"فشل حل الرابط المختصر: {e}")
            return None

    def extract_username_from_any_link(self, link: str) -> str:
        """استخراج اسم المستخدم من أي نوع رابط"""
        username = self.extract_username(link)

        if username:
            return username

        if "video" in link.lower() or "vt.tiktok" in link:
            return "video"
        elif "vm.tiktok" in link:
            return "profile"
        else:
            return "tiktok"

    def _respect_rate_limit(self):
        """احترام حدود الطلبات"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < TIKTOK_RATE_LIMIT_DELAY:
            sleep_time = TIKTOK_RATE_LIMIT_DELAY - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def get_followers_count(self, link: str) -> Optional[int]:
        """الحصول على عدد المتابعين مع البروكسي"""
        username = self.extract_username(link)
        if not username:
            logger.warning(f"⚠️ فشل استخراج اسم المستخدم من: {link}")
            return None

        # فحص الكاش
        cache_key = username.lower()
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached["timestamp"] < TIKTOK_CACHE_DURATION:
                logger.info(
                    f"📦 استخدام الكاش للمستخدم: @{username} ({cached['followers']:,} متابع)"
                )
                return cached["followers"]

        self._respect_rate_limit()

        # محاولة جلب عدد المتابعين مع البروكسي
        for attempt in range(TIKTOK_MAX_RETRIES):
            try:
                followers = self._fetch_followers_api(username)
                if followers is not None:
                    self.cache[cache_key] = {
                        "username": username,
                        "followers": followers,
                        "timestamp": time.time(),
                    }
                    self.save_cache()
                    logger.info(f"🔍 تم فحص @{username}: {followers:,} متابع")
                    return followers

            except Exception as e:
                logger.warning(f"⚠️ محاولة {attempt + 1}/{TIKTOK_MAX_RETRIES} فشلت: {e}")
                if attempt < TIKTOK_MAX_RETRIES - 1:
                    time.sleep(2**attempt)

        logger.error(f"❌ فشل فحص المتابعين لـ @{username}")
        return None

    def _fetch_followers_api(self, username: str) -> Optional[int]:
        """جلب المتابعين من API مع البروكسي"""
        try:
            url = f"https://www.tiktok.com/@{username}"
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            }

            # محاولة مع بروكسي
            if self.proxy_manager:
                proxy = self.proxy_manager.get_best_proxy()
                if proxy:
                    resp = self.proxy_manager.use_proxy(
                        proxy, url, headers=headers, timeout=TIKTOK_REQUEST_TIMEOUT
                    )
                    if resp:
                        text = resp.text
                        resp_status = resp.status_code
                    else:
                        # جرب بدون بروكسي
                        resp = requests.get(
                            url, headers=headers, timeout=TIKTOK_REQUEST_TIMEOUT
                        )
                        text = resp.text
                        resp_status = resp.status_code
                else:
                    resp = requests.get(
                        url, headers=headers, timeout=TIKTOK_REQUEST_TIMEOUT
                    )
                    text = resp.text
                    resp_status = resp.status_code
            else:
                resp = requests.get(
                    url, headers=headers, timeout=TIKTOK_REQUEST_TIMEOUT
                )
                text = resp.text
                resp_status = resp.status_code

            if resp_status == 200:
                patterns = [
                    r'"followerCount":(\d+)',
                    r'followers":"([\d.]+[KMB]?)"',
                    r'data-e2e="followers-count">([^<]+)</strong>',
                ]

                for pattern in patterns:
                    match = re.search(pattern, text)
                    if match:
                        followers_str = match.group(1)
                        return self._parse_followers_string(followers_str)

        except Exception as e:
            logger.debug(f"API fetch failed: {e}")

        return None

    def _parse_followers_string(self, followers_str: str) -> int:
        """تحويل نص المتابعين لرقم"""
        try:
            if followers_str.isdigit():
                return int(followers_str)

            followers_str = followers_str.upper().replace(",", "")

            if "K" in followers_str:
                return int(float(followers_str.replace("K", "")) * 1000)
            elif "M" in followers_str:
                return int(float(followers_str.replace("M", "")) * 1000000)
            elif "B" in followers_str:
                return int(float(followers_str.replace("B", "")) * 1000000000)

            return int(float(followers_str))
        except:
            return 0

    def format_followers(self, count: Optional[int]) -> str:
        """تنسيق عدد المتابعين للعرض"""
        if count is None:
            return "غير متاح"
        return f"{count:,}"


# ==============================================================================
# 🛠️ الدوال المساعدة
# ==============================================================================
def generate_human_credentials():
    """توليد بيانات حساب بشرية واقعية"""
    vowels = "aeiou"
    consonants = "bcdfghjklmnprstvwxyz"

    name_part1 = "".join(random.choices(consonants, k=1)) + random.choice(vowels)
    name_part2 = random.choice(consonants) + random.choice(vowels)
    name_part3 = random.choice(consonants) + random.choice(vowels)

    username_styles = [
        lambda: f"{name_part1}{name_part2}{name_part3}{random.randint(1990, 2005)}",
        lambda: f"{name_part1}{name_part2}{name_part3}_{random.randint(10, 99)}",
        lambda: f"{name_part1}{name_part2}_{random.randint(70, 99)}",
    ]

    username = random.choice(username_styles)()
    email_domains = ["gmail.com", "outlook.com", "yahoo.com"]
    email = f"{username}@{random.choice(email_domains)}"

    pass_letters = "".join(random.choices(string.ascii_letters, k=5))
    password = f"{pass_letters.capitalize()}{random.randint(1990, 2005)}{random.choice('!@#$*')}"

    return username, email, password


def rand_wait():
    """انتظار عشوائي ذكي"""
    return random.uniform(MIN_WAIT_SECONDS, MAX_WAIT_SECONDS)


def compact_accounts_file():
    """تحويل ملف accounts.json إلى سطر واحد لكل حساب"""
    try:
        if os.path.exists(ACCOUNTS_JSON):
            with open(ACCOUNTS_JSON, "r", encoding="utf-8") as f:
                accounts = json.load(f)

            with open(ACCOUNTS_JSON, "w", encoding="utf-8") as f:
                f.write("[\n")
                for i, account in enumerate(accounts):
                    compact_json = json.dumps(
                        account, ensure_ascii=False, separators=(",", ":")
                    )
                    if i < len(accounts) - 1:
                        f.write(f"  {compact_json},\n")
                    else:
                        f.write(f"  {compact_json}\n")
                f.write("]")

            logger.info(f"✅ تم تحويل {ACCOUNTS_JSON} إلى سطر واحد لكل حساب")
            return True
    except Exception as e:
        logger.error(f"❌ خطأ في تحويل الملف: {e}")
        return False


# ==============================================================================
# 📋 نظام الطابور المحسن
# ==============================================================================
class QueueManager:
    def __init__(self):
        self.queues: Dict[str, List[Dict]] = {}
        self.active_orders: List[str] = []
        self.order_counter: Dict[str, int] = {}
        self.canceled_orders: Dict[str, List[Dict]] = {}
        self.load()

    def load(self):
        try:
            if os.path.exists(QUEUE_FILE):
                with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.queues = data.get("queues", {})
                    self.active_orders = data.get("active_orders", [])
                    self.order_counter = data.get("order_counter", {})
                    logger.info(
                        f"📂 تم تحميل الطابور: {len(self.active_orders)} طلب نشط"
                    )

            if os.path.exists(CANCELED_ORDERS_FILE):
                with open(CANCELED_ORDERS_FILE, "r", encoding="utf-8") as f:
                    self.canceled_orders = json.load(f)
                    logger.info(f"📂 تم تحميل الطلبات الملغاة")

        except Exception as e:
            logger.error(f"❌ خطأ في تحميل الطابور: {e}")
            self.queues, self.active_orders, self.order_counter = {}, [], {}
            self.canceled_orders = {}

    def save(self):
        try:
            with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "queues": self.queues,
                        "active_orders": self.active_orders,
                        "order_counter": self.order_counter,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            with open(CANCELED_ORDERS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.canceled_orders, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"❌ خطأ في حفظ الطابور: {e}")

    def cancel_order(self, user_id: str, order_number: int) -> Tuple[bool, str]:
        """إلغاء طلب محدد"""
        user_id = str(user_id)

        if user_id not in self.queues:
            return False, "❌ لا توجد طلبات لك!"

        order_found = None
        for order in self.queues[user_id]:
            if order.get("order_number") == order_number:
                order_found = order
                break

        if not order_found:
            return False, f"❌ لم يتم العثور على الطلب #{order_number}"

        if order_found["status"] == "completed":
            return False, "❌ لا يمكن إلغاء طلب مكتمل!"

        if order_found["status"] == "canceled":
            return False, "❌ هذا الطلب ملغي بالفعل!"

        completed_amount = order_found["completed"] * 10
        service_type = order_found.get("service_type", "متابعين")
        quantity = order_found.get("quantity", 0)
        remaining = quantity - completed_amount

        order_found["status"] = "canceled"
        order_found["canceled_at"] = datetime.now().isoformat()
        order_found["completed_amount"] = completed_amount
        order_found["remaining_amount"] = remaining

        order_id = order_found["order_id"]
        if order_id in self.active_orders:
            self.active_orders.remove(order_id)

        if user_id not in self.canceled_orders:
            self.canceled_orders[user_id] = []
        self.canceled_orders[user_id].append(order_found)

        self.save()

        logger.info(f"🚫 تم إلغاء الطلب #{order_number} للعميل {user_id}")

        msg = f"✅ **تم إلغاء الطلب بنجاح!**\n\n"
        msg += f"📊 **تفاصيل الطلب الملغي:**\n"
        msg += f"• رقم الطلب: #{order_number}\n"
        msg += f"• النوع: {service_type}\n"
        msg += f"• الكمية المطلوبة: {quantity:,}\n"

        if completed_amount > 0:
            msg += f"\n⚠️ **ملاحظة مهمة:**\n"
            msg += f"• تم إرسال: **{completed_amount:,}** {service_type} ✅\n"
            msg += f"• لم يتم إرسال: **{remaining:,}** {service_type} ❌\n"
            msg += f"• التقدم: {order_found['completed']}/{order_found['accounts_needed']} حساب\n"
        else:
            msg += f"• الحالة: تم الإلغاء قبل البدء ✅\n"

        return True, msg

    def get_user_orders(self, user_id: str) -> List[Dict]:
        """الحصول على جميع طلبات المستخدم النشطة"""
        user_id = str(user_id)
        if user_id not in self.queues:
            return []

        return [
            order
            for order in self.queues[user_id]
            if order["status"] != "completed" and order["status"] != "canceled"
        ]

    def add_order(
        self,
        user_id: str,
        link: str,
        quantity: int,
        initial_followers: Optional[int] = None,
        service_type: str = "متابعين",
        service_id: int = FOLLOWERS_SERVICE_ID,
        username: str = None,
    ) -> Tuple[str, int]:

        if user_id not in self.order_counter:
            self.order_counter[user_id] = 0
        self.order_counter[user_id] += 1
        order_number = self.order_counter[user_id]

        accounts_needed = (quantity // 10) + (1 if quantity % 10 > 0 else 0)
        order_id = f"order_{user_id}_{int(time.time())}"

        order = {
            "order_id": order_id,
            "order_number": order_number,
            "user_id": user_id,
            "link": link,
            "username": username,
            "service_type": service_type,
            "service_id": service_id,
            "quantity": quantity,
            "initial_followers": initial_followers,
            "completed": 0,
            "accounts_needed": accounts_needed,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }

        if user_id not in self.queues:
            self.queues[user_id] = []
        self.queues[user_id].append(order)
        self.active_orders.append(order_id)
        self.save()

        logger.info(
            f"📝 طلب جديد #{order_number} للعميل {user_id} - نوع: {service_type}"
        )
        return order_id, order_number

    def get_next_order(self) -> Optional[Dict]:
        if not self.active_orders:
            return None

        for order_id in self.active_orders[:]:
            for user_id, orders in self.queues.items():
                for order in orders:
                    if order["order_id"] == order_id and order["status"] == "pending":
                        if order["completed"] < order["accounts_needed"]:
                            self.active_orders.remove(order_id)
                            self.active_orders.append(order_id)
                            return order
        return None

    def update_order_progress(self, order_id: str, success: bool):
        for user_id, orders in self.queues.items():
            for order in orders[:]:  # نسخة من القائمة للتعديل الآمن
                if order["order_id"] == order_id:
                    if success:
                        order["completed"] += 1
                        order_num = order.get("order_number", "N/A")
                        progress = f"{order['completed']}/{order['accounts_needed']}"
                        service_type = order.get("service_type", "متابعين")
                        logger.info(
                            f"✅ نجح إرسال {service_type}! التقدم: {progress} للطلب #{order_num}"
                        )

                        if order["completed"] >= order["accounts_needed"]:
                            order["status"] = "completed"
                            if order_id in self.active_orders:
                                self.active_orders.remove(order_id)
                            logger.info(
                                f"✅ اكتمل الطلب #{order_num} بنجاح للعميل {user_id} 🎉"
                            )

                            # حذف الطلب المكتمل من القائمة
                            self.queues[user_id].remove(order)

                            # إذا لم يعد للمستخدم طلبات، احذف مفتاحه
                            if len(self.queues[user_id]) == 0:
                                del self.queues[user_id]

                            logger.info(f"🗑️ تم حذف الطلب المكتمل #{order_num} من الملف")

                    self.save()
                    return

    def status_markdown(self) -> str:
        # عد الطلبات النشطة فقط (غير المكتملة)
        active_orders = []
        for orders in self.queues.values():
            for order in orders:
                if order["status"] == "pending":
                    active_orders.append(order)

        active = len(active_orders)

        # عد الطلبات الملغاة من ملف منفصل
        canceled = 0
        for canceled_list in self.canceled_orders.values():
            canceled += len(canceled_list)

        status = f"📊 **حالة الطابور:**\n"
        status += f"• طلبات نشطة: {active}\n"
        status += f"• طلبات ملغاة: {canceled}\n\n"

        if active > 0:
            status += "**الطلبات النشطة:**\n"
            for user_id, orders in self.queues.items():
                active_user_orders = [o for o in orders if o["status"] == "pending"]
                if active_user_orders:
                    status += f"**العميل {user_id}:**\n"
                    for order in active_user_orders[-3:]:  # آخر 3 طلبات نشطة فقط
                        order_num = order.get("order_number", "N/A")
                        service_type = order.get("service_type", "متابعين")
                        status += f"  • #{order_num} ({service_type}): {order['completed']}/{order['accounts_needed']} ⏳\n"
        else:
            status += "✨ **لا توجد طلبات نشطة حالياً**"

        return status


# ==============================================================================
# 🔑 مدير الحسابات المحسن مع دعم البروكسيات
# ==============================================================================
class AccountManager:
    def __init__(self, proxy_manager: ProxyManager = None):
        compact_accounts_file()
        self.accounts: List[Dict] = self.load_accounts()
        self.round_index = 0
        self.proxy_manager = proxy_manager

    def load_accounts(self) -> List[Dict]:
        accounts: List[Dict] = []
        seen = set()

        if os.path.exists(ACCOUNTS_JSON):
            try:
                with open(ACCOUNTS_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f) or []
                    if isinstance(data, list):
                        for a in data:
                            tok = a.get("token")
                            if tok and tok not in seen:
                                a.setdefault("use_count", 0)
                                a.setdefault("auto_created", False)
                                a.setdefault("username", "unknown")
                                a.setdefault("email", "")
                                a.setdefault("password", "")
                                a.setdefault("created_at", datetime.now().isoformat())
                                a.setdefault("last_used", None)
                                accounts.append(a)
                                seen.add(tok)
                        logger.info(
                            f"📂 تم تحميل {len(accounts)} حساب من {ACCOUNTS_JSON}"
                        )
            except Exception as e:
                logger.warning(f"⚠️ تعذر قراءة {ACCOUNTS_JSON}: {e}")

        if os.path.exists(ACCOUNTS_TXT):
            try:
                with open(ACCOUNTS_TXT, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            a = json.loads(line)
                            tok = a.get("token")
                            if tok and tok not in seen:
                                a.setdefault("use_count", 0)
                                a.setdefault("auto_created", False)
                                a.setdefault("username", a.get("username", "imported"))
                                a.setdefault("email", a.get("email", ""))
                                a.setdefault("password", a.get("password", ""))
                                a.setdefault("created_at", datetime.now().isoformat())
                                a.setdefault("last_used", None)
                                accounts.append(a)
                                seen.add(tok)
                        except:
                            continue
                logger.info(f"📂 تم قراءة حسابات إضافية من {ACCOUNTS_TXT}")
            except Exception as e:
                logger.warning(f"⚠️ تعذر قراءة {ACCOUNTS_TXT}: {e}")

        available = self._count_available_accounts(accounts)
        logger.info(f"📊 إحصائيات الحسابات: {available} متاح من {len(accounts)} إجمالي")

        return accounts

    def _count_available_accounts(self, accounts: List[Dict]) -> int:
        now = datetime.now()
        available = 0
        for acc in accounts:
            last_used = acc.get("last_used")
            if last_used is None:
                available += 1
            else:
                try:
                    last_used_time = datetime.fromisoformat(last_used)
                    hours = (now - last_used_time).total_seconds() / 3600
                    if hours >= TOKEN_COOLDOWN_HOURS:
                        available += 1
                except:
                    pass
        return available

    def save_accounts(self):
        """حفظ الحسابات بسطر واحد لكل حساب"""
        try:
            temp_file = f"{ACCOUNTS_JSON}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("[\n")
                for i, account in enumerate(self.accounts):
                    compact_json = json.dumps(
                        account, ensure_ascii=False, separators=(",", ":")
                    )
                    if i < len(self.accounts) - 1:
                        f.write(f"  {compact_json},\n")
                    else:
                        f.write(f"  {compact_json}\n")
                f.write("]")

            if os.path.exists(ACCOUNTS_JSON):
                os.remove(ACCOUNTS_JSON)
            os.rename(temp_file, ACCOUNTS_JSON)

            logger.debug(f"💾 تم حفظ {len(self.accounts)} حساب")
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ الحسابات: {e}")

    @staticmethod
    def validate_token_format(token: str) -> bool:
        if not token:
            return False
        return bool(re.match(r"^[a-zA-Z0-9]{20,100}$", token))

    def _append_to_txt_legacy(self, account: Dict):
        try:
            with open(ACCOUNTS_TXT, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "token": account.get("token"),
                            "username": account.get("username", "imported"),
                            "password": account.get("password", ""),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except:
            pass

    def create_new_account(self) -> Optional[Dict]:
        """إنشاء حساب جديد مع البروكسي"""
        for attempt in range(MAX_ACCOUNT_CREATION_ATTEMPTS):
            try:
                logger.info(
                    f"🔄 محاولة إنشاء حساب جديد... (محاولة {attempt + 1}/{MAX_ACCOUNT_CREATION_ATTEMPTS})"
                )
                username, email, password = generate_human_credentials()

                payload = {"login": username, "email": email, "password": password}

                time.sleep(random.uniform(1.5, 3.5))

                # محاولة مع بروكسي
                if self.proxy_manager:
                    proxy = self.proxy_manager.get_best_proxy()
                    if proxy:
                        logger.info(f"🌐 استخدام بروكسي لإنشاء الحساب")
                        resp_obj = self.proxy_manager.use_proxy(
                            proxy,
                            f"{API_BASE_URL}/register",
                            method="POST",
                            json=payload,
                            headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                                "Accept": "application/json",
                                "Content-Type": "application/json",
                            },
                        )
                        if resp_obj:
                            resp = resp_obj
                        else:
                            # جرب بدون بروكسي
                            resp = requests.post(
                                f"{API_BASE_URL}/register",
                                json=payload,
                                timeout=20,
                                headers={
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                                    "Accept": "application/json",
                                    "Content-Type": "application/json",
                                },
                            )
                    else:
                        resp = requests.post(
                            f"{API_BASE_URL}/register",
                            json=payload,
                            timeout=20,
                            headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                                "Accept": "application/json",
                                "Content-Type": "application/json",
                            },
                        )
                else:
                    resp = requests.post(
                        f"{API_BASE_URL}/register",
                        json=payload,
                        timeout=20,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                        },
                    )

                if resp.status_code == 201:
                    data = resp.json()
                    api_token = data.get("api_token")

                    if api_token and self.validate_token_format(api_token):
                        acc = {
                            "token": api_token,
                            "username": username,
                            "email": email,
                            "password": password,
                            "created_at": datetime.now().isoformat(),
                            "last_used": None,
                            "use_count": 0,
                            "auto_created": True,
                        }
                        self.accounts.append(acc)
                        self.save_accounts()
                        self._append_to_txt_legacy(acc)

                        logger.info(f"✅ تم إنشاء الحساب '{username}' بنجاح!")
                        return acc

                elif resp.status_code == 429:
                    logger.warning("⚠️ Rate limited - انتظار...")
                    time.sleep(random.uniform(8, 15))
                else:
                    logger.error(f"❌ فشل إنشاء الحساب: {resp.text[:100]}")
                    time.sleep(random.uniform(3, 6))

            except Exception as e:
                logger.error(f"❌ خطأ في إنشاء الحساب: {e}")
                time.sleep(random.uniform(3, 6))

        logger.error(f"❌ فشلت جميع محاولات إنشاء حساب جديد!")
        return None

    def add_account(self, account_data: str) -> str:
        try:
            if account_data.strip().startswith("{"):
                data = json.loads(account_data)
                token = data.get("token", "")
                username = data.get("username", "imported")
                email = data.get("email", "")
                password = data.get("password", "")
            else:
                token = account_data.strip()
                username, email, password = "imported", "", ""

            if not self.validate_token_format(token):
                return "❌ صيغة التوكن غير صحيحة!"

            for a in self.accounts:
                if a.get("token") == token:
                    return "⚠️ التوكن موجود بالفعل!"

            acc = {
                "token": token,
                "username": username,
                "email": email,
                "password": password,
                "created_at": datetime.now().isoformat(),
                "last_used": None,
                "use_count": 0,
                "auto_created": False,
            }
            self.accounts.append(acc)
            self.save_accounts()
            self._append_to_txt_legacy(acc)

            return f"✅ تم إضافة الحساب بنجاح!\n👤 المستخدم: {username}\n📊 إجمالي الحسابات: {len(self.accounts)}"

        except Exception as e:
            return f"❌ خطأ: {e}"

    def get_available_account(self) -> Optional[Dict]:
        now = datetime.now()
        available_accounts = []

        for acc in self.accounts:
            last_used = acc.get("last_used")
            if last_used is None:
                available_accounts.append(acc)
            else:
                try:
                    last_used_time = datetime.fromisoformat(last_used)
                    hours = (now - last_used_time).total_seconds() / 3600
                    if hours >= TOKEN_COOLDOWN_HOURS:
                        available_accounts.append(acc)
                except:
                    continue

        if not available_accounts:
            logger.warning(
                f"⚠️ لا توجد حسابات متاحة! (كل الـ {len(self.accounts)} حساب في فترة الانتظار)"
            )
            return None

        available_accounts.sort(
            key=lambda a: (a.get("use_count", 0), a.get("last_used") or "1900-01-01")
        )
        selected = available_accounts[self.round_index % len(available_accounts)]
        self.round_index = (self.round_index + 1) % len(available_accounts)

        username = selected.get("username", "unknown")
        logger.info(
            f"🔑 استخدام الحساب: {username} (متاح: {len(available_accounts)}/{len(self.accounts)})"
        )

        return selected

    def mark_used(self, token: str):
        for acc in self.accounts:
            if acc.get("token") == token:
                acc["last_used"] = datetime.now().isoformat()
                acc["use_count"] = acc.get("use_count", 0) + 1
                self.save_accounts()

                username = acc.get("username", "unknown")
                logger.info(f"🔒 الحساب {username} لن يكون متاح لمدة 25 ساعة")
                return

    def stats(self) -> Dict:
        total = len(self.accounts)
        now = datetime.now()
        available = 0
        never_used = 0

        for acc in self.accounts:
            last_used = acc.get("last_used")
            if last_used is None:
                available += 1
                never_used += 1
            else:
                try:
                    last_used_time = datetime.fromisoformat(last_used)
                    hours = (now - last_used_time).total_seconds() / 3600
                    if hours >= TOKEN_COOLDOWN_HOURS:
                        available += 1
                except:
                    pass

        auto_created = sum(1 for a in self.accounts if a.get("auto_created"))

        return {
            "total": total,
            "available": available,
            "on_cooldown": total - available,
            "auto_created": auto_created,
            "never_used": never_used,
        }


# ==============================================================================
# 🚀 معالج الطلبات المحسن مع البروكسيات
# ==============================================================================
class OrderProcessor:
    def __init__(
        self,
        account_manager: AccountManager,
        queue_manager: QueueManager,
        proxy_manager: ProxyManager,
    ):
        self.account_manager = account_manager
        self.queue_manager = queue_manager
        self.proxy_manager = proxy_manager
        self.tiktok_analyzer = TikTokAnalyzer(proxy_manager)
        self.processing_task: Optional[asyncio.Task] = None
        self.proxy_refresh_task: Optional[asyncio.Task] = None
        self._user_messages: Dict[str, Message] = {}
        self._last_updates: Dict[str, str] = {}
        self._update_failures: Dict[str, int] = {}
        self.stats = self._load_stats()
        self.app: Optional[Application] = None

    def _load_stats(self):
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return {
            "total_orders": 0,
            "successful": 0,
            "failed": 0,
            "followers": 0,
            "likes": 0,
            "canceled": 0,
        }

    def _save_stats(self):
        try:
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except:
            pass

    def validate_tiktok_link(self, link: str) -> bool:
        patterns = [
            r"https?://(?:www\.)?tiktok\.com/@[\w\.-]+",
            r"https?://(?:www\.)?tiktok\.com/[\w\.-]+",
            r"https?://vm\.tiktok\.com/[\w]+",
            r"https?://vt\.tiktok\.com/[\w]+",
            r"@[\w\.-]+",
        ]
        return any(re.match(p, link) for p in patterns)

    def place_order_v2(
        self, api_token: str, link: str, service_id: int, quantity: int = 10
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """وضع طلب مع البروكسي - مُصلح"""
        payload = {
            "key": api_token,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity,
        }

        # جرب مع بروكسي أولاً
        proxy = self.proxy_manager.get_best_proxy()

        if proxy:
            logger.info(f"🌐 استخدام بروكسي: {proxy.ip}:{proxy.port}")

            response = self.proxy_manager.use_proxy(
                proxy,
                f"{API_BASE_URL}/v2",
                json=payload,
                method="POST",
                timeout=20,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )

            if response:
                try:
                    data = response.json()
                    if "order" in data:
                        service_name = (
                            "متابعين"
                            if service_id == FOLLOWERS_SERVICE_ID
                            else "لايكات"
                        )
                        logger.info(f"✅ نجح إرسال 10 {service_name} عبر البروكسي!")
                        return True, str(data["order"]), None
                    elif "error" in data:
                        error_msg = str(data.get("error"))
                        logger.error(f"❌ فشل الإرسال: {error_msg}")
                        return False, None, error_msg
                except:
                    pass

        # إذا فشل البروكسي، جرب بدون
        logger.warning("⚠️ محاولة بدون بروكسي...")

        try:
            resp = requests.post(
                f"{API_BASE_URL}/v2",
                json=payload,
                timeout=20,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )

            if resp.status_code == 200:
                data = resp.json()
                if "order" in data:
                    service_name = (
                        "متابعين" if service_id == FOLLOWERS_SERVICE_ID else "لايكات"
                    )
                    logger.info(f"✅ نجح إرسال 10 {service_name}!")
                    return True, str(data["order"]), None
                elif "error" in data:
                    error_msg = str(data.get("error"))
                    logger.error(f"❌ فشل الإرسال: {error_msg}")
                    return False, None, error_msg

        except Exception as e:
            logger.error(f"❌ خطأ في الإرسال: {e}")
            return False, None, f"Exception: {e}"

        # إضافة return في حالة عدم نجاح أي محاولة
        return False, None, "فشلت جميع المحاولات"

    def _create_enhanced_message(
        self,
        order: Dict,
        status: str = "processing",
        account_name: str = None,
        error: str = None,
        service_order_id: str = None,
    ) -> str:
        """إنشاء رسالة محسنة"""
        order_num = order.get("order_number", "N/A")
        link = order.get("link", "")
        service_type = order.get("service_type", "متابعين")
        quantity = order.get("quantity", 0)
        completed = order.get("completed", 0)
        accounts_needed = order.get("accounts_needed", 0)
        initial_followers = order.get("initial_followers")

        username = order.get(
            "username"
        ) or self.tiktok_analyzer.extract_username_from_any_link(link)
        service_emoji = "👥" if service_type == "متابعين" else "❤️"

        if status == "success":
            header = f"✅ **نجح إرسال {service_type}!**"
            emoji = "🎉"
        elif status == "failed":
            header = "❌ **فشل الإرسال**"
            emoji = "😔"
        elif status == "completed":
            header = "🎊 **اكتمل الطلب بنجاح!**"
            emoji = "🏆"
        elif status == "processing":
            header = "🔄 **معالجة الطلب**"
            emoji = "⚡"
        elif status == "waiting":
            header = "⏳ **في الانتظار**"
            emoji = "⏰"
        else:
            header = "📋 **حالة الطلب**"
            emoji = "📊"

        msg = f"{header}\n"
        msg += f"{'─' * 25}\n\n"

        msg += f"{emoji} **معلومات الطلب**\n"
        msg += f"🆔 رقم الطلب: `#{order_num}`\n"
        msg += f"🎯 نوع الخدمة: {service_type} {service_emoji}\n"
        msg += f"👤 الحساب: `@{username}`\n"
        msg += f"🔗 الرابط: {link}\n\n"

        if service_type == "متابعين":
            msg += f"📊 **إحصائيات المتابعين**\n"

            if initial_followers is not None:
                msg += f"📈 المتابعين قبل: **{self.tiktok_analyzer.format_followers(initial_followers)}**\n"
                expected_after = initial_followers + quantity
                msg += f"🎯 المتوقع بعد: **{self.tiktok_analyzer.format_followers(expected_after)}**\n"
            else:
                msg += f"📈 المتابعين قبل: _جاري الفحص..._\n"

            msg += f"➕ سيتم إضافة: **{quantity:,}** متابع\n\n"
        else:
            msg += f"❤️ **معلومات اللايكات**\n"
            msg += f"➕ سيتم إضافة: **{quantity:,}** لايك\n\n"

        msg += f"📈 **التقدم الحالي**\n"
        progress_percent = (
            (completed / accounts_needed * 100) if accounts_needed > 0 else 0
        )
        progress_bar = self._create_progress_bar(progress_percent)
        msg += f"{progress_bar}\n"
        msg += f"🔢 الحسابات: {completed}/{accounts_needed}\n"
        msg += f"{service_emoji} تم إرسال: **{completed * 10:,}/{quantity:,}** {service_type}\n"
        msg += f"📊 النسبة: **{progress_percent:.1f}%**\n\n"

        if status == "processing" and account_name:
            msg += f"🔑 **الحساب المستخدم**: {account_name}\n"

        if status == "completed":
            msg += f"✨ **الطلب مكتمل 100%**\n"
            msg += f"⏱️ يُرجى الانتظار 5-10 دقائق لظهور {service_type}\n"

            if service_type == "متابعين":
                current_followers = self.tiktok_analyzer.get_followers_count(link)
                if current_followers is not None:
                    msg += f"\n📊 **النتيجة النهائية**\n"
                    msg += f"👥 المتابعين الآن: **{self.tiktok_analyzer.format_followers(current_followers)}**\n"
                    if initial_followers is not None:
                        gained = current_followers - initial_followers
                        msg += f"➕ الزيادة الفعلية: **{gained:,}** متابع\n"

        if service_order_id:
            msg += f"\n🆔 Order ID: `{service_order_id}`"

        if error:
            msg += f"\n⚠️ السبب: {error}"

        msg += f"\n\n⏰ آخر تحديث: {datetime.now().strftime('%H:%M:%S')}"

        return msg

    def _create_progress_bar(self, percent: float, length: int = 10) -> str:
        """إنشاء شريط تقدم"""
        filled = int(length * percent / 100)
        empty = length - filled
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percent:.1f}%"

    async def _update_user_message(self, user_id: str, new_text: str):
        """تحديث رسالة العميل بذكاء"""
        try:
            if self._last_updates.get(user_id) == new_text:
                return

            msg = self._user_messages.get(user_id)
            if not msg:
                return

            try:
                await msg.edit_text(new_text, parse_mode=ParseMode.MARKDOWN)
                self._last_updates[user_id] = new_text
                self._update_failures[user_id] = 0
            except Exception as edit_error:
                self._update_failures[user_id] = (
                    self._update_failures.get(user_id, 0) + 1
                )

                if self._update_failures[user_id] >= MAX_UPDATE_ATTEMPTS:
                    try:
                        new_msg = await msg.reply_text(
                            new_text, parse_mode=ParseMode.MARKDOWN
                        )
                        self._user_messages[user_id] = new_msg
                        self._last_updates[user_id] = new_text
                        self._update_failures[user_id] = 0
                    except:
                        pass
        except Exception as e:
            logger.debug(f"خطأ في تحديث رسالة العميل {user_id}: {e}")

    async def _notify_group(self, message: str):
        """إرسال إشعار للجروب"""
        if not GROUP_NOTIFY_ENABLED or not self.app:
            return

        try:
            await self.app.bot.send_message(
                chat_id=GROUP_ID, text=message, parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"❌ فشل إرسال إشعار الجروب: {e}")

    def set_user_message(self, user_id: str, message: Message):
        """تخزين رسالة العميل"""
        self._user_messages[user_id] = message
        self._last_updates[user_id] = ""
        self._update_failures[user_id] = 0

    async def start_proxy_refresh(self):
        """تحديث البروكسيات بشكل دوري"""
        while True:
            try:
                await asyncio.sleep(PROXY_REFRESH_INTERVAL)
                logger.info("🔄 بدء تحديث البروكسيات الدوري...")
                await self.proxy_manager.refresh_proxies()
                logger.info("✅ تم تحديث البروكسيات")
            except Exception as e:
                logger.error(f"❌ خطأ في تحديث البروكسيات: {e}")
                await asyncio.sleep(300)  # انتظر 5 دقائق عند الخطأ

    async def run(self):
        logger.info("🚀 بدء المعالجة التلقائية للطابور...")
        consecutive_failures = 0
        last_update_time = {}

        while True:
            try:
                order = self.queue_manager.get_next_order()

                if not order:
                    await asyncio.sleep(10)
                    continue

                if order.get("status") == "canceled":
                    continue

                user_id = order["user_id"]
                order_num = order.get("order_number", "N/A")
                service_type = order.get("service_type", "متابعين")
                service_id = order.get("service_id", FOLLOWERS_SERVICE_ID)
                link = order.get("link", "")
                quantity = order.get("quantity", 0)

                username = order.get(
                    "username"
                ) or self.tiktok_analyzer.extract_username_from_any_link(link)

                logger.info(
                    f"🔄 معالجة طلب #{order_num} ({service_type}) للعميل {user_id}"
                )

                if order["completed"] == 0:
                    initial_info = ""
                    if service_type == "متابعين":
                        initial_followers = order.get("initial_followers")
                        if initial_followers is not None:
                            initial_info = f"📈 المتابعين الحاليين: {self.tiktok_analyzer.format_followers(initial_followers)}"

                    service_emoji = "👥" if service_type == "متابعين" else "❤️"

                    await self._notify_group(
                        f"🚀 **بدء معالجة طلب جديد**\n"
                        f"📊 رقم الطلب: #{order_num}\n"
                        f"🎯 نوع الخدمة: {service_type} {service_emoji}\n"
                        f"👤 الحساب: @{username}\n"
                        f"🔗 الرابط: {link}\n\n"
                        f"👤 العميل: {user_id}\n"
                        f"{service_emoji} المطلوب: {quantity:,} {service_type}\n"
                        f"📊 يحتاج: {order['accounts_needed']} حساب\n"
                        f"{initial_info}"
                    )

                acc = self.account_manager.get_available_account()

                if not acc:
                    logger.warning("⚠️ لا توجد حسابات متاحة - محاولة إنشاء حساب جديد...")
                    acc = self.account_manager.create_new_account()

                    if not acc:
                        consecutive_failures += 1

                        current_time = time.time()
                        if (
                            current_time - last_update_time.get(user_id, 0)
                            > UPDATE_INTERVAL
                        ):
                            msg = self._create_enhanced_message(order, "waiting")
                            await self._update_user_message(user_id, msg)
                            last_update_time[user_id] = current_time

                        if consecutive_failures >= 5:
                            logger.error(f"❌ فشل 5 محاولات متتالية - انتظار دقيقة")
                            await asyncio.sleep(60)
                            consecutive_failures = 0
                        else:
                            await asyncio.sleep(15)
                        continue

                consecutive_failures = 0

                msg = self._create_enhanced_message(
                    order, "processing", account_name=acc.get("username")
                )
                await self._update_user_message(user_id, msg)

                ok, service_order_id, err = self.place_order_v2(
                    acc["token"], order["link"], service_id, 10
                )

                self.account_manager.mark_used(acc["token"])

                if ok:
                    self.queue_manager.update_order_progress(order["order_id"], True)
                    self.stats["successful"] += 1

                    if service_type == "متابعين":
                        self.stats["followers"] = self.stats.get("followers", 0) + 10
                    else:
                        self.stats["likes"] = self.stats.get("likes", 0) + 10

                    new_order = order.copy()
                    new_order["completed"] = order["completed"] + 1
                    is_completed = (
                        new_order["completed"] >= new_order["accounts_needed"]
                    )

                    if is_completed:
                        status = "completed"
                    else:
                        status = "success"

                    msg = self._create_enhanced_message(
                        new_order, status, service_order_id=service_order_id
                    )
                    await self._update_user_message(user_id, msg)

                    if is_completed:
                        final_info = ""

                        if service_type == "متابعين":
                            await asyncio.sleep(5)
                            current_followers = (
                                self.tiktok_analyzer.get_followers_count(order["link"])
                            )
                            if current_followers is not None:
                                final_info = f"👥 المتابعين الآن: {self.tiktok_analyzer.format_followers(current_followers)}\n"
                                if order.get("initial_followers") is not None:
                                    gained = (
                                        current_followers - order["initial_followers"]
                                    )
                                    final_info += f"➕ الزيادة: {gained:,} متابع\n"

                        service_emoji = "👥" if service_type == "متابعين" else "❤️"

                        await self._notify_group(
                            f"✅ **اكتمل الطلب بنجاح**\n"
                            f"📊 رقم الطلب: #{order_num}\n"
                            f"🎯 نوع الخدمة: {service_type} {service_emoji}\n"
                            f"👤 الحساب: @{username}\n"
                            f"🔗 الرابط: {link}\n\n"
                            f"👤 العميل: {user_id}\n"
                            f"{service_emoji} تم إرسال: {quantity:,} {service_type}\n"
                            f"{final_info}"
                            f"⭐ الطلب مكتمل 100%"
                        )
                else:
                    self.stats["failed"] += 1

                    msg = self._create_enhanced_message(order, "failed", error=err)
                    await self._update_user_message(user_id, msg)

                self.stats["total_orders"] += 1
                self._save_stats()

                wt = rand_wait()
                await asyncio.sleep(wt)

            except Exception as e:
                logger.error(f"❌ خطأ في المعالجة: {e}")
                await asyncio.sleep(5)

    def start(self):
        if not self.processing_task or self.processing_task.done():
            self.processing_task = asyncio.create_task(self.run())

        # بدء تحديث البروكسيات
        if not self.proxy_refresh_task or self.proxy_refresh_task.done():
            self.proxy_refresh_task = asyncio.create_task(self.start_proxy_refresh())

        logger.info("✅ تم تفعيل المعالجة والبروكسيات")


# ==============================================================================
# 🤖 البوت الرئيسي المحسن
# ==============================================================================
class TelegramBot:
    def __init__(self):
        self.proxy_mgr = ProxyManager()
        self.acc_mgr = AccountManager(self.proxy_mgr)
        self.queue_mgr = QueueManager()
        self.proc = OrderProcessor(self.acc_mgr, self.queue_mgr, self.proxy_mgr)
        self.tiktok_analyzer = TikTokAnalyzer(self.proxy_mgr)

    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.proc.start()
        msg = (
            "🔥 **بوت الطابور المصري - النسخة النهائية**\n\n"
            "**✨ الميزات الجديدة:**\n"
            "• 🌐 نظام بروكسيات ذكي متقدم\n"
            "• 🔍 فحص المتابعين قبل وبعد\n"
            "• ❤️ خدمة اللايكات الجديدة\n"
            "• 🚫 إلغاء أي طلب `/cancel`\n"
            "• 📊 إحصائيات مفصلة للطلبات\n"
            "• 🎨 رسائل محسنة بتنسيق احترافي\n"
            "• ⚡ معالجة أسرع وأكثر ذكاءً\n\n"
            "**📋 الأوامر المتاحة:**\n"
            "`/follow [لينك] [عدد]` - طلب متابعين\n"
            "`/like [لينك] [عدد]` - طلب لايكات\n"
            "`/cancel [رقم]` - إلغاء أي طلب\n"
            "`/check [لينك]` - فحص عدد المتابعين\n"
            "`/queue` - حالة الطابور\n"
            "`/stats` - الإحصائيات\n"
            "`/proxy` - حالة البروكسيات\n"
            "`/refresh_proxy` - تحديث البروكسيات (أدمن)\n"
            "`/add_token [توكن]` - إضافة حساب (أدمن)\n\n"
            "🇪🇬 صُنع بكل فخر في مصر\n"
            "👨‍💻 Developer: @zizo0022sasa"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def proxy_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر عرض حالة البروكسيات"""
        stats = self.proxy_mgr.get_statistics()

        msg = f"🌐 **حالة البروكسيات**\n"
        msg += f"{'='*25}\n\n"
        msg += f"📊 **الإحصائيات:**\n"
        msg += f"• إجمالي: {stats['total']}\n"
        msg += f"• شغال: {stats['working']}\n"
        msg += f"• فاشل: {stats['failed']}\n"
        msg += f"• متوسط السرعة: {stats['avg_speed_ms']:.0f}ms\n\n"

        if stats["protocols"]:
            msg += f"**البروتوكولات:**\n"
            for proto, count in stats["protocols"].items():
                msg += f"• {proto}: {count}\n"
            msg += "\n"

        if stats["top_sites"]:
            msg += f"**أفضل المواقع:**\n"
            for site, count in stats["top_sites"][:5]:
                site_name = site.split("/")[-2] if "/" in site else site
                msg += f"• {site_name}: {count} بروكسي\n"

        if stats["total"] == 0:
            msg += "\n⚠️ **لا توجد بروكسيات محملة!**\n"
            msg += "ضع البروكسيات في:\n"
            msg += f"• `{PROXY_FILE}`\n"
            msg += f"• `{PROXY_FILE_JSON}`\n"
            msg += f"• `{PROXY_FILE_TXT}`"

        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def refresh_proxy_cmd(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """أمر تحديث البروكسيات يدوياً"""
        if ADMIN_ID and update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ هذا الأمر للأدمن فقط!")
            return

        msg = await update.message.reply_text("🔄 جاري تحديث البروكسيات...")

        await self.proxy_mgr.refresh_proxies()

        stats = self.proxy_mgr.get_statistics()

        await msg.edit_text(
            f"✅ **تم تحديث البروكسيات!**\n\n"
            f"📊 النتيجة:\n"
            f"• إجمالي: {stats['total']}\n"
            f"• شغال: {stats['working']}\n"
            f"• فاشل: {stats['failed']}",
            parse_mode=ParseMode.MARKDOWN,
        )

    async def cancel_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر إلغاء الطلبات مع تأكيد"""
        user_id = str(update.effective_user.id)

        if not context.args:
            orders = self.queue_mgr.get_user_orders(user_id)

            if not orders:
                await update.message.reply_text(
                    "❌ **لا توجد طلبات نشطة يمكن إلغاؤها!**",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return

            msg = "📋 **طلباتك النشطة:**\n\n"
            for order in orders:
                service_emoji = "👥" if order["service_type"] == "متابعين" else "❤️"
                completed_amount = order["completed"] * 10
                progress_percent = (
                    (order["completed"] / order["accounts_needed"] * 100)
                    if order["accounts_needed"] > 0
                    else 0
                )

                msg += (
                    f"• **الطلب #{order['order_number']}**\n"
                    f"  النوع: {order['service_type']} {service_emoji}\n"
                    f"  الكمية: {order['quantity']:,}\n"
                    f"  تم إرسال: {completed_amount:,}\n"
                    f"  التقدم: {progress_percent:.1f}%\n"
                    f"  الرابط: {order['link']}\n\n"
                )

            msg += "**للإلغاء استخدم:**\n"
            msg += "`/cancel [رقم_الطلب]`\n\n"
            msg += "مثال: `/cancel 5`\n\n"
            msg += "⚠️ **ملاحظة:** يمكن إلغاء أي طلب في أي وقت!"

            await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            return

        try:
            order_number = int(context.args[0])
        except ValueError:
            await update.message.reply_text(
                "❌ رقم الطلب يجب أن يكون رقم صحيح!", parse_mode=ParseMode.MARKDOWN
            )
            return

        orders = self.queue_mgr.get_user_orders(user_id)
        order_found = None
        for order in orders:
            if order.get("order_number") == order_number:
                order_found = order
                break

        if not order_found:
            await update.message.reply_text(
                f"❌ **لم يتم العثور على الطلب #{order_number}**\n"
                f"أو أن الطلب مكتمل بالفعل",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ نعم، ألغي الطلب", callback_data=f"cancel_yes_{order_number}"
                ),
                InlineKeyboardButton(
                    "❌ لا، احتفظ بالطلب", callback_data=f"cancel_no_{order_number}"
                ),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        service_type = order_found.get("service_type", "متابعين")
        quantity = order_found.get("quantity", 0)
        completed_amount = order_found["completed"] * 10

        confirm_msg = f"⚠️ **تأكيد إلغاء الطلب**\n\n"
        confirm_msg += f"هل أنت متأكد من إلغاء:\n"
        confirm_msg += f"• **الطلب #{order_number}**\n"
        confirm_msg += f"• النوع: {service_type}\n"
        confirm_msg += f"• الكمية المطلوبة: {quantity:,}\n"

        if completed_amount > 0:
            confirm_msg += f"• تم إرسال: **{completed_amount:,}** {service_type}\n"
            confirm_msg += (
                f"• سيتم إلغاء: **{quantity - completed_amount:,}** {service_type}\n"
            )

        confirm_msg += f"\n⚠️ لا يمكن التراجع عن هذا الإجراء!"

        await update.message.reply_text(
            confirm_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )

    async def handle_cancel_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """معالج أزرار التأكيد للإلغاء"""
        query = update.callback_query
        await query.answer()

        user_id = str(query.from_user.id)
        data = query.data

        if data.startswith("cancel_yes_"):
            order_number = int(data.replace("cancel_yes_", ""))
            success, message = self.queue_mgr.cancel_order(user_id, order_number)

            if success:
                self.proc.stats["canceled"] = self.proc.stats.get("canceled", 0) + 1
                self.proc._save_stats()

                if GROUP_NOTIFY_ENABLED:
                    try:
                        await context.bot.send_message(
                            chat_id=GROUP_ID,
                            text=(
                                f"🚫 **طلب ملغي**\n"
                                f"العميل: {user_id}\n"
                                f"رقم الطلب: #{order_number}"
                            ),
                            parse_mode=ParseMode.MARKDOWN,
                        )
                    except:
                        pass

            await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)

        elif data.startswith("cancel_no_"):
            order_number = int(data.replace("cancel_no_", ""))
            await query.edit_message_text(
                f"✅ **تم الاحتفاظ بالطلب #{order_number}**\n"
                f"سيستمر تنفيذ طلبك بشكل طبيعي.",
                parse_mode=ParseMode.MARKDOWN,
            )

    async def follow_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر طلب المتابعين"""
        await self._process_service_request(
            update, context, service_type="متابعين", service_id=FOLLOWERS_SERVICE_ID
        )

    async def like_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر طلب اللايكات"""
        await self._process_service_request(
            update, context, service_type="لايكات", service_id=LIKES_SERVICE_ID
        )

    async def _process_service_request(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        service_type: str,
        service_id: int,
    ):
        """معالجة طلب خدمة"""
        if not context.args or len(context.args) < 2:
            command = "follow" if service_type == "متابعين" else "like"
            await update.message.reply_text(
                f"❌ الصيغة الصحيحة:\n`/{command} [لينك] [عدد]`\n\n"
                f"مثال:\n`/{command} @username 50`",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        link = context.args[0]
        try:
            qty = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ العدد يجب أن يكون رقم صحيح!")
            return

        if qty <= 0:
            await update.message.reply_text("❌ العدد يجب أن يكون أكبر من صفر!")
            return

        if qty > 10000:
            await update.message.reply_text(
                f"❌ الحد الأقصى 10,000 {service_type} للطلب الواحد!"
            )
            return

        if not self.proc.validate_tiktok_link(link):
            await update.message.reply_text(
                "❌ رابط TikTok غير صحيح!\n\n"
                "الصيغ المقبولة:\n"
                "• `@username`\n"
                "• `https://tiktok.com/@username`\n"
                "• رابط مختصر",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        initial_followers = None
        if service_type == "متابعين":
            checking_msg = await update.message.reply_text(
                "🔍 **جاري فحص الحساب...**\n" "⏳ يرجى الانتظار قليلاً...",
                parse_mode=ParseMode.MARKDOWN,
            )
            initial_followers = self.tiktok_analyzer.get_followers_count(link)
        else:
            checking_msg = await update.message.reply_text(
                "🔄 **جاري تجهيز طلبك...**", parse_mode=ParseMode.MARKDOWN
            )

        username = self.tiktok_analyzer.extract_username_from_any_link(link)

        user_id = str(update.effective_user.id)
        order_id, order_num = self.queue_mgr.add_order(
            user_id, link, qty, initial_followers, service_type, service_id, username
        )
        accounts_needed = (qty // 10) + (1 if qty % 10 > 0 else 0)

        service_emoji = "👥" if service_type == "متابعين" else "❤️"

        msg = f"✅ **تم إضافة طلبك بنجاح!**\n"
        msg += f"{'─' * 25}\n\n"

        msg += f"📋 **تفاصيل الطلب**\n"
        msg += f"🆔 رقم الطلب: `#{order_num}`\n"
        msg += f"🎯 نوع الخدمة: {service_type} {service_emoji}\n"
        msg += f"👤 الحساب: `@{username}`\n"
        msg += f"🔗 الرابط: {link}\n\n"

        if service_type == "متابعين":
            msg += f"📊 **معلومات المتابعين**\n"
            if initial_followers is not None:
                msg += f"📈 المتابعين الحاليين: **{self.tiktok_analyzer.format_followers(initial_followers)}**\n"
                expected = initial_followers + qty
                msg += f"🎯 المتوقع بعد الإنجاز: **{self.tiktok_analyzer.format_followers(expected)}**\n"
            else:
                msg += f"📈 المتابعين الحاليين: _غير متاح_\n"
            msg += f"➕ سيتم إضافة: **{qty:,}** متابع\n\n"
        else:
            msg += f"❤️ **معلومات اللايكات**\n"
            msg += f"➕ سيتم إضافة: **{qty:,}** لايك\n\n"

        msg += f"⚙️ **معلومات المعالجة**\n"
        msg += f"📦 الحسابات المطلوبة: {accounts_needed}\n"
        msg += f"⏱️ الوقت المتوقع: ~{accounts_needed * 10} ثانية\n\n"

        msg += f"🚀 **المعالجة تبدأ تلقائياً**\n"
        msg += f"📌 سيتم تحديث هذه الرسالة بالتقدم المباشر\n\n"
        msg += f"💡 **تلميح:** يمكنك إلغاء الطلب في أي وقت:\n"
        msg += f"`/cancel {order_num}`"

        await checking_msg.delete()
        sent_msg = await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

        self.proc.set_user_message(user_id, sent_msg)
        self.proc.start()

    async def check_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر فحص المتابعين"""
        if not context.args:
            await update.message.reply_text(
                "❌ الصيغة الصحيحة:\n`/check [لينك]`\n\n" "مثال:\n`/check @username`",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        link = context.args[0]

        if not self.proc.validate_tiktok_link(link):
            await update.message.reply_text(
                "❌ رابط TikTok غير صحيح!", parse_mode=ParseMode.MARKDOWN
            )
            return

        checking_msg = await update.message.reply_text(
            "🔍 **جاري فحص الحساب...**\n" "⏳ يرجى الانتظار...",
            parse_mode=ParseMode.MARKDOWN,
        )

        followers = self.tiktok_analyzer.get_followers_count(link)
        username = self.tiktok_analyzer.extract_username_from_any_link(link)

        if followers is not None:
            msg = f"✅ **نتيجة الفحص**\n\n"
            msg += f"👤 الحساب: `@{username}`\n"
            msg += f"👥 عدد المتابعين: **{self.tiktok_analyzer.format_followers(followers)}**\n"
            msg += f"🔗 الرابط: {link}"
        else:
            msg = f"❌ **فشل الفحص**\n\n"
            msg += f"لم نتمكن من فحص الحساب\n"
            msg += f"الأسباب المحتملة:\n"
            msg += f"• الحساب خاص\n"
            msg += f"• الرابط غير صحيح\n"
            msg += f"• مشكلة في الاتصال"

        await checking_msg.edit_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def queue_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            self.queue_mgr.status_markdown(), parse_mode=ParseMode.MARKDOWN
        )

    async def add_token_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if ADMIN_ID and update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ هذا الأمر للأدمن فقط!")
            return

        if not context.args:
            await update.message.reply_text(
                "📝 **طريقة إضافة حساب:**\n\n"
                "**صيغة JSON:**\n"
                '`/add_token {"token":"TOKEN","username":"user","password":"pass"}`\n\n'
                "**أو توكن فقط:**\n"
                "`/add_token TOKEN`",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        data = " ".join(context.args)
        res = self.acc_mgr.add_account(data)
        await update.message.reply_text(res)

    async def stats_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        a = self.acc_mgr.stats()
        s = self.proc.stats
        proxy_stats = self.proxy_mgr.get_statistics()

        success_rate = 0
        if s["total_orders"] > 0:
            success_rate = (s["successful"] / s["total_orders"]) * 100

        now = datetime.now()
        next_available = None
        for acc in self.acc_mgr.accounts:
            if acc.get("last_used"):
                try:
                    last = datetime.fromisoformat(acc["last_used"])
                    available_at = last + timedelta(hours=TOKEN_COOLDOWN_HOURS)
                    if available_at > now and (
                        not next_available or available_at < next_available
                    ):
                        next_available = available_at
                except:
                    pass

        time_to_next = ""
        if next_available:
            delta = next_available - now
            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            time_to_next = f"\n⏰ الحساب التالي بعد: {hours}س {minutes}د"

        total_followers = s.get("followers", 0)
        total_likes = s.get("likes", 0)
        total_canceled = s.get("canceled", 0)

        msg = (
            f"📊 **الإحصائيات الكاملة**\n"
            f"{'='*25}\n\n"
            f"**👤 الحسابات ({a['total']} حساب):**\n"
            f"✅ متاح الآن: {a['available']}\n"
            f"⏳ في الانتظار: {a['on_cooldown']}\n"
            f"🆕 لم تُستخدم: {a.get('never_used', 0)}\n"
            f"🤖 مُنشأة تلقائياً: {a['auto_created']}{time_to_next}\n\n"
            f"**📦 الطلبات ({s['total_orders']} طلب):**\n"
            f"✅ ناجح: {s['successful']}\n"
            f"❌ فاشل: {s['failed']}\n"
            f"🚫 ملغي: {total_canceled}\n"
            f"📈 معدل النجاح: {success_rate:.1f}%\n\n"
            f"**🎯 الخدمات المُرسلة:**\n"
            f"👥 متابعين: {total_followers:,}\n"
            f"❤️ لايكات: {total_likes:,}\n\n"
            f"**🌐 البروكسيات:**\n"
            f"• إجمالي: {proxy_stats['total']}\n"
            f"• شغالة: {proxy_stats['working']}\n"
            f"• فاشلة: {proxy_stats['failed']}\n"
            f"• متوسط السرعة: {proxy_stats['avg_speed_ms']:.0f}ms\n\n"
            f"{self.queue_mgr.status_markdown()}"
        )
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    async def run(self):
        if not TELEGRAM_BOT_TOKEN:
            logger.error("❌ توكن البوت غير موجود!")
            return

        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        self.proc.app = app

        app.add_handler(CommandHandler("start", self.start_cmd))
        app.add_handler(CommandHandler("follow", self.follow_cmd))
        app.add_handler(CommandHandler("like", self.like_cmd))
        app.add_handler(CommandHandler("cancel", self.cancel_cmd))
        app.add_handler(CommandHandler("check", self.check_cmd))
        app.add_handler(CommandHandler("queue", self.queue_cmd))
        app.add_handler(CommandHandler("add_token", self.add_token_cmd))
        app.add_handler(CommandHandler("stats", self.stats_cmd))
        app.add_handler(CommandHandler("proxy", self.proxy_cmd))
        app.add_handler(CommandHandler("refresh_proxy", self.refresh_proxy_cmd))

        app.add_handler(
            CallbackQueryHandler(self.handle_cancel_callback, pattern="^cancel_")
        )

        async def after_start(_):
            self.proc.start()

            # اختبار البروكسيات عند البدء
            if PROXY_TEST_ON_START and len(self.proxy_mgr.proxies) > 0:
                logger.info("🔍 اختبار البروكسيات عند البدء...")
                # اختبر عينة من البروكسيات
                sample_size = min(20, len(self.proxy_mgr.proxies))
                sample_proxies = random.sample(self.proxy_mgr.proxies, sample_size)

                for proxy in sample_proxies:
                    await self.proxy_mgr.test_proxy(proxy)

                self.proxy_mgr.working_proxies = [
                    p for p in self.proxy_mgr.proxies if p.working
                ]
                self.proxy_mgr.save_proxies()

                logger.info(
                    f"✅ اختبار البروكسيات اكتمل: {len(self.proxy_mgr.working_proxies)} شغال"
                )

        app.post_init = after_start

        logger.info("=" * 60)
        logger.info("✅ البوت جاهز للعمل!")
        logger.info(f"🤖 Token: {TELEGRAM_BOT_TOKEN[:20]}...")
        logger.info(f"👑 Admin: {ADMIN_ID}")
        logger.info(f"📢 Group: {GROUP_ID}")
        logger.info("✨ النسخة: النهائية مع البروكسيات المدمجة")
        logger.info("👥 خدمة المتابعين: Service ID 196")
        logger.info("❤️ خدمة اللايكات: Service ID 188")
        logger.info(f"🌐 البروكسيات: {len(self.proxy_mgr.proxies)} محملة")
        logger.info("🚫 أمر الإلغاء: /cancel لأي طلب")
        logger.info("🔍 TikTok Analyzer: مفعل مع البروكسيات")
        logger.info("📝 JSON Format: سطر واحد لكل حساب")
        logger.info("📟 Logging: Terminal Only (No Files)")
        logger.info("=" * 60)

        await app.run_polling(allowed_updates=Update.ALL_TYPES)


# ==============================================================================
# 🚀 نقطة البداية
# ==============================================================================
async def main():
    print("\n" + "=" * 70)
    print("🔥 بوت الطابور المصري - النسخة النهائية الكاملة")
    print("✨ نظام البروكسيات المدمج بالكامل")
    print("👥 Service ID 196: متابعين")
    print("❤️ Service ID 188: لايكات")
    print("🌐 البروكسيات: working_proxies_freefollower.json")
    print("🚫 أمر الإلغاء: /cancel لأي طلب")
    print("📝 JSON Format: سطر واحد لكل حساب")
    print("📟 Logging: Terminal Only")
    print("👨‍💻 Developer: @zizo0022sasa")
    print("🇪🇬 Made with ❤️ in Egypt")
    print("=" * 70 + "\n")

    bot = TelegramBot()
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 تم إيقاف البوت بنجاح")
