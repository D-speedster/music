#!/usr/bin/env python3
"""
اسکریپت تست برای ربات ویرایش موزیک
"""

import asyncio
import os
from telethon import TelegramClient
from config import Config

async def test_bot():
    """تست اتصال و عملکرد اولیه ربات"""
    
    print("🔄 شروع تست ربات...")
    
    # ایجاد کلاینت
    client = TelegramClient('test_session', Config.API_ID, Config.API_HASH)
    
    try:
        await client.start(bot_token=Config.BOT_TOKEN)
        print("✅ اتصال به تلگرام موفق!")
        
        # دریافت اطلاعات ربات
        me = await client.get_me()
        print(f"🤖 نام کاربری ربات: @{me.username}")
        print(f"📝 نام ربات: {me.first_name}")
        print(f"🆔 شناسه ربات: {me.id}")
        
        # بررسی دایرکتوری‌ها
        if os.path.exists(Config.TEMP_DIR):
            print(f"📁 دایرکتوری temp موجود است: {Config.TEMP_DIR}")
        else:
            print(f"❌ دایرکتوری temp موجود نیست: {Config.TEMP_DIR}")
            
        if os.path.exists(Config.OUTPUT_DIR):
            print(f"📁 دایرکتوری output موجود است: {Config.OUTPUT_DIR}")
        else:
            print(f"❌ دایرکتوری output موجود نیست: {Config.OUTPUT_DIR}")
        
        print("✅ تست کامل شد!")
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
    
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_bot())