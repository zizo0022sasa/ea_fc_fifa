#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 مدير البروكسيات الذكي المحسّن - النسخة النهائية
✅ يجلب آلاف البروكسيات الشغالة
🚀 اختبار سريع ودقيق
"""

import asyncio
import json
import logging
import os
import random
import socket
import struct
import threading
import time
import warnings
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Union

import aiohttp
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# تعطيل تحذيرات SSL
warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class ProxyData:
    """بيانات البروكسي"""

    ip: str
    port: int
    protocol: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    speed_ms: Optional[int] = None
    last_checked: Optional[str] = None
    working_sites: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    fail_count: int = 0
    success_count: int = 0
    is_elite: bool = False
    anonymity: str = "unknown"

    def to_url(self) -> str:
        """تحويل لصيغة URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.ip}:{self.port}"
        return f"{self.protocol}://{self.ip}:{self.port}"

    def to_dict(self) -> dict:
        """تحويل لـ dictionary"""
        return asdict(self)

    @classmethod
    def from_string(
        cls, proxy_str: str, default_protocol: str = "http"
    ) -> Optional["ProxyData"]:
        """إنشاء من نص"""
        try:
            proxy_str = proxy_str.strip()

            if not proxy_str or proxy_str.startswith("#"):
                return None

            # إزالة البروتوكول إذا موجود
            if "://" in proxy_str:
                parts = proxy_str.split("://", 1)
                protocol = parts[0].lower()
                proxy_str = parts[1]
            else:
                protocol = default_protocol

            # معالجة المصادقة
            if "@" in proxy_str:
                auth_host = proxy_str.split("@", 1)
                auth_parts = auth_host[0].split(":", 1)
                host_parts = auth_host[1].split(":", 1)

                if len(host_parts) == 2:
                    return cls(
                        ip=host_parts[0],
                        port=int(host_parts[1]),
                        protocol=protocol,
                        username=auth_parts[0] if auth_parts else None,
                        password=auth_parts[1] if len(auth_parts) > 1 else None,
                    )
            else:
                # IP:Port فقط
                parts = proxy_str.split(":", 1)
                if len(parts) == 2 and parts[1].isdigit():
                    return cls(ip=parts[0], port=int(parts[1]), protocol=protocol)

        except (ValueError, IndexError):
            pass

        return None


