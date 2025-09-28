#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تست عملکرد ربات موزیک تلگرام
"""

import os
import sys
import asyncio
import tempfile
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.audio_processor import AudioProcessor
from utils.batch_processor import BatchProcessor
from utils.admin_panel import AdminPanel
from config import Config

class BotTester:
    """کلاس تست عملکرد ربات"""
    
    def __init__(self):
        self.config = Config()
        self.audio_processor = AudioProcessor()
        self.batch_processor = BatchProcessor()
        self.admin_panel = AdminPanel()
        
    async def test_audio_processor(self):
        """تست پردازشگر صوتی"""
        print("🎵 تست پردازشگر صوتی...")
        
        # تست فرمت‌های پشتیبانی شده
        supported_formats = self.audio_processor.get_supported_formats()
        print(f"✅ فرمت‌های پشتیبانی شده: {supported_formats}")
        
        # تست قالب‌های نام‌گذاری
        metadata = {
            'title': 'نمونه آهنگ',
            'artist': 'هنرمند نمونه',
            'album': 'آلبوم نمونه',
            'year': '2024'
        }
        
        templates = [
            '{artist} - {title}',
            '{title} ({year})',
            '{album} - {artist} - {title}'
        ]
        
        for template in templates:
            filename = self.audio_processor.generate_filename(metadata, template, '.mp3')
            print(f"✅ قالب '{template}' → '{filename}'")
        
        print("✅ تست پردازشگر صوتی موفق بود!\n")
    
    async def test_batch_processor(self):
        """تست پردازشگر دسته‌ای"""
        print("📦 تست پردازشگر دسته‌ای...")
        
        # تست تخمین زمان پردازش
        file_paths = ['file1.mp3', 'file2.flac', 'file3.wav']
        operations = ['metadata_update', 'cover_art_add']
        
        estimated_time = self.batch_processor.estimate_processing_time(file_paths, operations)
        print(f"✅ تخمین زمان پردازش {len(file_paths)} فایل: {estimated_time:.1f} ثانیه")
        
        # تست اعتبارسنجی فایل‌ها
        valid_files = self.batch_processor.validate_files(file_paths)
        print(f"✅ فایل‌های معتبر: {len(valid_files)} از {len(file_paths)}")
        
        print("✅ تست پردازشگر دسته‌ای موفق بود!\n")
    
    async def test_admin_panel(self):
        """تست پنل مدیریت"""
        print("🔧 تست پنل مدیریت...")
        
        # تست ایجاد دیتابیس
        await self.admin_panel.init_database()
        print("✅ دیتابیس ایجاد شد")
        
        # تست ثبت فعالیت کاربر
        user_id = 123456789
        await self.admin_panel.log_user_activity(user_id, 'test_action')
        print(f"✅ فعالیت کاربر {user_id} ثبت شد")
        
        # تست بررسی محدودیت‌ها
        can_process = await self.admin_panel.check_user_limits(user_id)
        print(f"✅ بررسی محدودیت کاربر: {'مجاز' if can_process else 'غیرمجاز'}")
        
        # تست آمار سیستم
        system_stats = await self.admin_panel.get_system_stats()
        print(f"✅ آمار سیستم: {system_stats.total_users} کاربر، {system_stats.total_files} فایل")
        
        print("✅ تست پنل مدیریت موفق بود!\n")
    
    async def test_config(self):
        """تست تنظیمات"""
        print("⚙️ تست تنظیمات...")
        
        # تست بارگذاری تنظیمات
        print(f"✅ حداکثر حجم فایل: {self.config.MAX_FILE_SIZE / (1024*1024):.1f} MB")
        print(f"✅ فرمت‌های پشتیبانی شده: {len(self.config.SUPPORTED_AUDIO_FORMATS)} فرمت")
        print(f"✅ پیش‌تنظیمات بیت‌ریت: {len(self.config.BITRATE_PRESETS)} حالت")
        
        # تست ایجاد پوشه‌ها
        self.config.ensure_directories()
        temp_exists = os.path.exists(self.config.TEMP_DIR)
        output_exists = os.path.exists(self.config.OUTPUT_DIR)
        print(f"✅ پوشه موقت: {'موجود' if temp_exists else 'ناموجود'}")
        print(f"✅ پوشه خروجی: {'موجود' if output_exists else 'ناموجود'}")
        
        print("✅ تست تنظیمات موفق بود!\n")
    
    async def test_performance(self):
        """تست عملکرد"""
        print("🚀 تست عملکرد...")
        
        import time
        
        # تست سرعت پردازش متادیتا
        start_time = time.time()
        for i in range(1000):
            metadata = {
                'title': f'آهنگ {i}',
                'artist': f'هنرمند {i}',
                'album': f'آلبوم {i // 10}',
                'year': str(2020 + (i % 5))
            }
            filename = self.audio_processor.generate_filename(metadata, '{artist} - {title}', '.mp3')
        
        processing_time = time.time() - start_time
        print(f"✅ سرعت پردازش متادیتا: {1000/processing_time:.0f} عملیات در ثانیه")
        
        # تست حافظه
        import psutil
        process = psutil.Process()
        memory_usage = process.memory_info().rss / (1024 * 1024)  # MB
        print(f"✅ مصرف حافظه: {memory_usage:.1f} MB")
        
        print("✅ تست عملکرد موفق بود!\n")
    
    async def run_all_tests(self):
        """اجرای تمام تست‌ها"""
        print("🧪 شروع تست‌های ربات موزیک تلگرام\n")
        print("=" * 50)
        
        try:
            await self.test_config()
            await self.test_audio_processor()
            await self.test_batch_processor()
            await self.test_admin_panel()
            await self.test_performance()
            
            print("=" * 50)
            print("🎉 تمام تست‌ها با موفقیت انجام شد!")
            print("✅ ربات آماده استفاده است")
            
        except Exception as e:
            print(f"❌ خطا در تست: {e}")
            print("🔧 لطفاً مشکل را بررسی کنید")
            return False
        
        return True

async def main():
    """تابع اصلی"""
    tester = BotTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🚀 برای اجرای ربات دستور زیر را وارد کنید:")
        print("python bot.py")
    else:
        print("\n❌ لطفاً مشکلات را برطرف کنید و دوباره تست کنید")

if __name__ == "__main__":
    # بررسی وجود فایل .env
    if not os.path.exists('.env'):
        print("⚠️ فایل .env یافت نشد!")
        print("لطفاً فایل .env.example را به .env کپی کنید و تنظیمات را وارد کنید")
        sys.exit(1)
    
    # اجرای تست‌ها
    asyncio.run(main())