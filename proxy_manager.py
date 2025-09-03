#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 مدير البروكسيات المحسّن - النسخة النهائية الشغالة
✅ بساطة وكفاءة عالية
🚀 اختبار سريع ودقيق
"""

import json
import logging
import os
import random
import socket
import threading
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List, Optional, Set

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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


class ProxyTester:
    """فئة اختبار البروكسيات"""

    def __init__(self):
        self.test_urls = [
            "https://freefollower.net/",
            "https://api.ipify.org/",
            "http://www.google.com/generate_204",
        ]

    def quick_test(self, ip: str, port: int, timeout: int = 3) -> bool:
        """اختبار سريع للمنفذ"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def test_http_proxy(self, proxy_url: str, timeout: int = 10) -> Dict:
        """اختبار HTTP proxy"""
        result = {
            "working": False,
            "speed_ms": None,
            "anonymity": "unknown",
            "response_code": None,
        }

        try:
            session = requests.Session()
            
            # إعداد retry strategy
            retry_strategy = Retry(
                total=2,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            proxies = {"http": proxy_url, "https": proxy_url}

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            start_time = time.time()

            # اختبار على موقع سريع
            response = session.get(
                "http://httpbin.org/ip",
                proxies=proxies,
                headers=headers,
                timeout=timeout,
                verify=False,
            )

            elapsed_ms = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                result["working"] = True
                result["speed_ms"] = elapsed_ms
                result["response_code"] = response.status_code

                # فحص مستوى الإخفاء
                try:
                    response_data = response.json()
                    origin_ip = response_data.get("origin", "").split(",")[0].strip()
                    proxy_ip = proxy_url.split("@")[-1].split(":")[0]

                    if proxy_ip not in origin_ip:
                        result["anonymity"] = "elite"
                    else:
                        result["anonymity"] = "transparent"
                except:
                    result["anonymity"] = "anonymous"

        except requests.exceptions.ConnectTimeout:
            pass
        except requests.exceptions.ProxyError:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except Exception:
            pass

        return result


class ProxyManager:
    """مدير البروكسيات الذكي المبسط"""

    def __init__(self):
        self.working_proxies = []
        self.failed_proxies = set()
        self.lock = threading.Lock()
        self.tester = ProxyTester()
        
        # ملفات التخزين
        self.working_file = "working_proxies.json"
        self.failed_file = "failed_proxies.json"

        # مصادر البروكسيات - تم اختيار الأفضل فقط
        self.sources = [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all&simplified=true",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt",
            "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
        ]

        # تحميل البيانات المحفوظة
        self.load_data()

    def load_data(self):
        """تحميل البيانات المحفوظة"""
        # تحميل البروكسيات الشغالة
        try:
            if os.path.exists(self.working_file):
                with open(self.working_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.working_proxies = data
                    logger.info(f"✅ تم تحميل {len(self.working_proxies)} بروكسي شغال")
        except:
            self.working_proxies = []

        # تحميل البروكسيات الفاشلة
        try:
            if os.path.exists(self.failed_file):
                with open(self.failed_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.failed_proxies = set(data.get("failed", []))
                    logger.info(f"📋 تم تحميل {len(self.failed_proxies)} بروكسي فاشل")
        except:
            self.failed_proxies = set()

    def save_data(self):
        """حفظ البيانات"""
        try:
            # حفظ الشغالة
            with open(self.working_file, "w", encoding="utf-8") as f:
                json.dump(self.working_proxies, f, ensure_ascii=False, indent=2)

            # حفظ الفاشلة
            failed_data = {
                "failed": list(self.failed_proxies)[:5000],  # حد أقصى 5000
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.failed_file, "w", encoding="utf-8") as f:
                json.dump(failed_data, f, ensure_ascii=False, indent=2)

            logger.info(f"💾 تم حفظ {len(self.working_proxies)} بروكسي شغال")
        except Exception as e:
            logger.error(f"خطأ في الحفظ: {e}")

    def fetch_from_source(self, url: str) -> List[str]:
        """جلب بروكسيات من مصدر واحد"""
        proxies = []
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                content = response.text
                
                # استخراج بسيط وفعال
                lines = content.split('\n')
                
                for line in lines:
                    line = line.strip()
                    
                    # تجاهل الأسطر الفارغة والتعليقات
                    if not line or line.startswith('#') or line.startswith('//'):
                        continue
                    
                    # تنظيف السطر
                    line = line.replace('http://', '').replace('https://', '')
                    
                    # البحث عن نمط IP:Port
                    if ':' in line:
                        parts = line.split()
                        proxy_part = parts[0]  # أول جزء عادة يحتوي على IP:Port
                        
                        try:
                            if '@' in proxy_part:
                                # إزالة معلومات المصادقة إن وجدت
                                proxy_part = proxy_part.split('@')[-1]
                            
                            ip, port = proxy_part.rsplit(':', 1)
                            port_num = int(port)
                            
                            # تحقق من صحة المنفذ
                            if 1 <= port_num <= 65535:
                                proxies.append(f"{ip}:{port}")
                                
                        except (ValueError, IndexError):
                            continue
                
                logger.info(f"✓ جلب {len(proxies)} من {url.split('/')[2]}")
                
        except Exception as e:
            logger.debug(f"✗ فشل {url.split('/')[2] if '/' in url else url}: {type(e).__name__}")
        
        return proxies

    def collect_proxies(self) -> List[str]:
        """جمع البروكسيات من جميع المصادر"""
        logger.info("🔄 جمع البروكسيات من المصادر...")
        
        all_proxies = set()
        
        # استخدام threading لتسريع العملية
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(self.fetch_from_source, self.sources))
        
        # دمج النتائج
        for proxy_list in results:
            for proxy in proxy_list:
                # تجنب الفاشلة والمكررة
                if proxy not in self.failed_proxies:
                    all_proxies.add(proxy)
        
        proxy_list = list(all_proxies)
        random.shuffle(proxy_list)  # خلط عشوائي
        
        logger.info(f"✅ تم جمع {len(proxy_list)} بروكسي فريد")
        return proxy_list

    def test_proxy(self, proxy_str: str) -> Optional[Dict]:
        """اختبار بروكسي واحد"""
        try:
            ip, port = proxy_str.split(':')
            port = int(port)
            
            # اختبار سريع أولاً
            if not self.tester.quick_test(ip, port, timeout=3):
                return None
            
            # اختبار HTTP
            proxy_url = f"http://{proxy_str}"
            result = self.tester.test_http_proxy(proxy_url, timeout=10)
            
            if result["working"]:
                return {
                    "proxy": proxy_str,
                    "ip": ip,
                    "port": port,
                    "protocol": "http",
                    "speed_ms": result["speed_ms"],
                    "anonymity": result["anonymity"],
                    "last_checked": datetime.now().isoformat(),
                    "success_count": 1,
                    "fail_count": 0,
                }
            
        except Exception:
            pass
        
        return None

    def test_all_proxies(self, proxy_list: List[str], max_workers: int = 100) -> List[Dict]:
        """اختبار جميع البروكسيات"""
        if not proxy_list:
            logger.warning("⚠️ لا توجد بروكسيات للاختبار")
            return []

        logger.info(f"🔬 اختبار {len(proxy_list)} بروكسي...")
        
        working_proxies = []
        
        # اختبار بالتوازي
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # معالجة على دفعات لتجنب استهلاك الذاكرة
            batch_size = 500
            total_tested = 0
            
            for i in range(0, len(proxy_list), batch_size):
                batch = proxy_list[i:i + batch_size]
                
                # اختبار الدفعة
                results = list(executor.map(self.test_proxy, batch))
                
                # جمع النتائج الشغالة
                batch_working = [r for r in results if r is not None]
                working_proxies.extend(batch_working)
                
                # تحديث الفاشلة
                failed_batch = [
                    proxy for proxy, result in zip(batch, results) 
                    if result is None
                ]
                self.failed_proxies.update(failed_batch)
                
                total_tested += len(batch)
                success_rate = (len(working_proxies) / total_tested * 100) if total_tested > 0 else 0
                
                logger.info(
                    f"📊 التقدم: {total_tested}/{len(proxy_list)} | "
                    f"✅ شغال: {len(working_proxies)} | "
                    f"📈 معدل النجاح: {success_rate:.1f}%"
                )
                
                # إذا وجدنا عدد كافي، نكتفي
                if len(working_proxies) >= 200:
                    logger.info("✨ تم العثور على عدد كافي من البروكسيات")
                    break
        
        # ترتيب حسب السرعة
        working_proxies.sort(key=lambda p: p.get('speed_ms', 99999))
        
        logger.info(f"🎉 النتيجة النهائية: {len(working_proxies)} بروكسي شغال!")
        return working_proxies

    def refresh_proxies(self):
        """تحديث البروكسيات"""
        logger.info("=" * 60)
        logger.info("🚀 بدء تحديث قاعدة البروكسيات...")
        logger.info("=" * 60)
        
        # جمع بروكسيات جديدة
        new_proxies = self.collect_proxies()
        
        if new_proxies:
            # اختبار
            working_new = self.test_all_proxies(new_proxies[:2000])  # حد أقصى 2000 للاختبار
            
            if working_new:
                with self.lock:
                    # دمج مع الموجودة
                    existing_ips = {p.get('ip') for p in self.working_proxies}
                    
                    # إضافة الجديدة فقط
                    for proxy in working_new:
                        if proxy['ip'] not in existing_ips:
                            self.working_proxies.append(proxy)
                    
                    # ترتيب حسب السرعة
                    self.working_proxies.sort(key=lambda p: p.get('speed_ms', 99999))
                    
                    # الاحتفاظ بأفضل 500 فقط
                    self.working_proxies = self.working_proxies[:500]
                
                # حفظ
                self.save_data()
                
                logger.info("=" * 60)
                logger.info(f"✅ النجاح! إجمالي البروكسيات الشغالة: {len(self.working_proxies)}")
                logger.info("=" * 60)
            else:
                logger.warning("⚠️ لم يتم العثور على بروكسيات شغالة")
        else:
            logger.error("❌ فشل جمع البروكسيات من المصادر")

    def get_best_proxy(self) -> Optional[Dict]:
        """أفضل بروكسي"""
        with self.lock:
            if self.working_proxies:
                return self.working_proxies[0]  # أسرع بروكسي
        return None

    def get_random_proxy(self) -> Optional[Dict]:
        """بروكسي عشوائي"""
        with self.lock:
            if self.working_proxies:
                return random.choice(self.working_proxies)
        return None

    def test_proxy_on_site(self, proxy_dict: Dict, url: str = "https://httpbin.org/ip") -> bool:
        """اختبار بروكسي على موقع محدد"""
        try:
            proxy_url = f"http://{proxy_dict['proxy']}"
            proxies = {"http": proxy_url, "https": proxy_url}
            
            response = requests.get(
                url,
                proxies=proxies,
                timeout=15,
                verify=False,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            
            return response.status_code == 200
            
        except:
            return False

    def get_statistics(self) -> Dict:
        """إحصائيات مفصلة"""
        with self.lock:
            if not self.working_proxies:
                return {"error": "لا توجد بروكسيات"}
            
            speeds = [p.get('speed_ms', 0) for p in self.working_proxies if p.get('speed_ms')]
            avg_speed = sum(speeds) / len(speeds) if speeds else 0
            
            anonymity_levels = {}
            for p in self.working_proxies:
                level = p.get('anonymity', 'unknown')
                anonymity_levels[level] = anonymity_levels.get(level, 0) + 1
            
            return {
                "total_working": len(self.working_proxies),
                "total_failed": len(self.failed_proxies),
                "avg_speed_ms": round(avg_speed, 2),
                "fastest_speed": min(speeds) if speeds else 0,
                "slowest_speed": max(speeds) if speeds else 0,
                "anonymity_levels": anonymity_levels,
                "top_10": [
                    {
                        "proxy": p['proxy'],
                        "speed_ms": p.get('speed_ms', 'N/A'),
                        "anonymity": p.get('anonymity', 'unknown')
                    }
                    for p in self.working_proxies[:10]
                ]
            }


def main():
    """الدالة الرئيسية"""
    
    print("\n" + "=" * 60)
    print("🚀 مدير البروكسيات المحسّن - النسخة النهائية")
    print("=" * 60)
    
    # إنشاء المدير
    manager = ProxyManager()
    
    # تحديث البروكسيات
    manager.refresh_proxies()
    
    # عرض الإحصائيات
    stats = manager.get_statistics()
    
    if "error" not in stats:
        print(f"\n📊 الإحصائيات النهائية:")
        print(f"├─ إجمالي الشغال: {stats['total_working']}")
        print(f"├─ إجمالي الفاشل: {stats['total_failed']}")
        print(f"├─ متوسط السرعة: {stats['avg_speed_ms']}ms")
        print(f"├─ أسرع بروكسي: {stats['fastest_speed']}ms")
        print(f"└─ أبطأ بروكسي: {stats['slowest_speed']}ms")
        
        if stats['anonymity_levels']:
            print(f"\n🔒 مستويات الإخفاء:")
            for level, count in stats['anonymity_levels'].items():
                print(f"├─ {level}: {count}")
        
        print(f"\n🏆 أفضل 5 بروكسيات:")
        for i, p in enumerate(stats['top_10'][:5], 1):
            print(f"{i}. {p['proxy']} - {p['speed_ms']}ms - {p['anonymity']}")
        
        # اختبار أفضل بروكسي
        print(f"\n🔧 اختبار أفضل بروكسي...")
        best_proxy = manager.get_best_proxy()
        
        if best_proxy:
            print(f"استخدام: {best_proxy['proxy']}")
            
            # اختبار على httpbin
            if manager.test_proxy_on_site(best_proxy):
                print(f"✅ نجح الاختبار!")
                
                # اختبار فعلي للحصول على IP
                try:
                    proxy_url = f"http://{best_proxy['proxy']}"
                    response = requests.get(
                        "http://httpbin.org/ip",
                        proxies={"http": proxy_url, "https": proxy_url},
                        timeout=10
                    )
                    if response.status_code == 200:
                        ip_data = response.json()
                        print(f"🌐 الـ IP المستخدم: {ip_data.get('origin', 'غير معروف')}")
                except:
                    pass
            else:
                print(f"❌ فشل الاختبار")
        
    else:
        print(f"❌ {stats['error']}")
    
    print(f"\n✨ اكتمل!")
    print(f"💾 البيانات محفوظة في: working_proxies.json")
    
    return manager


if __name__ == "__main__":
    try:
        manager = main()
    except KeyboardInterrupt:
        print("\n👋 إيقاف...")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
