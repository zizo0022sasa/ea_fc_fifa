# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              📋 FC26 DATABASE MODELS - نماذج قاعدة البيانات             ║
# ║                        Database Table Schemas                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from database.connection import db
import logging

logger = logging.getLogger(__name__)

class DatabaseModels:
    """Database table creation and schema management"""
    
    @staticmethod
    def create_all_tables():
        """Create all required database tables"""
        try:
            # Create users table
            db.execute_update("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    platform TEXT,
                    whatsapp TEXT,
                    payment_method TEXT,
                    payment_details TEXT,
                    registration_step TEXT DEFAULT 'start',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create registration_log table for tracking
            db.execute_update("""
                CREATE TABLE IF NOT EXISTS registration_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER,
                    step TEXT,
                    data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
                )
            """)
            
            # Create error_log table
            db.execute_update("""
                CREATE TABLE IF NOT EXISTS error_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER,
                    error_type TEXT,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create statistics table
            db.execute_update("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    metric_name TEXT,
                    metric_value INTEGER DEFAULT 0,
                    UNIQUE(date, metric_name)
                )
            """)
            
            logger.info("✅ All database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating database tables: {e}")
            return False
    
    @staticmethod
    def drop_all_tables():
        """Drop all tables (use with caution!)"""
        tables = ['users', 'registration_log', 'error_log', 'statistics']
        try:
            for table in tables:
                db.execute_update(f"DROP TABLE IF EXISTS {table}")
            logger.info("⚠️ All database tables dropped")
            return True
        except Exception as e:
            logger.error(f"❌ Error dropping tables: {e}")
            return False
    
    @staticmethod
    def get_table_info():
        """Get information about all tables"""
        try:
            tables_info = {}
            
            # Get all tables
            tables = db.execute_query("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            
            for table in tables:
                table_name = table[0]
                
                # Get table schema
                schema = db.execute_query(f"PRAGMA table_info({table_name})")
                
                # Get row count
                count = db.execute_query(f"SELECT COUNT(*) FROM {table_name}")[0][0]
                
                tables_info[table_name] = {
                    'columns': [col[1] for col in schema],
                    'row_count': count
                }
            
            return tables_info
            
        except Exception as e:
            logger.error(f"❌ Error getting table info: {e}")
            return {}

# Initialize database on import
if __name__ != "__main__":
    DatabaseModels.create_all_tables()