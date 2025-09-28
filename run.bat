@echo off
chcp 65001 >nul
title Telegram Music Bot - اجرای ربات

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🎵 Telegram Music Bot 🎵                 ║
echo ║                      اجرای ربات موزیک                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: بررسی وجود محیط مجازی
if not exist "venv\" (
    echo ❌ محیط مجازی یافت نشد!
    echo 💡 لطفاً ابتدا install.bat را اجرا کنید.
    echo.
    pause
    exit /b 1
)

:: بررسی وجود فایل .env
if not exist ".env" (
    echo ❌ فایل .env یافت نشد!
    echo 💡 لطفاً ابتدا فایل .env را تنظیم کنید.
    echo.
    echo 📝 مراحل تنظیم:
    echo    1. فایل .env.example را کپی کرده و نام آن را به .env تغییر دهید
    echo    2. BOT_TOKEN و ADMIN_USER_ID را تنظیم کنید
    echo.
    pause
    exit /b 1
)

:: فعال‌سازی محیط مجازی
echo 🔄 فعال‌سازی محیط مجازی...
call venv\Scripts\activate.bat

:: بررسی نصب وابستگی‌ها
echo 🔍 بررسی وابستگی‌ها...
python -c "import telegram, mutagen, aiofiles, aiosqlite" 2>nul
if errorlevel 1 (
    echo ❌ برخی وابستگی‌ها نصب نشده‌اند!
    echo 🔄 نصب وابستگی‌ها...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ خطا در نصب وابستگی‌ها!
        pause
        exit /b 1
    )
)

:: بررسی وجود دایرکتوری‌های مورد نیاز
if not exist "temp\" mkdir temp
if not exist "output\" mkdir output

:: اجرای ربات
echo.
echo ✅ همه چیز آماده است!
echo 🚀 شروع ربات...
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  برای توقف ربات از Ctrl+C استفاده کنید                    ║
echo ║  لاگ‌ها در پایین نمایش داده می‌شوند                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: اجرای ربات با مدیریت خطا
python bot.py
set exit_code=%errorlevel%

echo.
if %exit_code% equ 0 (
    echo ✅ ربات با موفقیت متوقف شد.
) else (
    echo ❌ ربات با خطا متوقف شد! (کد خطا: %exit_code%)
    echo.
    echo 🔍 راهنمای عیب‌یابی:
    echo    1. بررسی اتصال اینترنت
    echo    2. بررسی صحت BOT_TOKEN در فایل .env
    echo    3. بررسی لاگ‌های بالا برای جزئیات خطا
    echo    4. اطمینان از نصب FFmpeg
    echo.
)

echo.
echo 📝 برای اجرای مجدد، این فایل را دوباره اجرا کنید.
pause