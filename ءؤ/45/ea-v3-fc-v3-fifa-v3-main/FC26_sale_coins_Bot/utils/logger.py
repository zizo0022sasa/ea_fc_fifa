# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              📝 FC26 LOGGER - نظام السجلات                               ║
# ║                         Logging System                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from config import LOGGING_CONFIG

class FC26Logger:
    """Enhanced logging system for FC26 Bot"""
    
    def __init__(self):
        self.logger = None
        self.setup_logger()
    
    def setup_logger(self):
        """Setup comprehensive logging system"""
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(LOGGING_CONFIG['file'])
        os.makedirs(log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('FC26_Bot')
        self.logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler only (no file logging)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            LOGGING_CONFIG['format'],
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set formatters
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        
        # Initial log
        self.logger.info("🚀 FC26 Bot Logger initialized successfully")
    
    def log_user_action(self, user_id: int, action: str, details: str = None):
        """Log user actions"""
        log_message = f"👤 User {user_id}: {action}"
        if details:
            log_message += f" | Details: {details}"
        self.logger.info(log_message)
    
    def log_registration_step(self, user_id: int, step: str, success: bool = True):
        """Log registration steps"""
        status = "✅" if success else "❌"
        self.logger.info(f"{status} User {user_id} registration step: {step}")
    
    def log_validation_error(self, user_id: int, field: str, error: str):
        """Log validation errors"""
        self.logger.warning(f"⚠️ Validation error - User {user_id}, Field: {field}, Error: {error}")
    
    def log_database_operation(self, operation: str, user_id: int = None, success: bool = True):
        """Log database operations"""
        status = "✅" if success else "❌"
        user_info = f"User {user_id}" if user_id else "System"
        self.logger.info(f"{status} DB Operation: {operation} | {user_info}")
    
    def log_security_event(self, user_id: int, event: str, details: str = None):
        """Log security-related events"""
        log_message = f"🛡️ SECURITY: User {user_id} - {event}"
        if details:
            log_message += f" | Details: {details}"
        self.logger.warning(log_message)
    
    def log_performance_metric(self, operation: str, duration: float, user_id: int = None):
        """Log performance metrics"""
        user_info = f"User {user_id}" if user_id else "System"
        self.logger.info(f"📊 Performance: {operation} took {duration:.2f}s | {user_info}")
    
    def log_bot_start(self):
        """Log bot startup"""
        self.logger.info("="*60)
        self.logger.info("🎮 FC26 Gaming Bot Starting...")
        self.logger.info(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*60)
    
    def log_bot_stop(self):
        """Log bot shutdown"""
        self.logger.info("="*60)
        self.logger.info("🔴 FC26 Gaming Bot Shutting Down...")
        self.logger.info(f"⏰ Stop Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*60)
    
    def log_error_with_context(self, error: Exception, context: str, user_id: int = None):
        """Log errors with context"""
        user_info = f" | User {user_id}" if user_id else ""
        self.logger.error(f"❌ Error in {context}: {str(error)}{user_info}", exc_info=True)
    
    def get_logger(self):
        """Get the logger instance"""
        return self.logger

# Global logger instance
fc26_logger = FC26Logger()
logger = fc26_logger.get_logger()

# Convenience functions for easy logging
def log_user_action(user_id: int, action: str, details: str = None):
    fc26_logger.log_user_action(user_id, action, details)

def log_registration_step(user_id: int, step: str, success: bool = True):
    fc26_logger.log_registration_step(user_id, step, success)

def log_validation_error(user_id: int, field: str, error: str):
    fc26_logger.log_validation_error(user_id, field, error)

def log_database_operation(operation: str, user_id: int = None, success: bool = True):
    fc26_logger.log_database_operation(operation, user_id, success)

def log_security_event(user_id: int, event: str, details: str = None):
    fc26_logger.log_security_event(user_id, event, details)

def log_performance_metric(operation: str, duration: float, user_id: int = None):
    fc26_logger.log_performance_metric(operation, duration, user_id)

def log_error_with_context(error: Exception, context: str, user_id: int = None):
    fc26_logger.log_error_with_context(error, context, user_id)