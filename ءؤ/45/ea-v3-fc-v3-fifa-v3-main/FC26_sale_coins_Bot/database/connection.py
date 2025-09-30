# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              💾 FC26 DATABASE CONNECTION - اتصال قاعدة البيانات          ║
# ║                     Database Connection Management                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import sqlite3
import logging
import os
from typing import Optional
from contextlib import contextmanager
from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection manager with proper error handling"""
    
    def __init__(self):
        self.db_path = os.path.join(DATABASE_CONFIG['path'], DATABASE_CONFIG['name'])
        self._ensure_database_directory()
    
    def _ensure_database_directory(self):
        """Ensure database directory exists"""
        os.makedirs(DATABASE_CONFIG['path'], exist_ok=True)
        if DATABASE_CONFIG.get('backup_path'):
            os.makedirs(DATABASE_CONFIG['backup_path'], exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> Optional[list]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_script(self, script: str):
        """Execute multiple SQL statements"""
        with self.get_connection() as conn:
            conn.executescript(script)
            conn.commit()

# Global database instance
db = DatabaseConnection()