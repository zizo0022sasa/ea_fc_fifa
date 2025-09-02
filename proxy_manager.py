#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 مدير البروكسيات الذكي - متكامل مع بوت التليجرام
✅ اختبار على freefollower.net ومواقع عالمية
🗑️ حذف تلقائي للبروكسيات الفاشلة
"""

import asyncio
import json
import logging
import random
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set

import aiohttp
import requests

logger = logging.getLogger(__name__)


@dataclass
class ProxyData:
    """بيانات البروكسي"""

    ip: str
    port: int
    protocol: str = "http"  # http, https, socks4, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    speed_ms: Optional[int] = None
    last_checked: Optional[str] = None
    working_sites: List[str] = None
    success_rate: float = 0.0

    def __post_init__(self):
        if self.working_sites is None:
            self.working_sites = []

    def to_url(self) -> str:
        """تحويل لصيغة URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.ip}:{self.port}"
        return f"{self.protocol}://{self.ip}:{self.port}"

    def to_dict(self) -> dict:
        """تحويل لـ dictionary"""
        return asdict(self)

    @classmethod
    def from_string(cls, proxy_str: str) -> "ProxyData":
        """إنشاء من نص"""
        # معالجة أنواع مختلفة من صيغ البروكسي
        if "@" in proxy_str:
            # protocol://user:pass@ip:port
            parts = proxy_str.split("://")
            protocol = parts[0] if len(parts) > 1 else "http"
            rest = parts[1] if len(parts) > 1 else parts[0]

            auth_host = rest.split("@")
            auth = auth_host[0].split(":")
            host_port = auth_host[1].split(":")

            return cls(
                ip=host_port[0],
                port=int(host_port[1]),
                protocol=protocol,
                username=auth[0],
                password=auth[1],
            )
        elif "://" in proxy_str:
            # protocol://ip:port
            parts = proxy_str.split("://")
            protocol = parts[0]
            host_port = parts[1].split(":")
            return cls(ip=host_port[0], port=int(host_port[1]), protocol=protocol)
        else:
            # ip:port
            parts = proxy_str.split(":")
            return cls(ip=parts[0], port=int(parts[1]), protocol="http")


