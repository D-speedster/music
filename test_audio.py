#!/usr/bin/env python3
"""
اسکریپت تست برای ایجاد فایل صوتی نمونه
"""

import os
import wave
import struct
import math

def create_test_audio():
    """ایجاد فایل صوتی تست ساده"""
    
    # تنظیمات فایل صوتی
    sample_rate = 44100  # نرخ نمونه‌برداری
    duration = 5  # مدت زمان به ثانیه
    frequency = 440  # فرکانس (A4)
    
    # محاسبه تعداد فریم‌ها
    num_frames = int(sample_rate * duration)
    
    # ایجاد فایل WAV
    output_file = "test_audio.wav"
    
    with wave.open(output_file, 'w') as wav_file:
        # تنظیم پارامترهای فایل
        wav_file.setnchannels(1)  # مونو
        wav_file.setsampwidth(2)  # 16 بیت
        wav_file.setframerate(sample_rate)
        
        # تولید موج سینوسی
        for i in range(num_frames):
            # محاسبه مقدار نمونه
            sample = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            # نوشتن نمونه به فایل
            wav_file.writeframes(struct.pack('<h', sample))
    
    print(f"✅ فایل تست ایجاد شد: {output_file}")
    print(f"📊 مدت زمان: {duration} ثانیه")
    print(f"🎵 فرکانس: {frequency} Hz")
    print(f"📁 حجم فایل: {os.path.getsize(output_file)} بایت")
    
    return output_file

if __name__ == "__main__":
    create_test_audio()