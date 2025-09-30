# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🔗 FC26 URL VALIDATOR - مدقق الروابط                       ║
# ║                        URL Validation                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import re
import logging
from typing import Dict, Any, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class URLValidator:
    """URL validation for InstaPay and other links"""
    
    INSTAPAY_DOMAINS = [
        'instapay.com.eg',
        'ipn.eg',
        'instapay.eg'
    ]
    
    @classmethod
    def validate_instapay_url(cls, url: str) -> Dict[str, Any]:
        """
        Validate InstaPay URL
        
        Args:
            url (str): URL to validate
            
        Returns:
            Dict[str, Any]: Validation result
        """
        try:
            # Clean and normalize URL
            cleaned_url = url.strip()
            
            # Add protocol if missing
            if not cleaned_url.startswith(('http://', 'https://')):
                cleaned_url = 'https://' + cleaned_url
            
            # Parse URL
            parsed = urlparse(cleaned_url)
            
            # Check if it's a valid URL structure
            if not parsed.netloc:
                return {
                    "valid": False,
                    "error": "❌ رابط غير صحيح. تأكد من إدخال رابط كامل",
                }
            
            # Check InstaPay domains
            domain_valid = any(domain in parsed.netloc.lower() for domain in cls.INSTAPAY_DOMAINS)
            
            if not domain_valid:
                return {
                    "valid": False,
                    "error": f"❌ رابط إنستاباي غير صحيح. يجب أن يحتوي على أحد النطاقات التالية:\n" +
                            "\n".join([f"• {domain}" for domain in cls.INSTAPAY_DOMAINS]),
                }
            
            # Additional security checks
            security_check = cls._security_validate_url(cleaned_url)
            if not security_check["valid"]:
                return security_check
            
            return {
                "valid": True,
                "cleaned": cleaned_url,
                "formatted": cleaned_url,
                "display": cleaned_url,
                "clickable": f"<code>{cleaned_url}</code>",
                "domain": parsed.netloc,
                "path": parsed.path
            }
            
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return {
                "valid": False,
                "error": "❌ حدث خطأ في التحقق من الرابط"
            }
    
    @classmethod
    def _security_validate_url(cls, url: str) -> Dict[str, Any]:
        """Security validation for URLs"""
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'javascript:',
            r'data:',
            r'file:',
            r'ftp:',
            r'<script',
            r'onclick',
            r'onload'
        ]
        
        url_lower = url.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, url_lower):
                return {
                    "valid": False,
                    "error": "❌ الرابط يحتوي على محتوى مشبوه"
                }
        
        # Check URL length (reasonable limit)
        if len(url) > 500:
            return {
                "valid": False,
                "error": "❌ الرابط طويل جداً"
            }
        
        return {"valid": True}
    
    @classmethod
    def extract_instapay_from_text(cls, text: str) -> List[str]:
        """Extract InstaPay URLs from text"""
        try:
            # Pattern to match URLs containing InstaPay domains
            patterns = []
            for domain in cls.INSTAPAY_DOMAINS:
                patterns.append(rf'https?://[^\s]*{re.escape(domain)}[^\s]*')
            
            found_urls = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                found_urls.extend(matches)
            
            return list(set(found_urls))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting URLs: {e}")
            return []
    
    @classmethod
    def is_valid_url_format(cls, url: str) -> bool:
        """Quick check if URL has valid format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except:
            return False
    
    @classmethod
    def get_instapay_help_message(cls) -> str:
        """Get help message for InstaPay URL format"""
        return f"""💡 <b>كيفية إدخال رابط إنستاباي:</b>

🔹 <b>النطاقات المقبولة:</b>
{chr(10).join([f"   • {domain}" for domain in cls.INSTAPAY_DOMAINS])}

🔹 <b>أمثلة صحيحة:</b>
   • https://instapay.com.eg/abc123
   • https://ipn.eg/xyz789
   • instapay.com.eg/payment/456 (سيتم إضافة https تلقائياً)

🔹 <b>نصائح:</b>
   • انسخ الرابط كاملاً من إنستاباي
   • تأكد من صحة الرابط قبل الإرسال
   • لا تحتاج لإضافة https:// (سيتم إضافتها تلقائياً)

❌ <b>أمثلة خاطئة:</b>
   • روابط من مواقع أخرى
   • روابط غير مكتملة
   • نصوص بدون رابط"""