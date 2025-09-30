# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🔒 FC26 LOCKS - نظام الأقفال والحماية من التضارب             ║
# ║                      Anti-Conflict Lock System                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import asyncio
import time
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from collections import defaultdict

logger = logging.getLogger(__name__)

class UserLockManager:
    """User-specific lock manager to prevent conflicts"""
    
    def __init__(self):
        self.user_locks: Dict[int, asyncio.Lock] = {}
        self.lock_times: Dict[int, float] = {}
        self.lock_counts: Dict[int, int] = defaultdict(int)
        self.active_operations: Dict[int, str] = {}
    
    async def get_user_lock(self, user_id: int) -> asyncio.Lock:
        """Get or create user-specific lock"""
        if user_id not in self.user_locks:
            self.user_locks[user_id] = asyncio.Lock()
            logger.debug(f"🔒 Created new lock for user {user_id}")
        
        return self.user_locks[user_id]
    
    @asynccontextmanager
    async def acquire_user_lock(self, user_id: int, operation: str = "unknown"):
        """Context manager for acquiring user locks"""
        lock = await self.get_user_lock(user_id)
        
        # Check if user is already performing an operation
        if user_id in self.active_operations:
            current_op = self.active_operations[user_id]
            logger.warning(f"⚠️ User {user_id} attempted {operation} while {current_op} is active")
            raise UserBusyException(f"User is currently performing: {current_op}")
        
        start_time = time.time()
        
        try:
            # Acquire lock with timeout
            await asyncio.wait_for(lock.acquire(), timeout=30.0)
            
            # Record operation start
            self.lock_times[user_id] = start_time
            self.lock_counts[user_id] += 1
            self.active_operations[user_id] = operation
            
            logger.debug(f"🔓 Lock acquired for user {user_id} - operation: {operation}")
            
            yield lock
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ Lock acquisition timeout for user {user_id}")
            raise LockTimeoutException(f"Could not acquire lock for user {user_id}")
        
        finally:
            # Release lock and clean up
            if lock.locked():
                lock.release()
            
            # Record operation end
            if user_id in self.active_operations:
                del self.active_operations[user_id]
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.debug(f"🔒 Lock released for user {user_id} - duration: {duration:.2f}s")
    
    def is_user_busy(self, user_id: int) -> bool:
        """Check if user is currently performing an operation"""
        return user_id in self.active_operations
    
    def get_user_operation(self, user_id: int) -> Optional[str]:
        """Get current operation for user"""
        return self.active_operations.get(user_id)
    
    def cleanup_user_locks(self, inactive_minutes: int = 30):
        """Clean up inactive user locks"""
        current_time = time.time()
        inactive_threshold = inactive_minutes * 60
        
        users_to_cleanup = []
        
        for user_id, lock_time in self.lock_times.items():
            if current_time - lock_time > inactive_threshold:
                if user_id not in self.active_operations:
                    users_to_cleanup.append(user_id)
        
        for user_id in users_to_cleanup:
            if user_id in self.user_locks:
                del self.user_locks[user_id]
            if user_id in self.lock_times:
                del self.lock_times[user_id]
            if user_id in self.lock_counts:
                del self.lock_counts[user_id]
            
            logger.info(f"🧹 Cleaned up inactive lock for user {user_id}")
        
        return len(users_to_cleanup)
    
    def get_lock_statistics(self) -> Dict[str, Any]:
        """Get lock usage statistics"""
        return {
            'active_locks': len(self.active_operations),
            'total_locks_created': len(self.user_locks),
            'lock_usage_counts': dict(self.lock_counts),
            'active_operations': dict(self.active_operations)
        }

class MessageLockManager:
    """Message-specific lock manager for preventing message conflicts"""
    
    def __init__(self):
        self.active_messages: Dict[int, int] = {}  # user_id -> message_id
        self.message_locks: Dict[int, asyncio.Lock] = {}
    
    async def set_active_message(self, user_id: int, message_id: int):
        """Set active message for user"""
        async with await self._get_message_lock(user_id):
            old_message_id = self.active_messages.get(user_id)
            self.active_messages[user_id] = message_id
            
            logger.debug(f"📱 Active message updated for user {user_id}: {old_message_id} -> {message_id}")
            
            return old_message_id
    
    async def get_active_message(self, user_id: int) -> Optional[int]:
        """Get active message ID for user"""
        return self.active_messages.get(user_id)
    
    async def clear_active_message(self, user_id: int) -> Optional[int]:
        """Clear active message for user"""
        async with await self._get_message_lock(user_id):
            old_message_id = self.active_messages.pop(user_id, None)
            logger.debug(f"🗑️ Cleared active message for user {user_id}: {old_message_id}")
            return old_message_id
    
    async def _get_message_lock(self, user_id: int) -> asyncio.Lock:
        """Get message lock for user"""
        if user_id not in self.message_locks:
            self.message_locks[user_id] = asyncio.Lock()
        return self.message_locks[user_id]

class RateLimitManager:
    """Rate limiting manager to prevent spam and abuse"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.user_requests: Dict[int, list] = defaultdict(list)
    
    def is_rate_limited(self, user_id: int) -> bool:
        """Check if user is rate limited"""
        current_time = time.time()
        
        # Clean old requests
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if current_time - req_time < self.time_window
        ]
        
        # Check rate limit
        if len(self.user_requests[user_id]) >= self.max_requests:
            logger.warning(f"🚫 Rate limit exceeded for user {user_id}")
            return True
        
        # Record new request
        self.user_requests[user_id].append(current_time)
        return False
    
    def get_remaining_requests(self, user_id: int) -> int:
        """Get remaining requests for user"""
        current_requests = len(self.user_requests[user_id])
        return max(0, self.max_requests - current_requests)

# Custom Exceptions
class UserBusyException(Exception):
    """Raised when user is busy with another operation"""
    pass

class LockTimeoutException(Exception):
    """Raised when lock acquisition times out"""
    pass

# Global instances
user_lock_manager = UserLockManager()
message_lock_manager = MessageLockManager()
rate_limit_manager = RateLimitManager()

# Convenience functions
async def get_user_lock(user_id: int) -> asyncio.Lock:
    """Get user lock - backwards compatibility"""
    return await user_lock_manager.get_user_lock(user_id)

async def acquire_user_lock(user_id: int, operation: str = "unknown"):
    """Acquire user lock with context manager"""
    return user_lock_manager.acquire_user_lock(user_id, operation)

def is_user_busy(user_id: int) -> bool:
    """Check if user is busy"""
    return user_lock_manager.is_user_busy(user_id)

def is_rate_limited(user_id: int) -> bool:
    """Check rate limit"""
    return rate_limit_manager.is_rate_limited(user_id)