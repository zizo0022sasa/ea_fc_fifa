# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              💰 FC26 PRICE MANAGEMENT - إدارة الأسعار                    ║
# ║                     Price Management Handler                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import re
from typing import Optional, Tuple
import sys
import os

# إضافة مسار المشروع لاستيراد قاعدة البيانات
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.admin_operations import AdminOperations

class PriceManagement:
    """معالج إدارة الأسعار"""
    
    # الحدود المسموحة للأسعار
    MIN_PRICE = 1000  # 1000 ج.م
    MAX_PRICE = 50000  # 50000 ج.م
    
    # الكمية الافتراضية
    DEFAULT_AMOUNT = 1000000  # 1M كوين
    
    @classmethod
    def validate_price_input(cls, price_text: str) -> Tuple[bool, Optional[int], str]:
        """التحقق من صحة السعر المدخل"""
        if not price_text or not isinstance(price_text, str):
            return False, None, "يرجى إدخال سعر صحيح"
        
        # تنظيف النص من الفواصل والمسافات
        cleaned = re.sub(r'[^\d]', '', price_text.strip())
        
        if not cleaned:
            return False, None, "يرجى إدخال أرقام فقط"
        
        try:
            price = int(cleaned)
        except ValueError:
            return False, None, "يرجى إدخال رقم صحيح"
        
        # التحقق من الحدود
        if price < cls.MIN_PRICE:
            return False, None, f"السعر قليل جداً! الحد الأدنى: {cls.MIN_PRICE:,} ج.م"
        
        if price > cls.MAX_PRICE:
            return False, None, f"السعر عالي جداً! الحد الأقصى: {cls.MAX_PRICE:,} ج.م"
        
        return True, price, "سعر صحيح"
    
    @classmethod
    def get_current_price(cls, platform: str, transfer_type: str) -> Optional[int]:
        """جلب السعر الحالي"""
        return AdminOperations.get_price(platform, transfer_type, cls.DEFAULT_AMOUNT)
    
    @classmethod
    async def update_price(cls, platform: str, transfer_type: str, new_price: int, admin_id: int) -> bool:
        """تحديث السعر - Thread-safe async version"""
        return await AdminOperations.update_price(
            platform, transfer_type, cls.DEFAULT_AMOUNT, new_price, admin_id
        )
    
    @classmethod
    def get_all_current_prices(cls):
        """جلب جميع الأسعار الحالية"""
        return AdminOperations.get_all_prices()
    
    @classmethod
    def calculate_price_difference(cls, old_price: int, new_price: int) -> dict:
        """حساب الفرق في السعر"""
        difference = new_price - old_price
        percentage = (difference / old_price) * 100 if old_price > 0 else 0
        
        return {
            'absolute_diff': difference,
            'percentage_diff': round(percentage, 2),
            'is_increase': difference > 0,
            'is_decrease': difference < 0
        }
    
    @classmethod
    def format_price_change(cls, old_price: int, new_price: int) -> str:
        """تنسيق عرض تغيير السعر"""
        diff = cls.calculate_price_difference(old_price, new_price)
        
        if diff['is_increase']:
            return f"📈 زيادة: +{diff['absolute_diff']:,} ج.م ({diff['percentage_diff']:+.1f}%)"
        elif diff['is_decrease']:
            return f"📉 نقص: {diff['absolute_diff']:,} ج.م ({diff['percentage_diff']:+.1f}%)"
        else:
            return "➡️ لا يوجد تغيير"
    
    @classmethod
    def validate_platform(cls, platform: str) -> bool:
        """التحقق من صحة المنصة"""
        valid_platforms = ['playstation', 'xbox', 'pc']
        return platform.lower() in valid_platforms
    
    @classmethod
    def validate_transfer_type(cls, transfer_type: str) -> bool:
        """التحقق من صحة نوع التحويل"""
        valid_types = ['normal', 'instant']
        return transfer_type.lower() in valid_types
    
    @classmethod
    def get_price_history_summary(cls, platform: str, transfer_type: str, limit: int = 5):
        """جلب ملخص تاريخ تغيير السعر (يحتاج تطوير إضافي في قاعدة البيانات)"""
        # هذه الدالة للتطوير المستقبلي
        pass
    
    @classmethod
    def export_prices_data(cls) -> dict:
        """تصدير بيانات الأسعار"""
        prices = cls.get_all_current_prices()
        
        export_data = {
            'export_time': AdminOperations.get_current_timestamp(),
            'total_prices': len(prices),
            'platforms': {},
            'raw_data': prices
        }
        
        # تجميع البيانات حسب المنصة
        for price in prices:
            platform = price['platform']
            if platform not in export_data['platforms']:
                export_data['platforms'][platform] = {
                    'normal': None,
                    'instant': None
                }
            
            export_data['platforms'][platform][price['transfer_type']] = price['price']
        
        return export_data