class ProxyManager:
    """مدير البروكسيات الذكي"""

    def __init__(
        self,
        proxy_file: str = "working_proxies.json",
        sources_file: str = "proxy_sources.json",
        auto_clean: bool = True,
    ):
        self.proxy_file = proxy_file
        self.sources_file = sources_file
        self.auto_clean = auto_clean
        self.proxies: List[ProxyData] = []
        self.failed_proxies: Set[str] = set()
        self.lock = threading.Lock()

        # قائمة المواقع للاختبار
        self.test_sites = {
            # الموقع الرئيسي
            "freefollower": "https://freefollower.net/",
            # مواقع التواصل الاجتماعي العالمية
            "facebook": "https://www.facebook.com/robots.txt",
            "instagram": "https://www.instagram.com/robots.txt",
            "twitter": "https://twitter.com/robots.txt",
            "tiktok": "https://www.tiktok.com/robots.txt",
            "youtube": "https://www.youtube.com/robots.txt",
            "linkedin": "https://www.linkedin.com/robots.txt",
            "pinterest": "https://www.pinterest.com/robots.txt",
            "reddit": "https://www.reddit.com/robots.txt",
            "snapchat": "https://www.snapchat.com/robots.txt",
            "whatsapp": "https://www.whatsapp.com/robots.txt",
            "telegram": "https://telegram.org/robots.txt",
            "discord": "https://discord.com/robots.txt",
            "twitch": "https://www.twitch.tv/robots.txt",
            "tumblr": "https://www.tumblr.com/robots.txt",
            "vk": "https://vk.com/robots.txt",
            "weibo": "https://weibo.com/robots.txt",
            "wechat": "https://www.wechat.com/robots.txt",
            # منصات الفيديو والترفيه
            "netflix": "https://www.netflix.com/robots.txt",
            "spotify": "https://open.spotify.com/robots.txt",
            "soundcloud": "https://soundcloud.com/robots.txt",
            "vimeo": "https://vimeo.com/robots.txt",
            "dailymotion": "https://www.dailymotion.com/robots.txt",
            "hulu": "https://www.hulu.com/robots.txt",
            "hbo": "https://www.hbo.com/robots.txt",
            "disney": "https://www.disneyplus.com/robots.txt",
            "prime": "https://www.primevideo.com/robots.txt",
            # محركات البحث
            "google": "https://www.google.com/robots.txt",
            "bing": "https://www.bing.com/robots.txt",
            "yahoo": "https://search.yahoo.com/robots.txt",
            "duckduckgo": "https://duckduckgo.com/robots.txt",
            "baidu": "https://www.baidu.com/robots.txt",
            "yandex": "https://yandex.com/robots.txt",
            # التجارة الإلكترونية
            "amazon": "https://www.amazon.com/robots.txt",
            "ebay": "https://www.ebay.com/robots.txt",
            "alibaba": "https://www.alibaba.com/robots.txt",
            "aliexpress": "https://www.aliexpress.com/robots.txt",
            "shopify": "https://www.shopify.com/robots.txt",
            "etsy": "https://www.etsy.com/robots.txt",
            # مواقع تقنية
            "github": "https://github.com/robots.txt",
            "stackoverflow": "https://stackoverflow.com/robots.txt",
            "gitlab": "https://gitlab.com/robots.txt",
            "bitbucket": "https://bitbucket.org/robots.txt",
            # مواقع إخبارية
            "cnn": "https://www.cnn.com/robots.txt",
            "bbc": "https://www.bbc.com/robots.txt",
            "nytimes": "https://www.nytimes.com/robots.txt",
            "theguardian": "https://www.theguardian.com/robots.txt",
            "reuters": "https://www.reuters.com/robots.txt",
            # منصات عربية
            "shahid": "https://shahid.mbc.net/robots.txt",
            "anghami": "https://www.anghami.com/robots.txt",
            "souq": "https://www.souq.com/robots.txt",
            "noon": "https://www.noon.com/robots.txt",
            "careem": "https://www.careem.com/robots.txt",
            # مواقع آسيوية
            "wechat_cn": "https://weixin.qq.com/robots.txt",
            "line": "https://line.me/robots.txt",
            "kakao": "https://www.kakaocorp.com/robots.txt",
            "naver": "https://www.naver.com/robots.txt",
            "rakuten": "https://www.rakuten.com/robots.txt",
            # مواقع أوروبية
            "spotify_eu": "https://www.spotify.com/de/robots.txt",
            "zalando": "https://www.zalando.com/robots.txt",
            "booking": "https://www.booking.com/robots.txt",
            "skyscanner": "https://www.skyscanner.com/robots.txt",
            # مواقع أمريكا اللاتينية
            "mercadolibre": "https://www.mercadolibre.com/robots.txt",
            "globo": "https://www.globo.com/robots.txt",
            # مواقع أفريقية
            "jumia": "https://www.jumia.com/robots.txt",
            "takealot": "https://www.takealot.com/robots.txt",
            # بنوك ومالية
            "paypal": "https://www.paypal.com/robots.txt",
            "stripe": "https://stripe.com/robots.txt",
            "wise": "https://wise.com/robots.txt",
            # ألعاب
            "steam": "https://store.steampowered.com/robots.txt",
            "epicgames": "https://www.epicgames.com/robots.txt",
            "roblox": "https://www.roblox.com/robots.txt",
            "minecraft": "https://www.minecraft.net/robots.txt",
            # تعليم
            "coursera": "https://www.coursera.org/robots.txt",
            "udemy": "https://www.udemy.com/robots.txt",
            "edx": "https://www.edx.org/robots.txt",
            "khanacademy": "https://www.khanacademy.org/robots.txt",
        }

        # مصادر البروكسيات
        self.proxy_sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=all&timeout=20000&country=all&ssl=all&anonymity=all",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://www.proxy-list.download/api/v1/get?type=https",
            "https://www.proxy-list.download/api/v1/get?type=socks4",
            "https://www.proxy-list.download/api/v1/get?type=socks5",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc",
            "https://www.proxyscan.io/download?type=http",
            "https://www.proxyscan.io/download?type=https",
            "https://www.proxyscan.io/download?type=socks4",
            "https://www.proxyscan.io/download?type=socks5",
        ]

        self.load_proxies()

    def load_proxies(self):
        """تحميل البروكسيات من الملف"""
        try:
            with open(self.proxy_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.proxies = [ProxyData(**p) for p in data]
                logger.info(
                    f"✅ تم تحميل {len(self.proxies)} بروكسي من {self.proxy_file}"
                )
        except FileNotFoundError:
            logger.warning(f"⚠️ ملف {self.proxy_file} غير موجود")
            self.proxies = []
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل البروكسيات: {e}")
            self.proxies = []

    def save_proxies(self):
        """حفظ البروكسيات في الملف"""
        try:
            with self.lock:
                # فلترة البروكسيات الشغالة فقط
                working_proxies = [
                    p for p in self.proxies if p.to_url() not in self.failed_proxies
                ]

                data = [p.to_dict() for p in working_proxies]

                with open(self.proxy_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                logger.info(
                    f"💾 تم حفظ {len(working_proxies)} بروكسي في {self.proxy_file}"
                )
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ البروكسيات: {e}")

    async def fetch_proxies_from_source(
        self, session: aiohttp.ClientSession, url: str
    ) -> List[str]:
        """جلب بروكسيات من مصدر واحد"""
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                if response.status == 200:
                    text = await response.text()

                    # معالجة JSON إذا كان
                    if url.endswith(".json") or "json" in response.headers.get(
                        "content-type", ""
                    ):
                        try:
                            data = json.loads(text)
                            if isinstance(data, dict) and "data" in data:
                                proxies = []
                                for item in data["data"]:
                                    if "ip" in item and "port" in item:
                                        proxies.append(f"{item['ip']}:{item['port']}")
                                return proxies
                        except:
                            pass

                    # معالجة نص عادي
                    lines = text.strip().split("\n")
                    proxies = []
                    for line in lines:
                        line = line.strip()
                        if ":" in line and not line.startswith("#"):
                            proxies.append(line.split()[0] if " " in line else line)

                    return proxies
        except Exception as e:
            logger.debug(f"فشل جلب من {url}: {e}")

        return []

    async def collect_proxies(self) -> List[ProxyData]:
        """جمع البروكسيات من جميع المصادر"""
        logger.info("🔄 جمع البروكسيات من المصادر...")

        all_proxies = set()

        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_proxies_from_source(session, url)
                for url in self.proxy_sources
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, list):
                    all_proxies.update(result)

        # تحويل لـ ProxyData
        proxy_objects = []
        for proxy_str in all_proxies:
            try:
                proxy = ProxyData.from_string(proxy_str)
                proxy_objects.append(proxy)
            except:
                continue

        logger.info(f"✅ تم جمع {len(proxy_objects)} بروكسي فريد")
        return proxy_objects

    async def test_proxy(
        self, proxy: ProxyData, test_url: str = None, timeout: int = 20
    ) -> bool:
        """اختبار بروكسي واحد"""
        if test_url is None:
            test_url = self.test_sites["freefollower"]

        proxy_url = proxy.to_url()

        # إعداد البروكسي حسب المكتبة
        if proxy.protocol in ["socks4", "socks5"]:
            # للـ SOCKS نحتاج aiohttp-socks
            connector = None  # سنستخدم requests بدلاً من aiohttp للـ SOCKS

            try:
                proxies = {"http": proxy_url, "https": proxy_url}

                start_time = time.time()
                response = requests.get(
                    test_url,
                    proxies=proxies,
                    timeout=timeout,
                    verify=False,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                )

                elapsed = int((time.time() - start_time) * 1000)

                if response.status_code in [200, 301, 302]:
                    proxy.speed_ms = elapsed
                    proxy.last_checked = datetime.now().isoformat()

                    if test_url not in proxy.working_sites:
                        proxy.working_sites.append(test_url)

                    return True

            except Exception as e:
                logger.debug(f"فشل {proxy_url}: {e}")
                return False
        else:
            # HTTP/HTTPS
            try:
                connector = aiohttp.TCPConnector(ssl=False)
                timeout_obj = aiohttp.ClientTimeout(total=timeout)

                async with aiohttp.ClientSession(
                    connector=connector, timeout=timeout_obj
                ) as session:
                    start_time = time.time()

                    async with session.get(
                        test_url,
                        proxy=proxy_url,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        },
                    ) as response:
                        elapsed = int((time.time() - start_time) * 1000)

                        if response.status in [200, 301, 302]:
                            proxy.speed_ms = elapsed
                            proxy.last_checked = datetime.now().isoformat()

                            if test_url not in proxy.working_sites:
                                proxy.working_sites.append(test_url)

                            return True

            except Exception as e:
                logger.debug(f"فشل {proxy_url}: {e}")
                return False

        return False

    async def test_all_proxies(
        self, proxies: List[ProxyData] = None, max_workers: int = 50
    ) -> List[ProxyData]:
        """اختبار جميع البروكسيات"""
        if proxies is None:
            proxies = self.proxies

        if not proxies:
            logger.warning("⚠️ لا توجد بروكسيات للاختبار")
            return []

        logger.info(f"🔬 اختبار {len(proxies)} بروكسي على freefollower.net...")

        working_proxies = []

        # اختبار على الموقع الرئيسي أولاً
        semaphore = asyncio.Semaphore(max_workers)

        async def test_with_semaphore(proxy):
            async with semaphore:
                if await self.test_proxy(proxy, self.test_sites["freefollower"], 20):
                    return proxy
                return None

        tasks = [test_with_semaphore(proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if result and not isinstance(result, Exception):
                working_proxies.append(result)

        logger.info(f"✅ {len(working_proxies)} بروكسي يعمل على freefollower.net")

        # اختبار اختياري على مواقع أخرى
        if working_proxies and len(working_proxies) > 0:
            logger.info("🌍 اختبار على مواقع عالمية إضافية...")

            # اختبار على عينة من المواقع
            sample_sites = random.sample(
                list(self.test_sites.items()), min(10, len(self.test_sites))
            )

            for site_name, site_url in sample_sites:
                if site_name == "freefollower":
                    continue

                logger.info(f"🔍 اختبار على {site_name}...")

                tasks = [
                    self.test_proxy(proxy, site_url, 10)
                    for proxy in working_proxies[:20]
                ]
                await asyncio.gather(*tasks, return_exceptions=True)

        # حساب معدل النجاح
        for proxy in working_proxies:
            if len(proxy.working_sites) > 0:
                proxy.success_rate = (
                    len(proxy.working_sites) / len(self.test_sites) * 100
                )

        # ترتيب حسب السرعة
        working_proxies.sort(key=lambda p: p.speed_ms or 99999)

        return working_proxies

    def mark_proxy_failed(self, proxy_url: str):
        """تحديد بروكسي كفاشل وحذفه"""
        with self.lock:
            self.failed_proxies.add(proxy_url)

            # حذف من القائمة
            self.proxies = [p for p in self.proxies if p.to_url() != proxy_url]

            # حفظ تلقائي
            if self.auto_clean:
                self.save_proxies()

            logger.warning(f"🗑️ تم حذف البروكسي الفاشل: {proxy_url}")

    def get_best_proxy(self) -> Optional[ProxyData]:
        """الحصول على أفضل بروكسي متاح"""
        with self.lock:
            # فلترة البروكسيات الشغالة
            working = [p for p in self.proxies if p.to_url() not in self.failed_proxies]

            if not working:
                return None

            # ترتيب حسب السرعة ومعدل النجاح
            working.sort(key=lambda p: (p.speed_ms or 99999, -p.success_rate))

            return working[0]

    def get_random_proxy(self) -> Optional[ProxyData]:
        """الحصول على بروكسي عشوائي"""
        with self.lock:
            working = [p for p in self.proxies if p.to_url() not in self.failed_proxies]

            if not working:
                return None

            return random.choice(working)

    async def refresh_proxies(self):
        """تحديث قائمة البروكسيات"""
        logger.info("🔄 تحديث قائمة البروكسيات...")

        # جمع بروكسيات جديدة
        new_proxies = await self.collect_proxies()

        # اختبارها
        working_proxies = await self.test_all_proxies(new_proxies, max_workers=100)

        if working_proxies:
            with self.lock:
                # دمج مع الموجودة
                existing_urls = {p.to_url() for p in self.proxies}

                for proxy in working_proxies:
                    if proxy.to_url() not in existing_urls:
                        self.proxies.append(proxy)

                # حفظ
                self.save_proxies()

            logger.info(f"✅ تم إضافة {len(working_proxies)} بروكسي جديد")
        else:
            logger.warning("⚠️ لم يتم العثور على بروكسيات جديدة شغالة")

    def use_proxy(
        self, proxy: ProxyData, url: str, **kwargs
    ) -> Optional[requests.Response]:
        """استخدام بروكسي مع الحذف التلقائي عند الفشل"""
        proxy_url = proxy.to_url()

        proxies = {"http": proxy_url, "https": proxy_url}

        try:
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

            if response.status_code >= 400:
                # البروكسي شغال لكن رد بخطأ
                if response.status_code in [403, 429]:
                    # محظور أو rate limited
                    self.mark_proxy_failed(proxy_url)
                    return None

            return response

        except Exception as e:
            # البروكسي فشل
            logger.error(f"❌ فشل البروكسي {proxy_url}: {e}")
            self.mark_proxy_failed(proxy_url)
            return None

    def get_statistics(self) -> Dict:
        """احصائيات البروكسيات"""
        with self.lock:
            total = len(self.proxies)
            failed = len(self.failed_proxies)
            working = total - failed

            speeds = [p.speed_ms for p in self.proxies if p.speed_ms]
            avg_speed = sum(speeds) / len(speeds) if speeds else 0

            protocols = {}
            for p in self.proxies:
                protocols[p.protocol] = protocols.get(p.protocol, 0) + 1

            countries = {}
            for p in self.proxies:
                if p.country:
                    countries[p.country] = countries.get(p.country, 0) + 1

            return {
                "total": total,
                "working": working,
                "failed": failed,
                "avg_speed_ms": avg_speed,
                "protocols": protocols,
                "countries": countries,
                "top_sites": self._get_top_working_sites(),
            }

    def _get_top_working_sites(self) -> List[tuple]:
        """المواقع الأكثر نجاحاً"""
        site_counts = {}

        for proxy in self.proxies:
            for site in proxy.working_sites:
                site_counts[site] = site_counts.get(site, 0) + 1

        return sorted(site_counts.items(), key=lambda x: x[1], reverse=True)[:10]


# مثال على الاستخدام
async def main():
    # إنشاء المدير
    manager = ProxyManager()

    # تحديث البروكسيات
    await manager.refresh_proxies()

    # احصائيات
    stats = manager.get_statistics()
    print(f"📊 إحصائيات البروكسيات:")
    print(f"  • إجمالي: {stats['total']}")
    print(f"  • شغال: {stats['working']}")
    print(f"  • متوسط السرعة: {stats['avg_speed_ms']:.0f}ms")

    # استخدام بروكسي
    proxy = manager.get_best_proxy()
    if proxy:
        print(f"🌐 أفضل بروكسي: {proxy.to_url()}")
        response = manager.use_proxy(proxy, "https://freefollower.net/")
        if response:
            print(f"✅ نجح الطلب: {response.status_code}")
        else:
            print("❌ فشل الطلب")


if __name__ == "__main__":
    asyncio.run(main())
