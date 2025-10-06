#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تست عملکرد کامل ربات موزیک
"""

import os
import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN

async def test_bot_functionality():
    """تست عملکرد کامل ربات"""
    print("🔄 شروع تست عملکرد ربات...")
    
    # ایجاد کلاینت تست
    client = TelegramClient('test_session', API_ID, API_HASH)
    
    try:
        await client.start()
        print("✅ کلاینت تست متصل شد")
        
        # دریافت اطلاعات ربات
        bot_entity = await client.get_entity(BOT_TOKEN.split(':')[0])
        print(f"🤖 ربات پیدا شد: @{bot_entity.username}")
        
        # ارسال پیام /start
        print("\n📤 ارسال دستور /start...")
        await client.send_message(bot_entity, '/start')
        
        # انتظار برای دریافت پاسخ
        print("⏳ انتظار برای پاسخ ربات...")
        await asyncio.sleep(2)
        
        # دریافت آخرین پیام‌ها
        messages = await client.get_messages(bot_entity, limit=5)
        
        print("\n📨 آخرین پیام‌های دریافتی:")
        for i, msg in enumerate(messages):
            if msg.text:
                print(f"  {i+1}. {msg.text[:100]}...")
            if msg.buttons:
                print(f"     دکمه‌ها: {len(msg.buttons)} ردیف")
        
        # تست ارسال فایل صوتی
        test_file = "test_audio.mp3"
        if os.path.exists(test_file):
            print(f"\n📁 ارسال فایل تست: {test_file}")
            await client.send_file(bot_entity, test_file, caption="فایل تست")
            
            # انتظار برای پردازش
            await asyncio.sleep(3)
            
            # دریافت پاسخ
            new_messages = await client.get_messages(bot_entity, limit=3)
            print("\n📨 پاسخ ربات به فایل:")
            for msg in new_messages:
                if msg.text and msg.text not in [m.text for m in messages]:
                    print(f"  {msg.text[:100]}...")
                if msg.buttons:
                    print(f"  دکمه‌ها موجود: {len(msg.buttons)} ردیف")
        else:
            print(f"\n❌ فایل تست {test_file} یافت نشد")
        
        print("\n🎉 تست عملکرد ربات تکمیل شد!")
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
    
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_bot_functionality())