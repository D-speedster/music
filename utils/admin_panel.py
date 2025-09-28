import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import asyncio

@dataclass
class UserStats:
    """User statistics data class"""
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    files_processed: int
    total_file_size: int  # in bytes
    last_activity: datetime
    join_date: datetime
    is_banned: bool = False
    daily_limit_used: int = 0
    last_reset_date: str = ""

@dataclass
class SystemStats:
    """System statistics data class"""
    total_users: int
    total_files_processed: int
    total_data_processed: int  # in bytes
    active_users_today: int
    active_users_week: int
    average_file_size: float
    most_popular_format: str
    uptime_start: datetime

class AdminPanel:
    """Admin panel for managing bot statistics and user limits"""
    
    def __init__(self, db_path: str = "bot_data.db"):
        self.db_path = db_path
        self.init_database()
        
        # Default limits
        from config import Config
        self.default_limits = {
            'max_file_size': Config.MAX_FILE_SIZE_BYTES,  # Use config value
            'daily_file_limit': 20,
            'max_batch_size': 10,
            'banned_users': set()
        }
        
        # Load custom limits
        self.limits = self.load_limits()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    files_processed INTEGER DEFAULT 0,
                    total_file_size INTEGER DEFAULT 0,
                    last_activity TEXT,
                    join_date TEXT,
                    is_banned INTEGER DEFAULT 0,
                    daily_limit_used INTEGER DEFAULT 0,
                    last_reset_date TEXT DEFAULT ''
                )
            ''')
            
            # File processing logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    file_name TEXT,
                    file_size INTEGER,
                    file_format TEXT,
                    operations TEXT,
                    processing_time REAL,
                    timestamp TEXT,
                    success INTEGER DEFAULT 1
                )
            ''')
            
            # System settings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # Bot statistics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INTEGER PRIMARY KEY,
                    uptime_start TEXT,
                    total_commands INTEGER DEFAULT 0,
                    total_errors INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
    
    def load_limits(self) -> Dict[str, Any]:
        """Load custom limits from database"""
        limits = self.default_limits.copy()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings WHERE key LIKE 'limit_%'")
                
                for key, value in cursor.fetchall():
                    setting_name = key.replace('limit_', '')
                    if setting_name in ['max_file_size', 'daily_file_limit', 'max_batch_size']:
                        limits[setting_name] = int(value)
                    elif setting_name == 'banned_users':
                        limits['banned_users'] = set(json.loads(value))
        except Exception as e:
            print(f"Error loading limits: {e}")
        
        return limits
    
    def save_limits(self):
        """Save current limits to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for key, value in self.limits.items():
                    if key == 'banned_users':
                        value = json.dumps(list(value))
                    
                    cursor.execute(
                        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                        (f"limit_{key}", str(value))
                    )
                
                conn.commit()
        except Exception as e:
            print(f"Error saving limits: {e}")
    
    async def log_user_activity(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None
    ):
        """Log user activity and update user stats"""
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            user_exists = cursor.fetchone()
            
            if user_exists:
                # Update existing user
                cursor.execute('''
                    UPDATE users 
                    SET username = ?, first_name = ?, last_activity = ?
                    WHERE user_id = ?
                ''', (username, first_name, now, user_id))
            else:
                # Create new user
                cursor.execute('''
                    INSERT INTO users 
                    (user_id, username, first_name, last_activity, join_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, username, first_name, now, now))
            
            conn.commit()
    
    async def log_file_processing(
        self,
        user_id: int,
        file_name: str,
        file_size: int,
        file_format: str,
        operations: List[str],
        processing_time: float,
        success: bool = True
    ):
        """Log file processing activity"""
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Log file processing
            cursor.execute('''
                INSERT INTO file_logs 
                (user_id, file_name, file_size, file_format, operations, 
                 processing_time, timestamp, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, file_name, file_size, file_format,
                json.dumps(operations), processing_time, now, int(success)
            ))
            
            # Update user stats
            cursor.execute('''
                UPDATE users 
                SET files_processed = files_processed + 1,
                    total_file_size = total_file_size + ?,
                    daily_limit_used = daily_limit_used + 1,
                    last_activity = ?
                WHERE user_id = ?
            ''', (file_size, now, user_id))
            
            conn.commit()
    
    def check_user_limits(self, user_id: int, file_size: int) -> Dict[str, Any]:
        """Check if user can process a file based on current limits"""
        result = {
            'allowed': True,
            'reason': '',
            'limits': {
                'daily_remaining': 0,
                'max_file_size': self.limits['max_file_size']
            }
        }
        
        # Check if user is banned
        if user_id in self.limits['banned_users']:
            result['allowed'] = False
            result['reason'] = 'کاربر مسدود شده است'
            return result
        
        # Check file size limit
        if file_size > self.limits['max_file_size']:
            result['allowed'] = False
            result['reason'] = f'حجم فایل بیش از حد مجاز ({self.limits["max_file_size"] // (1024*1024)} MB)'
            return result
        
        # Check daily limit
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT daily_limit_used, last_reset_date 
                FROM users WHERE user_id = ?
            ''', (user_id,))
            
            user_data = cursor.fetchone()
            if user_data:
                daily_used, last_reset = user_data
                today = datetime.now().strftime('%Y-%m-%d')
                
                # Reset daily counter if it's a new day
                if last_reset != today:
                    cursor.execute('''
                        UPDATE users 
                        SET daily_limit_used = 0, last_reset_date = ?
                        WHERE user_id = ?
                    ''', (today, user_id))
                    daily_used = 0
                    conn.commit()
                
                # Check daily limit
                if daily_used >= self.limits['daily_file_limit']:
                    result['allowed'] = False
                    result['reason'] = f'محدودیت روزانه ({self.limits["daily_file_limit"]} فایل) به پایان رسیده'
                    return result
                
                result['limits']['daily_remaining'] = self.limits['daily_file_limit'] - daily_used
        
        return result
    
    def get_user_stats(self, user_id: int) -> Optional[UserStats]:
        """Get statistics for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, username, first_name, files_processed, 
                       total_file_size, last_activity, join_date, is_banned,
                       daily_limit_used, last_reset_date
                FROM users WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row:
                return UserStats(
                    user_id=row[0],
                    username=row[1],
                    first_name=row[2],
                    files_processed=row[3],
                    total_file_size=row[4],
                    last_activity=datetime.fromisoformat(row[5]),
                    join_date=datetime.fromisoformat(row[6]),
                    is_banned=bool(row[7]),
                    daily_limit_used=row[8],
                    last_reset_date=row[9]
                )
        return None
    
    def get_system_stats(self) -> SystemStats:
        """Get overall system statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total users
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # Total files processed
            cursor.execute("SELECT COUNT(*), SUM(file_size) FROM file_logs WHERE success = 1")
            files_data = cursor.fetchone()
            total_files = files_data[0] or 0
            total_size = files_data[1] or 0
            
            # Active users today
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM file_logs 
                WHERE DATE(timestamp) = ?
            ''', (today,))
            active_today = cursor.fetchone()[0]
            
            # Active users this week
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM file_logs 
                WHERE DATE(timestamp) >= ?
            ''', (week_ago,))
            active_week = cursor.fetchone()[0]
            
            # Average file size
            cursor.execute("SELECT AVG(file_size) FROM file_logs WHERE success = 1")
            avg_size = cursor.fetchone()[0] or 0
            
            # Most popular format
            cursor.execute('''
                SELECT file_format, COUNT(*) as count 
                FROM file_logs WHERE success = 1
                GROUP BY file_format 
                ORDER BY count DESC 
                LIMIT 1
            ''')
            popular_format = cursor.fetchone()
            most_popular = popular_format[0] if popular_format else 'N/A'
            
            return SystemStats(
                total_users=total_users,
                total_files_processed=total_files,
                total_data_processed=total_size,
                active_users_today=active_today,
                active_users_week=active_week,
                average_file_size=avg_size,
                most_popular_format=most_popular,
                uptime_start=datetime.now()  # This should be loaded from settings
            )
    
    def get_top_users(self, limit: int = 10) -> List[UserStats]:
        """Get top users by files processed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, username, first_name, files_processed, 
                       total_file_size, last_activity, join_date, is_banned,
                       daily_limit_used, last_reset_date
                FROM users 
                ORDER BY files_processed DESC 
                LIMIT ?
            ''', (limit,))
            
            users = []
            for row in cursor.fetchall():
                users.append(UserStats(
                    user_id=row[0],
                    username=row[1],
                    first_name=row[2],
                    files_processed=row[3],
                    total_file_size=row[4],
                    last_activity=datetime.fromisoformat(row[5]),
                    join_date=datetime.fromisoformat(row[6]),
                    is_banned=bool(row[7]),
                    daily_limit_used=row[8],
                    last_reset_date=row[9]
                ))
            
            return users
    
    def ban_user(self, user_id: int) -> bool:
        """Ban a user"""
        try:
            self.limits['banned_users'].add(user_id)
            self.save_limits()
            
            # Update user record
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET is_banned = 1 WHERE user_id = ?",
                    (user_id,)
                )
                conn.commit()
            
            return True
        except Exception as e:
            print(f"Error banning user: {e}")
            return False
    
    def unban_user(self, user_id: int) -> bool:
        """Unban a user"""
        try:
            self.limits['banned_users'].discard(user_id)
            self.save_limits()
            
            # Update user record
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET is_banned = 0 WHERE user_id = ?",
                    (user_id,)
                )
                conn.commit()
            
            return True
        except Exception as e:
            print(f"Error unbanning user: {e}")
            return False
    
    def update_limits(self, **kwargs) -> bool:
        """Update system limits"""
        try:
            for key, value in kwargs.items():
                if key in self.limits:
                    self.limits[key] = value
            
            self.save_limits()
            return True
        except Exception as e:
            print(f"Error updating limits: {e}")
            return False
    
    def get_recent_activity(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent file processing activity"""
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fl.*, u.username, u.first_name
                FROM file_logs fl
                LEFT JOIN users u ON fl.user_id = u.user_id
                WHERE fl.timestamp >= ?
                ORDER BY fl.timestamp DESC
                LIMIT 100
            ''', (since,))
            
            activities = []
            for row in cursor.fetchall():
                activities.append({
                    'id': row[0],
                    'user_id': row[1],
                    'username': row[9],
                    'first_name': row[10],
                    'file_name': row[2],
                    'file_size': row[3],
                    'file_format': row[4],
                    'operations': json.loads(row[5]),
                    'processing_time': row[6],
                    'timestamp': row[7],
                    'success': bool(row[8])
                })
            
            return activities
    
    def export_stats(self) -> Dict[str, Any]:
        """Export all statistics as JSON"""
        system_stats = self.get_system_stats()
        top_users = self.get_top_users(20)
        recent_activity = self.get_recent_activity(168)  # Last week
        
        return {
            'export_date': datetime.now().isoformat(),
            'system_stats': asdict(system_stats),
            'top_users': [asdict(user) for user in top_users],
            'recent_activity': recent_activity,
            'current_limits': self.limits.copy()
        }