class ProxyManager:
    """مدير البروكسيات الذكي"""

    def __init__(
        self,
        proxy_file: str = "working_proxies.json",
        sources_file: str = "proxy_sources.json",
        failed_file: str = "failed_proxies.json",
        auto_clean: bool = True,
        auto_create_files: bool = True,
    ):
        self.proxy_file = proxy_file
        self.sources_file = sources_file
        self.failed_file = failed_file
        self.auto_clean = auto_clean
        self.proxies: List[ProxyData] = []
        self.failed_proxies: Set[str] = set()
        self.lock = threading.Lock()

        # قائمة مواقع الاختبار
        self.test_sites = {
            # مواقع سريعة للاختبار
            "httpbin": "http://httpbin.org/ip",
            "ipify": "https://api.ipify.org/",
            "google": "http://www.google.com/generate_204",
            "cloudflare": "https://www.cloudflare.com/cdn-cgi/trace",
            # المواقع المستهدفة
            "freefollower": "https://freefollower.net/",
            "instagram": "https://www.instagram.com/",
            "facebook": "https://www.facebook.com/",
            "twitter": "https://twitter.com/",
            "tiktok": "https://www.tiktok.com/",
            "youtube": "https://www.youtube.com/",
        }

        # مصادر البروكسيات الموسعة
        self.proxy_sources = [
            # APIs موثوقة
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all&simplified=true",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all&simplified=true",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all&simplified=true",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://www.proxy-list.download/api/v1/get?type=https",
            "https://www.proxy-list.download/api/v1/get?type=socks4",
            "https://www.proxy-list.download/api/v1/get?type=socks5",
            # GitHub مصادر
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
            "https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt",
            "https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/socks4.txt",
            "https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/socks5.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt",
            "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt",
            "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt",
            # مصادر إضافية
            "https://api.openproxylist.xyz/http.txt",
            "https://api.openproxylist.xyz/socks4.txt",
            "https://api.openproxylist.xyz/socks5.txt",
            "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt",
            "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks4.txt",
            "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/socks5.txt",
            "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
            "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt",
            "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
            "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt",
            "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks4.txt",
            "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt",
            # Spys.me
            "https://spys.me/proxy.txt",
            # ProxyScan
            "https://www.proxyscan.io/download?type=http",
            "https://www.proxyscan.io/download?type=socks4",
            "https://www.proxyscan.io/download?type=socks5",
            # مصادر سريعة
            "https://www.proxy-list.download/api/v1/get?type=http&anon=elite",
            "https://www.proxy-list.download/api/v1/get?type=http&anon=anonymous",
            "https://www.proxy-list.download/api/v1/get?type=http&anon=transparent",
            # APIs بديلة
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps",
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks4",
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=socks5",
        ]

        # إنشاء الملفات إذا لم تكن موجودة
        if auto_create_files:
            self._create_default_files()

        # تحميل البيانات
        self.load_proxies()
        self.load_failed_proxies()
        self.load_sources()

    def _create_default_files(self):
        """إنشاء الملفات الافتراضية"""

        # ملف البروكسيات
        if not os.path.exists(self.proxy_file):
            with open(self.proxy_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            logger.info(f"✅ تم إنشاء ملف: {self.proxy_file}")

        # ملف المصادر
        if not os.path.exists(self.sources_file):
            data = {
                "sources": self.proxy_sources,
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.sources_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ تم إنشاء ملف: {self.sources_file}")

        # ملف البروكسيات الفاشلة
        if not os.path.exists(self.failed_file):
            data = {"failed": [], "last_updated": datetime.now().isoformat()}
            with open(self.failed_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ تم إنشاء ملف: {self.failed_file}")

    def load_proxies(self):
        """تحميل البروكسيات"""
        try:
            if os.path.exists(self.proxy_file):
                with open(self.proxy_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.proxies = []
                    for p in data:
                        try:
                            proxy = ProxyData(**p)
                            self.proxies.append(proxy)
                        except:
                            pass
                    logger.info(f"✅ تم تحميل {len(self.proxies)} بروكسي")
            else:
                self.proxies = []
        except:
            self.proxies = []

    def load_failed_proxies(self):
        """تحميل البروكسيات الفاشلة"""
        try:
            if os.path.exists(self.failed_file):
                with open(self.failed_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.failed_proxies = set(data.get("failed", []))
                    else:
                        self.failed_proxies = set(data)
                    logger.info(f"📋 تم تحميل {len(self.failed_proxies)} بروكسي فاشل")
        except:
            self.failed_proxies = set()

    def load_sources(self):
        """تحميل المصادر"""
        try:
            if os.path.exists(self.sources_file):
                with open(self.sources_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        sources = data.get("sources", self.proxy_sources)
                    else:
                        sources = data

                    # دمج المصادر الجديدة مع الموجودة
                    all_sources = set(sources) | set(self.proxy_sources)
                    self.proxy_sources = list(all_sources)

                    logger.info(f"📚 تم تحميل {len(self.proxy_sources)} مصدر")
        except:
            pass

    def save_proxies(self):
        """حفظ البروكسيات"""
        try:
            with self.lock:
                # فلترة وترتيب
                working = [
                    p for p in self.proxies if p.to_url() not in self.failed_proxies
                ]
                working.sort(key=lambda p: (-p.success_rate, p.speed_ms or 99999))

                data = [p.to_dict() for p in working]

                with open(self.proxy_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                logger.info(f"💾 تم حفظ {len(working)} بروكسي شغال")

                # حفظ الفاشلة
                self.save_failed_proxies()
        except Exception as e:
            logger.error(f"خطأ في الحفظ: {e}")

    def save_failed_proxies(self):
        """حفظ البروكسيات الفاشلة"""
        try:
            data = {
                "failed": list(self.failed_proxies)[:5000],  # حد أقصى 5000
                "last_updated": datetime.now().isoformat(),
                "count": len(self.failed_proxies),
            }

            with open(self.failed_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

    async def fetch_proxies_from_source(
        self, session: aiohttp.ClientSession, url: str
    ) -> List[str]:
        """جلب بروكسيات من مصدر"""
        proxies = []

        try:
            timeout = aiohttp.ClientTimeout(total=20)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }

            async with session.get(
                url, timeout=timeout, headers=headers, ssl=False
            ) as response:
                if response.status == 200:
                    text = await response.text()

                    # معالجة JSON
                    if "json" in response.headers.get("content-type", ""):
                        try:
                            data = json.loads(text)

                            # Geonode API
                            if isinstance(data, dict) and "data" in data:
                                for item in data["data"]:
                                    if isinstance(item, dict):
                                        ip = item.get("ip")
                                        port = item.get("port")
                                        if ip and port:
                                            proxies.append(f"{ip}:{port}")

                            # قائمة مباشرة
                            elif isinstance(data, list):
                                for item in data:
                                    if isinstance(item, str) and ":" in item:
                                        proxies.append(item)
                                    elif isinstance(item, dict):
                                        ip = item.get("ip") or item.get("host")
                                        port = item.get("port")
                                        if ip and port:
                                            proxies.append(f"{ip}:{port}")
                        except:
                            pass

                    # معالجة نص
                    if not proxies:
                        lines = text.split("\n")
                        for line in lines[:10000]:  # حد أقصى 10000 سطر
                            line = line.strip()

                            # تجاهل التعليقات والأسطر الفارغة
                            if (
                                not line
                                or line.startswith("#")
                                or line.startswith("//")
                            ):
                                continue

                            # استخراج IP:Port
                            # بعض الملفات تحتوي على معلومات إضافية
                            parts = line.split()
                            if parts:
                                proxy = parts[0]

                                # تحقق من الصيغة الأساسية
                                if ":" in proxy and proxy.count(":") <= 2:
                                    # تنظيف
                                    proxy = proxy.replace("http://", "").replace(
                                        "https://", ""
                                    )
                                    proxy = proxy.replace("socks4://", "").replace(
                                        "socks5://", ""
                                    )

                                    # تحقق من IP:Port
                                    try:
                                        ip_port = (
                                            proxy.split("@")[-1]
                                            if "@" in proxy
                                            else proxy
                                        )
                                        ip, port = ip_port.rsplit(":", 1)

                                        # تحقق من صحة المنفذ
                                        port_num = int(port)
                                        if 1 <= port_num <= 65535:
                                            proxies.append(proxy)
                                    except:
                                        continue

                    logger.debug(f"✓ جلب {len(proxies)} من {url.split('/')[2]}")

        except asyncio.TimeoutError:
            logger.debug(f"⏱ انتهت مهلة: {url.split('/')[2]}")
        except Exception as e:
            logger.debug(f"✗ فشل {url.split('/')[2]}: {type(e).__name__}")

        return proxies

    async def collect_proxies(self, max_per_source: int = 2000) -> List[ProxyData]:
        """جمع البروكسيات من جميع المصادر"""
        logger.info("🔄 جمع البروكسيات من المصادر...")

        all_proxies = {}

        # إعدادات الاتصال
        connector = aiohttp.TCPConnector(
            limit=50, limit_per_host=10, ttl_dns_cache=300, enable_cleanup_closed=True
        )

        async with aiohttp.ClientSession(connector=connector) as session:
            # جمع من جميع المصادر
            tasks = []
            for url in self.proxy_sources:
                task = self.fetch_proxies_from_source(session, url)
                tasks.append(task)

            # انتظار النتائج
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # معالجة النتائج
            for i, result in enumerate(results):
                if isinstance(result, list) and result:
                    source_url = self.proxy_sources[i].lower()

                    # تحديد البروتوكول الافتراضي
                    if "socks4" in source_url:
                        protocol = "socks4"
                    elif "socks5" in source_url:
                        protocol = "socks5"
                    elif "https" in source_url and "http.txt" not in source_url:
                        protocol = "https"
                    else:
                        protocol = "http"

                    # إضافة البروكسيات
                    count = 0
                    for proxy_str in result:
                        if count >= max_per_source:
                            break

                        # إنشاء كائن البروكسي
                        proxy = ProxyData.from_string(proxy_str, protocol)
                        if proxy:
                            key = f"{proxy.ip}:{proxy.port}"

                            # تجنب التكرار والفاشلة
                            if (
                                key not in all_proxies
                                and proxy.to_url() not in self.failed_proxies
                            ):
                                all_proxies[key] = proxy
                                count += 1

        proxy_list = list(all_proxies.values())

        # خلط عشوائي للعدالة في الاختبار
        random.shuffle(proxy_list)

        logger.info(f"✅ تم جمع {len(proxy_list)} بروكسي فريد")
        return proxy_list

    def quick_test_proxy(self, proxy: ProxyData, timeout: int = 5) -> bool:
        """اختبار سريع للبروكسي باستخدام socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((proxy.ip, proxy.port))
            sock.close()
            return result == 0
        except:
            return False

    async def test_proxy_http(
        self, proxy: ProxyData, test_url: str, timeout: int = 15
    ) -> bool:
        """اختبار HTTP/HTTPS"""
        proxy_url = proxy.to_url()

        try:
            connector = aiohttp.TCPConnector(ssl=False, force_close=True)
            timeout_obj = aiohttp.ClientTimeout(total=timeout)

            async with aiohttp.ClientSession(
                connector=connector, timeout=timeout_obj
            ) as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                }

                start_time = time.time()

                async with session.get(
                    test_url,
                    proxy=proxy_url,
                    headers=headers,
                    allow_redirects=False,
                    ssl=False,
                ) as response:
                    elapsed = int((time.time() - start_time) * 1000)

                    # قبول أكواد استجابة متعددة
                    if response.status in [
                        200,
                        201,
                        202,
                        204,
                        301,
                        302,
                        303,
                        304,
                        307,
                        308,
                        400,
                        403,
                        404,
                        405,
                    ]:
                        proxy.speed_ms = elapsed
                        proxy.last_checked = datetime.now().isoformat()
                        proxy.success_count += 1

                        # تحديد مستوى الإخفاء
                        if response.status == 200:
                            try:
                                text = await response.text()
                                if proxy.ip not in text:
                                    proxy.is_elite = True
                                    proxy.anonymity = "elite"
                                else:
                                    proxy.anonymity = "transparent"
                            except:
                                proxy.anonymity = "anonymous"

                        return True

        except asyncio.TimeoutError:
            proxy.fail_count += 1
        except:
            proxy.fail_count += 1

        return False

    def test_proxy_socks(
        self, proxy: ProxyData, test_url: str, timeout: int = 15
    ) -> bool:
        """اختبار SOCKS4/SOCKS5"""
        proxy_url = proxy.to_url()

        try:
            # يحتاج: pip install requests[socks] أو pip install pysocks
            proxies = {"http": proxy_url, "https": proxy_url}

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            start_time = time.time()

            response = requests.get(
                test_url,
                proxies=proxies,
                headers=headers,
                timeout=timeout,
                verify=False,
                allow_redirects=False,
            )

            elapsed = int((time.time() - start_time) * 1000)

            if response.status_code in [
                200,
                201,
                202,
                204,
                301,
                302,
                303,
                304,
                307,
                308,
                400,
                403,
                404,
                405,
            ]:
                proxy.speed_ms = elapsed
                proxy.last_checked = datetime.now().isoformat()
                proxy.success_count += 1
                return True

        except:
            proxy.fail_count += 1

        return False

    async def test_proxy(
        self, proxy: ProxyData, test_url: str = None, timeout: int = 15
    ) -> bool:
        """اختبار البروكسي"""
        if test_url is None:
            # استخدام موقع سريع للاختبار
            test_url = "http://httpbin.org/ip"

        # تجنب إعادة اختبار الفاشلة
        if proxy.to_url() in self.failed_proxies:
            return False

        # اختبار سريع بـ socket أولاً
        if not self.quick_test_proxy(proxy, timeout=3):
            return False

        # اختبار حسب البروتوكول
        if proxy.protocol in ["http", "https"]:
            result = await self.test_proxy_http(proxy, test_url, timeout)
        else:
            # SOCKS يحتاج معالجة خاصة
            result = self.test_proxy_socks(proxy, test_url, timeout)

        if result:
            # إضافة الموقع للقائمة
            site_name = test_url.split("/")[2] if "//" in test_url else test_url
            if site_name not in proxy.working_sites:
                proxy.working_sites.append(site_name)

        return result

    async def test_all_proxies(
        self,
        proxies: List[ProxyData] = None,
        max_workers: int = 100,
        quick_mode: bool = True,
    ) -> List[ProxyData]:
        """اختبار جميع البروكسيات"""
        if proxies is None:
            proxies = self.proxies

        if not proxies:
            logger.warning("⚠️ لا توجد بروكسيات للاختبار")
            return []

        logger.info(f"🔬 اختبار {len(proxies)} بروكسي...")

        working_proxies = []
        failed_count = 0

        # موقع الاختبار
        if quick_mode:
            test_url = "http://httpbin.org/ip"  # موقع سريع جداً
        else:
            test_url = self.test_sites.get("freefollower", "https://www.google.com/")

        # اختبار سريع أولي بـ socket
        logger.info("⚡ فحص سريع للمنافذ المفتوحة...")
        reachable_proxies = []

        for proxy in proxies:
            if self.quick_test_proxy(proxy, timeout=2):
                reachable_proxies.append(proxy)

        logger.info(f"📡 {len(reachable_proxies)} منفذ مفتوح من {len(proxies)}")

        if not reachable_proxies:
            logger.warning("⚠️ لا توجد منافذ مفتوحة!")
            return []

        # اختبار HTTP الفعلي
        semaphore = asyncio.Semaphore(max_workers)

        async def test_with_semaphore(proxy):
            async with semaphore:
                try:
                    if await self.test_proxy(proxy, test_url, timeout=10):
                        return proxy
                except:
                    pass
                return None

        # معالجة على دفعات
        batch_size = 200
        total_tested = 0

        for i in range(0, len(reachable_proxies), batch_size):
            batch = reachable_proxies[i : i + batch_size]
            tasks = [test_with_semaphore(proxy) for proxy in batch]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if result and not isinstance(result, Exception):
                    working_proxies.append(result)
                else:
                    failed_count += 1

            total_tested = min(i + batch_size, len(reachable_proxies))
            success_rate = (
                (len(working_proxies) / total_tested * 100) if total_tested > 0 else 0
            )

            logger.info(
                f"📊 التقدم: {total_tested}/{len(reachable_proxies)} | "
                f"✅ شغال: {len(working_proxies)} | "
                f"❌ فاشل: {failed_count} | "
                f"📈 معدل النجاح: {success_rate:.1f}%"
            )

            # إذا وجدنا عدد كافي، نكتفي
            if quick_mode and len(working_proxies) >= 100:
                logger.info("✨ تم العثور على عدد كافي من البروكسيات")
                break

        # اختبار على المواقع المستهدفة
        if working_proxies and not quick_mode:
            logger.info("🎯 اختبار على المواقع المستهدفة...")

            # اختبار عينة صغيرة
            sample_size = min(50, len(working_proxies))
            sample = random.sample(working_proxies, sample_size)

            for site_name, site_url in [("freefollower", "https://freefollower.net/")]:
                logger.info(f"🔍 اختبار {sample_size} بروكسي على {site_name}...")

                tasks = [
                    self.test_proxy(proxy, site_url, timeout=15) for proxy in sample
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                success = sum(1 for r in results if r and not isinstance(r, Exception))
                logger.info(f"✓ {success}/{sample_size} يعمل على {site_name}")

        # حساب معدل النجاح النهائي
        for proxy in working_proxies:
            total = proxy.success_count + proxy.fail_count
            if total > 0:
                proxy.success_rate = (proxy.success_count / total) * 100

        # ترتيب حسب الجودة
        working_proxies.sort(
            key=lambda p: (
                -p.success_rate,
                -p.is_elite,
                p.speed_ms or 99999,
                -len(p.working_sites),
            )
        )

        logger.info(f"🎉 النتيجة النهائية: {len(working_proxies)} بروكسي شغال!")

        return working_proxies

    def mark_proxy_failed(self, proxy_url: str):
        """وضع علامة فشل على بروكسي"""
        with self.lock:
            self.failed_proxies.add(proxy_url)
            self.proxies = [p for p in self.proxies if p.to_url() != proxy_url]

            if self.auto_clean and len(self.failed_proxies) % 100 == 0:
                self.save_failed_proxies()

    def get_best_proxy(self) -> Optional[ProxyData]:
        """أفضل بروكسي"""
        with self.lock:
            working = [p for p in self.proxies if p.to_url() not in self.failed_proxies]

            if not working:
                return None

            working.sort(
                key=lambda p: (-p.success_rate, -p.is_elite, p.speed_ms or 99999)
            )

            return working[0]

    def get_random_proxy(self) -> Optional[ProxyData]:
        """بروكسي عشوائي"""
        with self.lock:
            working = [p for p in self.proxies if p.to_url() not in self.failed_proxies]
            return random.choice(working) if working else None

    async def refresh_proxies(self, quick_mode: bool = True):
        """تحديث البروكسيات"""
        logger.info("=" * 60)
        logger.info("🔄 بدء تحديث قاعدة البروكسيات...")
        logger.info("=" * 60)

        # حفظ الشغالة الحالية
        current_working = []
        if self.proxies:
            current_working = [
                p
                for p in self.proxies
                if p.success_rate > 30 and p.to_url() not in self.failed_proxies
            ][
                :200
            ]  # أفضل 200 فقط

            logger.info(f"📦 الاحتفاظ بـ {len(current_working)} بروكسي سابق شغال")

        # جمع جديدة
        new_proxies = await self.collect_proxies(max_per_source=3000)

        if new_proxies:
            # فلترة
            filtered = []
            existing = {f"{p.ip}:{p.port}" for p in self.proxies}

            for proxy in new_proxies:
                key = f"{proxy.ip}:{proxy.port}"
                if key not in existing and proxy.to_url() not in self.failed_proxies:
                    filtered.append(proxy)

            logger.info(f"🆕 {len(filtered)} بروكسي جديد للاختبار")

            if filtered:
                # اختبار
                working_new = await self.test_all_proxies(
                    filtered, max_workers=150, quick_mode=quick_mode
                )

                if working_new:
                    with self.lock:
                        # دمج
                        all_proxies = current_working + working_new

                        # إزالة التكرار
                        unique = {}
                        for proxy in all_proxies:
                            key = f"{proxy.ip}:{proxy.port}"
                            if (
                                key not in unique
                                or proxy.success_rate > unique[key].success_rate
                            ):
                                unique[key] = proxy

                        self.proxies = list(unique.values())

                        # حفظ
                        self.save_proxies()

                    logger.info("=" * 60)
                    logger.info(
                        f"✅ النجاح! إجمالي البروكسيات الشغالة: {len(self.proxies)}"
                    )
                    logger.info("=" * 60)
                else:
                    logger.warning("⚠️ لم يتم العثور على بروكسيات جديدة شغالة")
            else:
                logger.info("ℹ️ جميع البروكسيات تم اختبارها مسبقاً")
        else:
            logger.error("❌ فشل جمع البروكسيات من المصادر")

    def use_proxy(
        self, proxy: ProxyData, url: str, **kwargs
    ) -> Optional[requests.Response]:
        """استخدام بروكسي"""
        if not proxy:
            return None

        proxy_url = proxy.to_url()

        try:
            proxies = {"http": proxy_url, "https": proxy_url}

            response = requests.get(
                url,
                proxies=proxies,
                timeout=kwargs.get("timeout", 20),
                verify=False,
                headers=kwargs.get(
                    "headers",
                    {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                ),
            )

            if response.status_code < 500:
                proxy.success_count += 1
                return response

            proxy.fail_count += 1

            if proxy.fail_count > 5:
                self.mark_proxy_failed(proxy_url)

        except Exception as e:
            proxy.fail_count += 1

            if proxy.fail_count > 3:
                self.mark_proxy_failed(proxy_url)
                logger.debug(f"فشل {proxy_url}: {type(e).__name__}")

        return None

    def get_statistics(self) -> Dict:
        """الإحصائيات"""
        with self.lock:
            total = len(self.proxies)
            working = [p for p in self.proxies if p.to_url() not in self.failed_proxies]

            speeds = [p.speed_ms for p in working if p.speed_ms]
            avg_speed = sum(speeds) / len(speeds) if speeds else 0

            protocols = {}
            anonymity = {}

            for p in working:
                protocols[p.protocol] = protocols.get(p.protocol, 0) + 1
                anonymity[p.anonymity] = anonymity.get(p.anonymity, 0) + 1

            elite = sum(1 for p in working if p.is_elite)

            return {
                "total": total,
                "working": len(working),
                "failed": len(self.failed_proxies),
                "avg_speed_ms": round(avg_speed, 2),
                "protocols": protocols,
                "anonymity": anonymity,
                "elite_count": elite,
                "top_proxies": [
                    {
                        "proxy": f"{p.ip}:{p.port}",
                        "protocol": p.protocol,
                        "speed": p.speed_ms,
                        "rate": round(p.success_rate, 1),
                        "elite": p.is_elite,
                    }
                    for p in working[:10]
                ],
            }


# الدالة الرئيسية
async def main():
    """تشغيل المدير"""

    # إنشاء المدير
    manager = ProxyManager(
        proxy_file="working_proxies.json",
        sources_file="proxy_sources.json",
        failed_file="failed_proxies.json",
        auto_clean=True,
        auto_create_files=True,
    )

    print("\n" + "=" * 60)
    print("🚀 مدير البروكسيات الذكي - الإصدار النهائي")
    print("=" * 60)

    # تحديث البروكسيات
    await manager.refresh_proxies(quick_mode=True)

    # الإحصائيات
    stats = manager.get_statistics()

    print("\n📊 الإحصائيات النهائية:")
    print(f"├─ إجمالي: {stats['total']}")
    print(f"├─ شغال: {stats['working']}")
    print(f"├─ فاشل: {stats['failed']}")
    print(f"└─ متوسط السرعة: {stats['avg_speed_ms']}ms")

    if stats["protocols"]:
        print("\n📡 البروتوكولات:")
        for proto, count in stats["protocols"].items():
            print(f"├─ {proto}: {count}")

    if stats["anonymity"]:
        print("\n🔒 مستوى الإخفاء:")
        for level, count in stats["anonymity"].items():
            print(f"├─ {level}: {count}")
        print(f"└─ Elite: {stats['elite_count']}")

    if stats["top_proxies"]:
        print("\n🏆 أفضل 5 بروكسيات:")
        for i, p in enumerate(stats["top_proxies"][:5], 1):
            elite = "⭐" if p["elite"] else ""
            print(
                f"{i}. {p['proxy']} [{p['protocol']}] - {p['speed']}ms - {p['rate']}% {elite}"
            )

    # اختبار
    print("\n🔧 اختبار البروكسي...")
    proxy = manager.get_best_proxy()

    if proxy:
        print(f"استخدام: {proxy.to_url()}")

        response = manager.use_proxy(proxy, "https://httpbin.org/ip")
        if response:
            print(
                f"✅ نجح! الـ IP المستخدم: {response.json().get('origin', 'غير معروف')}"
            )
        else:
            print("❌ فشل الاختبار")
    else:
        print("❌ لا توجد بروكسيات!")

    print("\n✨ اكتمل!")
    return manager


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 إيقاف...")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
