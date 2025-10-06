#!/usr/bin/env python3
"""
ایجاد فایل MP3 تست کوچک برای آزمایش AudioEditor
"""

import os
import base64
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC, TRCK

def create_minimal_mp3():
    """ایجاد فایل MP3 کوچک با متادیتا"""
    
    print("🔄 ایجاد فایل MP3 تست...")
    
    try:
        # یک فایل MP3 کوچک (حدود 1 ثانیه سکوت) در فرمت base64
        # این فایل MP3 واقعی است که شامل header های صحیح MP3 می‌باشد
        mp3_data = base64.b64decode("""
        SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAAEAAABIADAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDV1dXV1dXV1dXV1dXV1dXV1dXV1dXV1dXV1dXV1dXV6urq6urq6urq6urq6urq6urq6urq6urq6urq6urq6v////////////////////////////////8AAAAATGF2YzU4LjEzAAAAAAAAAAAAAAAAJAAAAAAAAAAAASDs90hvAAAAAAAAAAAAAAAAAAAA//tQxAAAAAAAAAAAAAAAAAAAAAAASW5mbwAAAA8AAAAEAAABIADAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDV1dXV1dXV1dXV1dXV1dXV1dXV1dXV1dXV1dXV1dXV6urq6urq6urq6urq6urq6urq6urq6urq6urq6urq6v////////////////////////////////8AAAAATGF2YzU4LjEzAAAAAAAAAAAAAAAAJAAAAAAAAAAAASDs90hvAAAAAAAAAAAAAAAAAAAA
        """.replace('\n', '').replace(' ', ''))
        
        # ذخیره فایل MP3
        with open("test_audio.mp3", "wb") as f:
            f.write(mp3_data)
        
        # اضافه کردن متادیتا
        audio = MP3("test_audio.mp3")
        
        # اضافه کردن تگ‌های ID3
        if audio.tags is None:
            audio.add_tags()
        
        audio.tags.add(TIT2(encoding=3, text="Test Song"))
        audio.tags.add(TPE1(encoding=3, text="Test Artist"))
        audio.tags.add(TALB(encoding=3, text="Test Album"))
        audio.tags.add(TCON(encoding=3, text="Test"))
        audio.tags.add(TDRC(encoding=3, text="2024"))
        audio.tags.add(TRCK(encoding=3, text="1"))
        
        audio.save()
        
        # بررسی فایل ایجاد شده
        if os.path.exists("test_audio.mp3"):
            size = os.path.getsize("test_audio.mp3")
            print(f"✅ فایل MP3 تست ایجاد شد: test_audio.mp3")
            print(f"📊 حجم: {size} بایت")
            
            # بررسی متادیتا
            audio = MP3("test_audio.mp3")
            print("📋 متادیتای اضافه شده:")
            if audio.tags:
                for key, value in audio.tags.items():
                    print(f"  {key}: {value}")
        else:
            print("❌ خطا در ایجاد فایل")
            
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_minimal_mp3()