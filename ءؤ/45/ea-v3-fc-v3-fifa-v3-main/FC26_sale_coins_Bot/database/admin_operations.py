# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🎯 FC26 ADMIN DATABASE OPERATIONS - عمليات قاعدة بيانات الادمن  ║
# ║                     Admin Database Management                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import sqlite3
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = logging.getLogger(__name__)

class AdminOperations:
    """عمليات قاعدة البيانات للادمن"""
    
    DB_NAME = "fc26_admin.db"
    
    # 🔥 Thread-safe database executor - ONLY ONE worker to prevent locks
    # This ensures all database operations are serialized (one at a time)
    _db_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="AdminDB")
    
    @classmethod
    def init_admin_db(cls):
        """تهيئة قاعدة بيانات الادمن"""
        conn = sqlite3.connect(cls.DB_NAME)
        cursor = conn.cursor()
        
        # جدول أسعار بيع الكوينز
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coin_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                transfer_type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                price INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, transfer_type, amount)
            )
        ''')
        
        # جدول سجل تعديلات الادمن
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # إدراج الأسعار الافتراضية
        cls._insert_default_prices(cursor)
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Admin database initialized successfully")
    
    @classmethod
    def _insert_default_prices(cls, cursor):
        """إدراج الأسعار الافتراضية"""
        default_prices = [
            # PlayStation - Normal
            ('playstation', 'normal', 1000000, 5600),
            # PlayStation - Instant  
            ('playstation', 'instant', 1000000, 5300),
            # Xbox - Normal
            ('xbox', 'normal', 1000000, 5600),
            # Xbox - Instant
            ('xbox', 'instant', 1000000, 5300),
            # PC - Normal
            ('pc', 'normal', 1000000, 6100),
            # PC - Instant
            ('pc', 'instant', 1000000, 5800),
        ]
        
        for platform, transfer_type, amount, price in default_prices:
            cursor.execute('''
                INSERT OR IGNORE INTO coin_prices 
                (platform, transfer_type, amount, price) 
                VALUES (?, ?, ?, ?)
            ''', (platform, transfer_type, amount, price))
    
    @classmethod
    def get_price(cls, platform: str, transfer_type: str, amount: int) -> Optional[int]:
        """جلب السعر من قاعدة البيانات"""
        conn = sqlite3.connect(cls.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT price FROM coin_prices 
            WHERE platform = ? AND transfer_type = ? AND amount = ?
        ''', (platform, transfer_type, amount))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    @classmethod
    def _update_price_sync(cls, platform: str, transfer_type: str, amount: int, new_price: int, admin_id: int) -> bool:
        """تحديث السعر في قاعدة البيانات - النسخة المتزامنة الداخلية"""
        conn = None
        try:
            # Enable WAL mode for better concurrency
            conn = sqlite3.connect(cls.DB_NAME, timeout=30.0)
            conn.execute('PRAGMA journal_mode=WAL')
            cursor = conn.cursor()
            
            print(f"🔄 [DB] Starting price update: {platform} {transfer_type} -> {new_price}")
            
            # جلب السعر القديم
            cursor.execute('''
                SELECT price FROM coin_prices 
                WHERE platform = ? AND transfer_type = ? AND amount = ?
            ''', (platform, transfer_type, amount))
            result = cursor.fetchone()
            old_price = result[0] if result else None
            
            print(f"💰 [DB] Old price: {old_price}, New price: {new_price}")
            
            # تحديث السعر
            cursor.execute('''
                INSERT OR REPLACE INTO coin_prices 
                (platform, transfer_type, amount, price, updated_at) 
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (platform, transfer_type, amount, new_price))
            
            # تسجيل العملية في السجل
            details = f"Platform: {platform}, Type: {transfer_type}, Amount: {amount}, Old: {old_price}, New: {new_price}"
            cursor.execute('''
                INSERT INTO admin_logs (admin_id, action, details) 
                VALUES (?, ?, ?)
            ''', (admin_id, "UPDATE_PRICE", details))
            
            conn.commit()
            print(f"✅ [DB] Price updated successfully: {platform} {transfer_type} {amount} -> {new_price}")
            logger.info(f"✅ Price updated: {platform} {transfer_type} {amount} -> {new_price}")
            return True
            
        except Exception as e:
            print(f"❌ [DB] Failed to update price: {e}")
            logger.error(f"❌ Failed to update price: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
                print(f"🔒 [DB] Connection closed")
    
    @classmethod
    async def update_price(cls, platform: str, transfer_type: str, amount: int, new_price: int, admin_id: int) -> bool:
        """تحديث السعر في قاعدة البيانات - Thread-safe version"""
        print(f"📝 [DB-EXECUTOR] Submitting price update task to database executor")
        loop = asyncio.get_event_loop()
        
        # Run database operation in dedicated thread pool
        result = await loop.run_in_executor(
            cls._db_executor,
            cls._update_price_sync,
            platform, transfer_type, amount, new_price, admin_id
        )
        
        print(f"✅ [DB-EXECUTOR] Price update task completed: {result}")
        return result
    
    @classmethod
    def get_all_prices(cls) -> List[Dict]:
        """جلب جميع الأسعار"""
        conn = sqlite3.connect(cls.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT platform, transfer_type, amount, price, updated_at 
            FROM coin_prices 
            ORDER BY platform, transfer_type, amount
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        prices = []
        for row in results:
            prices.append({
                'platform': row[0],
                'transfer_type': row[1], 
                'amount': row[2],
                'price': row[3],
                'updated_at': row[4]
            })
        
        return prices
    
    @classmethod
    def log_admin_action(cls, admin_id: int, action: str, details: str = ""):
        """تسجيل عمل الادمن"""
        conn = sqlite3.connect(cls.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO admin_logs (admin_id, action, details) 
            VALUES (?, ?, ?)
        ''', (admin_id, action, details))
        
        conn.commit()
        conn.close()
    
    @classmethod
    def get_admin_logs(cls, limit: int = 50) -> List[Dict]:
        """جلب سجل أعمال الادمن"""
        conn = sqlite3.connect(cls.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT admin_id, action, details, timestamp 
            FROM admin_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in results:
            logs.append({
                'admin_id': row[0],
                'action': row[1],
                'details': row[2],
                'timestamp': row[3]
            })
        
        return logs
    
    @classmethod
    def get_current_timestamp(cls) -> str:
        """جلب الوقت الحالي"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')