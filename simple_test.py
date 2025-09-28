#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تست ساده ساختار پروژه ربات موزیک تلگرام
"""

import os
import sys
from pathlib import Path

def test_project_structure():
    """تست ساختار پروژه"""
    print("📁 بررسی ساختار پروژه...")
    
    required_files = [
        'bot.py',
        'config.py',
        'requirements.txt',
        '.env.example',
        'README.md',
        'install.bat',
        'run.bat'
    ]
    
    required_dirs = [
        'utils',
        'temp',
        'output'
    ]
    
    required_utils = [
        'utils/__init__.py',
        'utils/audio_processor.py',
        'utils/batch_processor.py',
        'utils/admin_panel.py'
    ]
    
    # بررسی فایل‌های اصلی
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    # بررسی پوشه‌ها
    missing_dirs = []
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
        else:
            print(f"✅ {dir_name}/")
    
    # بررسی فایل‌های utils
    missing_utils = []
    for util_file in required_utils:
        if not os.path.exists(util_file):
            missing_utils.append(util_file)
        else:
            print(f"✅ {util_file}")
    
    # نتیجه‌گیری
    if missing_files or missing_dirs or missing_utils:
        print("\n❌ فایل‌ها یا پوشه‌های ناموجود:")
        for item in missing_files + missing_dirs + missing_utils:
            print(f"   - {item}")
        return False
    else:
        print("\n✅ تمام فایل‌ها و پوشه‌های مورد نیاز موجود است!")
        return True

def test_file_contents():
    """تست محتوای فایل‌ها"""
    print("\n📄 بررسی محتوای فایل‌ها...")
    
    # بررسی bot.py
    if os.path.exists('bot.py'):
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class MusicBot' in content:
                print("✅ کلاس MusicBot در bot.py موجود است")
            else:
                print("❌ کلاس MusicBot در bot.py یافت نشد")
    
    # بررسی config.py
    if os.path.exists('config.py'):
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class Config' in content:
                print("✅ کلاس Config در config.py موجود است")
            else:
                print("❌ کلاس Config در config.py یافت نشد")
    
    # بررسی .env.example
    if os.path.exists('.env.example'):
        with open('.env.example', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'BOT_TOKEN' in content:
                print("✅ BOT_TOKEN در .env.example موجود است")
            else:
                print("❌ BOT_TOKEN در .env.example یافت نشد")

def test_imports():
    """تست import های پایتون"""
    print("\n🐍 بررسی import های پایتون...")
    
    try:
        # تست import های استاندارد
        import os
        import sys
        import asyncio
        import json
        import sqlite3
        print("✅ ماژول‌های استاندارد پایتون")
        
        # تست pathlib
        from pathlib import Path
        print("✅ pathlib")
        
        return True
    except ImportError as e:
        print(f"❌ خطا در import: {e}")
        return False

def check_env_file():
    """بررسی فایل .env"""
    print("\n⚙️ بررسی فایل تنظیمات...")
    
    if os.path.exists('.env'):
        print("✅ فایل .env موجود است")
        return True
    else:
        print("⚠️ فایل .env موجود نیست")
        print("💡 برای ایجاد فایل .env:")
        print("   copy .env.example .env")
        return False

def main():
    """تابع اصلی"""
    print("🧪 تست ساده ربات موزیک تلگرام")
    print("=" * 50)
    
    # تست‌های مختلف
    structure_ok = test_project_structure()
    test_file_contents()
    imports_ok = test_imports()
    env_ok = check_env_file()
    
    print("\n" + "=" * 50)
    
    if structure_ok and imports_ok:
        print("🎉 ساختار پروژه صحیح است!")
        
        if env_ok:
            print("✅ پروژه آماده استفاده است")
            print("\n🚀 مراحل بعدی:")
            print("1. نصب وابستگی‌ها: pip install -r requirements.txt")
            print("2. تنظیم فایل .env")
            print("3. اجرای ربات: python bot.py")
        else:
            print("⚠️ لطفاً فایل .env را تنظیم کنید")
    else:
        print("❌ مشکلاتی در ساختار پروژه وجود دارد")
        print("🔧 لطفاً فایل‌های ناموجود را بررسی کنید")

if __name__ == "__main__":
    main()