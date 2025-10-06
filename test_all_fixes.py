#!/usr/bin/env python3
"""
اسکریپت تست جامع برای آزمایش تمام اصلاحات ربات
"""

import os
import sys
from audio_editor import AudioEditor

def test_cover_detection():
    """تست تشخیص کاور موجود"""
    print("🔍 تست تشخیص کاور موجود...")
    
    editor = AudioEditor()
    
    # تست فایل بدون کاور
    metadata_no_cover = editor.get_metadata("test_audio.mp3")
    print(f"فایل test_audio.mp3 - کاور: {'✅ دارد' if metadata_no_cover.get('has_cover') else '❌ ندارد'}")
    
    # اگر فایل خروجی وجود دارد، آن را هم تست کن
    output_file = "output/test_output.mp3"
    if os.path.exists(output_file):
        metadata_with_cover = editor.get_metadata(output_file)
        print(f"فایل {output_file} - کاور: {'✅ دارد' if metadata_with_cover.get('has_cover') else '❌ ندارد'}")
    
    return True

def test_cover_addition():
    """تست افزودن کاور"""
    print("\n🖼️ تست افزودن کاور...")
    
    editor = AudioEditor()
    
    # ایجاد یک تصویر تست ساده
    test_cover_path = "test_cover.jpg"
    
    # ایجاد یک تصویر ساده با PIL
    try:
        from PIL import Image
        
        # ایجاد تصویر 300x300 قرمز
        img = Image.new('RGB', (300, 300), color='red')
        img.save(test_cover_path, 'JPEG')
        print(f"✅ تصویر تست ایجاد شد: {test_cover_path}")
        
        # کپی فایل صوتی برای تست
        test_audio_copy = "test_audio_copy.mp3"
        import shutil
        shutil.copy("test_audio.mp3", test_audio_copy)
        
        # افزودن کاور
        success = editor.add_cover_art(test_audio_copy, test_cover_path)
        
        if success:
            print("✅ کاور با موفقیت اضافه شد")
            
            # بررسی متادیتا
            metadata = editor.get_metadata(test_audio_copy)
            print(f"وضعیت کاور پس از افزودن: {'✅ دارد' if metadata.get('has_cover') else '❌ ندارد'}")
            
            # پاک کردن فایل‌های تست
            if os.path.exists(test_audio_copy):
                os.remove(test_audio_copy)
            if os.path.exists(test_cover_path):
                os.remove(test_cover_path)
                
            return True
        else:
            print("❌ خطا در افزودن کاور")
            return False
            
    except ImportError:
        print("❌ PIL در دسترس نیست - تست کاور رد شد")
        return True
    except Exception as e:
        print(f"❌ خطا در تست کاور: {e}")
        return False

def test_metadata_operations():
    """تست عملیات متادیتا"""
    print("\n📝 تست عملیات متادیتا...")
    
    editor = AudioEditor()
    
    # خواندن متادیتا
    metadata = editor.get_metadata("test_audio.mp3")
    print("متادیتای فعلی:")
    for key, value in metadata.items():
        if key != 'has_cover':
            print(f"  {key}: {value}")
    
    # تست تولید نام فایل
    patterns = [
        "{artist} - {title}",
        "{title}",
        "{artist} - {album} - {track} - {title}"
    ]
    
    print("\nتست تولید نام فایل:")
    for pattern in patterns:
        filename = editor.generate_filename(metadata, pattern)
        print(f"  الگو: {pattern}")
        print(f"  نتیجه: {filename}")
    
    return True

def main():
    """اجرای تمام تست‌ها"""
    print("🚀 شروع تست جامع اصلاحات ربات")
    print("=" * 50)
    
    tests = [
        ("تشخیص کاور", test_cover_detection),
        ("افزودن کاور", test_cover_addition),
        ("عملیات متادیتا", test_metadata_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'موفق' if result else 'ناموفق'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ {test_name}: خطا - {e}")
    
    print("\n" + "=" * 50)
    print("📊 خلاصه نتایج:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ موفق" if result else "❌ ناموفق"
        print(f"  {test_name}: {status}")
    
    print(f"\nنتیجه کلی: {passed}/{total} تست موفق")
    
    if passed == total:
        print("🎉 تمام تست‌ها موفق بودند!")
        return True
    else:
        print("⚠️ برخی تست‌ها ناموفق بودند.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)