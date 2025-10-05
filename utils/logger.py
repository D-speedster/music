import logging
import os
import sys
from datetime import datetime
from typing import Optional
from config import Config

class MusicBotLogger:
    """سیستم لاگ گیری حرفه‌ای برای ربات موزیک"""
    
    def __init__(self, name: str = "MusicBot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # جلوگیری از تکرار handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """تنظیم handlers برای لاگ گیری"""
        
        # فرمت لاگ
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        file_handler = logging.FileHandler(
            f'logs/music_bot_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler(
            f'logs/music_bot_errors_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, **kwargs):
        """لاگ سطح DEBUG"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def info(self, message: str, **kwargs):
        """لاگ سطح INFO"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """لاگ سطح WARNING"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs):
        """لاگ سطح ERROR"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs):
        """لاگ سطح CRITICAL"""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def _format_message(self, message: str, **kwargs) -> str:
        """فرمت کردن پیام لاگ با اطلاعات اضافی"""
        if kwargs:
            extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | {extra_info}"
        return message
    
    def log_file_processing_start(self, user_id: int, file_name: str, file_size: int, file_type: str):
        """لاگ شروع پردازش فایل"""
        self.info(
            "شروع پردازش فایل",
            user_id=user_id,
            file_name=file_name,
            file_size_mb=round(file_size / (1024*1024), 2),
            file_type=file_type
        )
    
    def log_file_download_start(self, file_id: str, file_size: int, method: str):
        """لاگ شروع دانلود فایل"""
        self.info(
            "شروع دانلود فایل",
            file_id=file_id,
            file_size_mb=round(file_size / (1024*1024), 2),
            download_method=method
        )
    
    def log_file_download_success(self, file_path: str, actual_size: int):
        """لاگ موفقیت دانلود فایل"""
        self.info(
            "دانلود فایل موفق",
            file_path=file_path,
            actual_size_mb=round(actual_size / (1024*1024), 2)
        )
    
    def log_file_download_error(self, error: Exception, file_id: str):
        """لاگ خطا در دانلود فایل"""
        self.error(
            f"خطا در دانلود فایل: {str(error)}",
            file_id=file_id,
            error_type=type(error).__name__
        )
    
    def log_audio_processing_start(self, file_path: str):
        """لاگ شروع پردازش صوتی"""
        self.info("شروع پردازش صوتی", file_path=file_path)
    
    def log_audio_processing_success(self, file_path: str, metadata: dict):
        """لاگ موفقیت پردازش صوتی"""
        self.info(
            "پردازش صوتی موفق",
            file_path=file_path,
            duration=metadata.get('duration'),
            bitrate=metadata.get('bitrate'),
            format=metadata.get('format')
        )
    
    def log_delivery_method(self, method: str, file_size: int, reason: str):
        """لاگ روش ارسال فایل"""
        self.info(
            f"انتخاب روش ارسال: {method}",
            file_size_mb=round(file_size / (1024*1024), 2),
            reason=reason
        )
    
    def log_user_limit_check(self, user_id: int, allowed: bool, reason: Optional[str] = None):
        """لاگ بررسی محدودیت کاربر"""
        self.info(
            "بررسی محدودیت کاربر",
            user_id=user_id,
            allowed=allowed,
            reason=reason or "مجاز"
        )

# Instance سراسری
logger = MusicBotLogger()