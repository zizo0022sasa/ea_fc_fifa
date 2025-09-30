# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              💰 FC26 COIN SELLING PRICING - نظام أسعار بيع الكوينز        ║
# ║                     Coin Selling Price Management                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from typing import Dict, List, Optional, Tuple
from enum import Enum

# استيراد قاعدة بيانات الادمن للربط مع الأسعار
try:
    from database.admin_operations import AdminOperations
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

class Platform(Enum):
    """منصات اللعب المدعومة"""
    PLAYSTATION = "playstation"
    XBOX = "xbox" 
    PC = "pc"

class CoinSellPricing:
    """إدارة أسعار بيع الكوينز"""
    
    # الأسعار العادية (التحويل خلال 24 ساعة) - أغلى من الفوري
    NORMAL_PRICES = {
        # PlayStation و Xbox نفس السعر
        Platform.PLAYSTATION.value: {
            1000000: 5600,  # 1M = 5600 ج.م (العادي - أغلى)
        },
        Platform.XBOX.value: {
            1000000: 5600,  # 1M = 5600 ج.م (العادي - أغلى)
        },
        # PC سعر منفصل (أغلى شوية)
        Platform.PC.value: {
            1000000: 6100,  # 1M = 6100 ج.م (العادي - أغلى)
        }
    }
    
    # الأسعار الفورية (التحويل خلال ساعة) - أرخص من العادي
    INSTANT_PRICES = {
        # PlayStation و Xbox نفس السعر
        Platform.PLAYSTATION.value: {
            1000000: 5300,  # 1M = 5300 ج.م (الفوري - أقل)
        },
        Platform.XBOX.value: {
            1000000: 5300,  # 1M = 5300 ج.م (الفوري - أقل)
        },
        # PC سعر منفصل (أغلى شوية)
        Platform.PC.value: {
            1000000: 5800,  # 1M = 5800 ج.م (الفوري - أقل)
        }
    }
    
    # للتوافق مع الكود القديم
    CURRENT_PRICES = NORMAL_PRICES
    

    @classmethod
    def get_price(cls, platform: str, coins: int, transfer_type: str = "normal") -> Optional[int]:
        """جلب السعر من قاعدة البيانات أولاً، ثم الكود كاحتياطي"""
        
        # محاولة جلب السعر من قاعدة البيانات الذكية أولاً
        if DATABASE_AVAILABLE:
            try:
                db_price = AdminOperations.get_price(platform, transfer_type, coins)
                if db_price is not None:
                    return db_price
            except Exception:
                pass  # في حالة الخطأ، استخدم الأسعار الافتراضية
        
        # في حالة عدم وجود السعر في قاعدة البيانات، استخدم القيم الافتراضية
        price_table = cls.INSTANT_PRICES if transfer_type == "instant" else cls.NORMAL_PRICES
        
        if platform not in price_table:
            return None
        
        return price_table[platform].get(coins)
    
    @classmethod
    def get_transfer_prices(cls, platform: str, coins: int) -> Dict[str, Optional[int]]:
        """جلب أسعار التحويل العادي والفوري لكمية معينة"""
        return {
            "normal": cls.get_price(platform, coins, "normal"),
            "instant": cls.get_price(platform, coins, "instant")
        }
    
    @classmethod
    def calculate_custom_price(cls, platform: str, coins: int) -> Optional[int]:
        """حساب السعر لكمية مخصصة من الكوينز"""
        if platform not in cls.CURRENT_PRICES:
            return None
        
        platform_prices = cls.CURRENT_PRICES[platform]
        
        # إذا كانت الكمية موجودة في الباقات المحددة
        if coins in platform_prices:
            return platform_prices[coins]
        
        # حساب السعر بناءً على أقرب كمية
        price_per_100k = cls._get_price_per_100k(platform)
        if price_per_100k:
            return int((coins / 100000) * price_per_100k)
        
        return None
    
    @classmethod
    def _get_price_per_100k(cls, platform: str) -> Optional[float]:
        """حساب سعر الـ 100k كوين للمنصة"""
        if platform not in cls.CURRENT_PRICES:
            return None
        
        # استخدام سعر الـ 100k كأساس
        return cls.CURRENT_PRICES[platform].get(100000, 150)
    
    @classmethod
    def _format_coins(cls, coins: int) -> str:
        """تنسيق عرض الكوينز"""
        if coins >= 1000000:
            millions = coins / 1000000
            if millions == int(millions):
                return f"{int(millions)}M"
            else:
                return f"{millions:.1f}M"
        elif coins >= 1000:
            thousands = coins / 1000
            if thousands == int(thousands):
                return f"{int(thousands)}K" 
            else:
                return f"{thousands:.0f}K"
        else:
            return str(coins)
    
    @classmethod
    def format_price(cls, price: int) -> Dict[str, str]:
        """تنسيق السعر بفاصلة عادية"""
        if not isinstance(price, (int, float)) or price <= 0:
            return {"egp": "0 ج.م"}
        
        price = int(price)
        
        # بالجنيه مع الفاصلة العادية
        formatted_egp = f"{price:,} ج.م"  # فاصلة عادية ","
        
        return {"egp": formatted_egp}
    
    @classmethod
    def get_platform_display_name(cls, platform: str) -> str:
        """جلب اسم المنصة للعرض"""
        platform_names = {
            Platform.PLAYSTATION.value: "🎮 PlayStation",
            Platform.XBOX.value: "🎮 Xbox", 
            Platform.PC.value: "🖥️ PC"
        }
        return platform_names.get(platform, platform)
    
    @classmethod
    def validate_coin_amount(cls, coins: int) -> Tuple[bool, str]:
        """التحقق من صحة كمية الكوينز"""
        if coins < 50000:
            return False, "❌ الحد الأدنى للبيع هو 50,000 كوين"
        
        if coins > 10000000:  # 10M max
            return False, "❌ الحد الأقصى للبيع هو 10,000,000 كوين"
        
        if coins % 10000 != 0:
            return False, "❌ يجب أن تكون الكمية من مضاعفات 10,000 كوين"
        
        return True, "✅ كمية صحيحة"
    
    @classmethod
    def get_discount_info(cls, coins: int) -> Optional[str]:
        """جلب معلومات الخصم إن وجد"""
        if coins >= 2000000:  # 2M+
            return "🎉 خصم خاص للكميات الكبيرة!"
        elif coins >= 1000000:  # 1M+
            return "💰 سعر مميز للمليون كوين!"
        elif coins >= 500000:  # 500K+
            return "⭐ عرض خاص للكميات المتوسطة!"
        
        return None
    
    @classmethod
    def get_all_platforms(cls) -> List[str]:
        """جلب جميع المنصات المدعومة"""
        return list(cls.CURRENT_PRICES.keys())
    
    @classmethod 
    def update_price(cls, platform: str, coins: int, new_price: int) -> bool:
        """تحديث سعر كمية معينة (للإدارة)"""
        if platform not in cls.CURRENT_PRICES:
            return False
        
        cls.CURRENT_PRICES[platform][coins] = new_price
        return True
    
    @classmethod
    def get_price_comparison(cls) -> Dict:
        """مقارنة الأسعار بين المنصات"""
        comparison = {}
        for platform in cls.NORMAL_PRICES:
            comparison[platform] = {
                "platform_name": cls.get_platform_display_name(platform),
                "normal_base_price": cls.NORMAL_PRICES[platform].get(100000, 0),
                "instant_base_price": cls.INSTANT_PRICES[platform].get(100000, 0),
                "price_tiers": len(cls.NORMAL_PRICES[platform])
            }
        
        return comparison
    
    @classmethod
    def get_platform_pricing_message(cls, platform: str) -> str:
        """رسالة أسعار مختصرة - 1M فقط"""
        if platform not in cls.NORMAL_PRICES:
            return "❌ منصة غير مدعومة"
        
        platform_name = cls.get_platform_display_name(platform)
        
        normal_price_1m = cls.NORMAL_PRICES[platform].get(1000000)
        instant_price_1m = cls.INSTANT_PRICES[platform].get(1000000)
        
        normal_formatted = f"{normal_price_1m:,} ج.م" if normal_price_1m else "غير متاح"
        instant_formatted = f"{instant_price_1m:,} ج.م" if instant_price_1m else "غير متاح"
        
        return f"""✅ تم اختيار المنصة

💰 أسعار {platform_name}:

🔸 1M كوين:
   📅 عادي: {normal_formatted}
   ⚡️ فوري: {instant_formatted}


💡 ملاحظات:
📅 التحويل العادي: خلال 24 ساعة
⚡️ التحويل الفوري: خلال ساعة واحدة

🎯 اختر نوع التحويل:"""