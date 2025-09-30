# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🔧 FC26 DATABASE OPERATIONS - عمليات قاعدة البيانات        ║
# ║                     Database CRUD Operations                             ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import logging
from typing import Dict, Optional, List
from datetime import datetime
from database.connection import db

logger = logging.getLogger(__name__)

class UserOperations:
    """User-related database operations"""
    
    @staticmethod
    def save_user_step(user_id: int, step: str, data: Dict = None) -> bool:
        """Save user registration step and data"""
        try:
            # Check if user exists
            existing = db.execute_query(
                "SELECT telegram_id FROM users WHERE telegram_id = ?", (user_id,)
            )
            
            if existing:
                # Update existing user
                query = "UPDATE users SET registration_step = ?, updated_at = CURRENT_TIMESTAMP"
                params = [step, user_id]
                
                if data:
                    for key, value in data.items():
                        if key in ['platform', 'whatsapp', 'payment_method', 'payment_details']:
                            query += f", {key} = ?"
                            params.insert(-1, value)
                
                query += " WHERE telegram_id = ?"
                db.execute_update(query, tuple(params))
                
            else:
                # Insert new user
                platform = data.get('platform') if data else None
                whatsapp = data.get('whatsapp') if data else None
                payment_method = data.get('payment_method') if data else None
                payment_details = data.get('payment_details') if data else None
                
                db.execute_update("""
                    INSERT INTO users (telegram_id, platform, whatsapp, payment_method, payment_details, registration_step)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, platform, whatsapp, payment_method, payment_details, step))
            
            # Log the step
            RegistrationOperations.log_step(user_id, step, str(data) if data else None)
            
            logger.info(f"✅ Step saved for user {user_id}: {step}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving user step: {e}")
            return False
    
    @staticmethod
    def get_user_data(user_id: int) -> Optional[Dict]:
        """Get user data from database"""
        try:
            result = db.execute_query("""
                SELECT telegram_id, platform, whatsapp, payment_method, 
                       payment_details, registration_step, created_at, updated_at
                FROM users WHERE telegram_id = ?
            """, (user_id,))
            
            if result:
                row = result[0]
                return {
                    "telegram_id": row[0],
                    "platform": row[1],
                    "whatsapp": row[2],
                    "payment_method": row[3],
                    "payment_details": row[4],
                    "registration_step": row[5],
                    "created_at": row[6],
                    "updated_at": row[7]
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting user data: {e}")
            return None
    
    @staticmethod
    def user_exists(user_id: int) -> bool:
        """Check if user exists in database"""
        try:
            result = db.execute_query(
                "SELECT telegram_id FROM users WHERE telegram_id = ?", (user_id,)
            )
            return len(result) > 0
        except Exception as e:
            logger.error(f"❌ Error checking user existence: {e}")
            return False
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete user and related data"""
        try:
            # Delete user data
            affected = db.execute_update("DELETE FROM users WHERE telegram_id = ?", (user_id,))
            
            # Delete registration logs
            db.execute_update("DELETE FROM registration_log WHERE telegram_id = ?", (user_id,))
            
            if affected > 0:
                logger.info(f"✅ User {user_id} deleted successfully")
                return True
            else:
                logger.warning(f"⚠️ User {user_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting user: {e}")
            return False
    
    @staticmethod
    def update_user_field(user_id: int, field: str, value: str) -> bool:
        """Update specific field for user"""
        allowed_fields = {'platform', 'whatsapp', 'payment_method', 'payment_details', 'registration_step'}
        
        if field not in allowed_fields:
            logger.error(f"❌ Invalid field name: {field}")
            return False
        
        try:
            affected = db.execute_update(
                f"UPDATE users SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
                (value, user_id)
            )
            
            if affected > 0:
                logger.info(f"✅ Field {field} updated for user {user_id}")
                return True
            else:
                logger.warning(f"⚠️ User {user_id} not found for field update")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating user field: {e}")
            return False

class RegistrationOperations:
    """Registration tracking operations"""
    
    @staticmethod
    def log_step(user_id: int, step: str, data: str = None) -> bool:
        """Log registration step"""
        try:
            db.execute_update("""
                INSERT INTO registration_log (telegram_id, step, data)
                VALUES (?, ?, ?)
            """, (user_id, step, data))
            return True
        except Exception as e:
            logger.error(f"❌ Error logging registration step: {e}")
            return False
    
    @staticmethod
    def get_user_registration_history(user_id: int) -> List[Dict]:
        """Get user's registration history"""
        try:
            result = db.execute_query("""
                SELECT step, data, timestamp 
                FROM registration_log 
                WHERE telegram_id = ? 
                ORDER BY timestamp DESC
            """, (user_id,))
            
            return [{"step": row[0], "data": row[1], "timestamp": row[2]} for row in result]
        except Exception as e:
            logger.error(f"❌ Error getting registration history: {e}")
            return []

class StatisticsOperations:
    """Statistics and analytics operations"""
    
    @staticmethod
    def get_users_count() -> int:
        """Get total number of users"""
        try:
            result = db.execute_query("SELECT COUNT(*) FROM users")
            return result[0][0] if result else 0
        except Exception as e:
            logger.error(f"❌ Error getting users count: {e}")
            return 0
    
    @staticmethod
    def get_completed_registrations() -> int:
        """Get number of completed registrations"""
        try:
            result = db.execute_query(
                "SELECT COUNT(*) FROM users WHERE registration_step = 'completed'"
            )
            return result[0][0] if result else 0
        except Exception as e:
            logger.error(f"❌ Error getting completed registrations: {e}")
            return 0
    
    @staticmethod
    def update_daily_metric(metric_name: str, value: int = 1) -> bool:
        """Update daily metric"""
        try:
            # Try to update existing record
            affected = db.execute_update("""
                UPDATE statistics 
                SET metric_value = metric_value + ? 
                WHERE date = CURRENT_DATE AND metric_name = ?
            """, (value, metric_name))
            
            # If no record exists, create new one
            if affected == 0:
                db.execute_update("""
                    INSERT INTO statistics (metric_name, metric_value)
                    VALUES (?, ?)
                """, (metric_name, value))
            
            return True
        except Exception as e:
            logger.error(f"❌ Error updating daily metric: {e}")
            return False

class ErrorOperations:
    """Error logging operations"""
    
    @staticmethod
    def log_error(user_id: int, error_type: str, error_message: str) -> bool:
        """Log error to database"""
        try:
            db.execute_update("""
                INSERT INTO error_log (telegram_id, error_type, error_message)
                VALUES (?, ?, ?)
            """, (user_id, error_type, error_message))
            return True
        except Exception as e:
            logger.error(f"❌ Error logging error: {e}")
            return False