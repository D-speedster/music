#!/usr/bin/env python3
"""
تست کامل عملکرد AudioEditor
"""
import os
import shutil
from audio_editor import AudioEditor
from config import Config

def test_audio_editor():
    """تست کامل عملکرد AudioEditor"""
    
    print("🔄 شروع تست AudioEditor...")
    
    # بررسی وجود فایل تست
    test_file = "test_audio.mp3"
    if not os.path.exists(test_file):
        print("❌ فایل تست موجود نیست. ابتدا python create_test_mp3.py را اجرا کنید.")
        return
    
    try:
        # ایجاد AudioEditor
        editor = AudioEditor()
        
        # بارگذاری فایل
        print(f"📂 بارگذاری فایل: {test_file}")
        audio_file = editor.load_file(test_file)
        if audio_file:
            print("✅ فایل با موفقیت بارگذاری شد")
        else:
            print("❌ خطا در بارگذاری فایل")
            return
        
        # دریافت متادیتا فعلی
        print("\n📋 متادیتای فعلی:")
        metadata = editor.get_metadata(test_file)
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        
        # به‌روزرسانی متادیتا
        print("\n✏️ به‌روزرسانی متادیتا...")
        new_metadata = {
            'title': 'آهنگ تست',
            'artist': 'هنرمند تست',
            'album': 'آلبوم تست',
            'genre': 'تست',
            'year': '2024',
            'track': '1'
        }
        
        success = editor.update_metadata(test_file, new_metadata)
        if success:
            print("  ✅ متادیتا با موفقیت به‌روزرسانی شد")
            for key, value in new_metadata.items():
                print(f"    {key}: {value}")
        else:
            print("  ❌ خطا در به‌روزرسانی متادیتا")
        
        # دریافت متادیتای جدید
        print("\n📋 متادیتای جدید:")
        updated_metadata = editor.get_metadata(test_file)
        for key, value in updated_metadata.items():
            print(f"  {key}: {value}")
        
        # تولید نام فایل
        print("\n📝 تولید نام فایل:")
        filename_patterns = [
            "{artist} - {title}",
            "{title} ({year})",
            "{album} - {track} - {title}",
            "{artist} - {album} - {title}"
        ]
        
        for pattern in filename_patterns:
            filename = editor.generate_filename(updated_metadata, pattern)
            print(f"  {pattern} → {filename}")
        
        # کپی فایل به عنوان خروجی
        output_file = os.path.join(Config.OUTPUT_DIR, "test_output.mp3")
        print(f"\n💾 کپی فایل: {output_file}")
        
        # اطمینان از وجود دایرکتوری خروجی
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        shutil.copy2(test_file, output_file)
        print(f"✅ فایل کپی شد: {output_file}")
        
        # بررسی حجم فایل
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"📊 حجم فایل خروجی: {size} بایت")
        
        # بررسی متادیتای فایل خروجی
        print("\n📋 متادیتای فایل خروجی:")
        output_metadata = editor.get_metadata(output_file)
        for key, value in output_metadata.items():
            print(f"  {key}: {value}")
        
        print("\n🎉 تست AudioEditor با موفقیت تکمیل شد!")
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audio_editor()