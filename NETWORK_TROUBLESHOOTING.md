# 🌐 راهنمای حل مشکلات شبکه و نصب وابستگی‌ها

## 🚨 مشکل فعلی
خطای `ProxyError` و عدم امکان اتصال به PyPI برای نصب پکیج‌ها.

## 🔍 تشخیص مشکل

### 1. بررسی اتصال اینترنت
```bash
# تست اتصال به اینترنت
ping google.com
ping pypi.org
```

### 2. بررسی تنظیمات پروکسی
```bash
# بررسی متغیرهای محیطی پروکسی
echo $HTTP_PROXY
echo $HTTPS_PROXY
echo $NO_PROXY

# در ویندوز:
echo %HTTP_PROXY%
echo %HTTPS_PROXY%
```

## 🛠️ راه‌حل‌های پیشنهادی

### راه‌حل 1: غیرفعال کردن پروکسی برای pip
```bash
pip install --proxy="" mutagen
pip install --proxy="" python-telegram-bot
pip install --proxy="" aiofiles
```

### راه‌حل 2: استفاده از mirror های محلی
```bash
# استفاده از mirror ایرانی
pip install -i https://pypi.douban.com/simple/ mutagen
pip install -i https://mirrors.aliyun.com/pypi/simple/ python-telegram-bot

# یا mirror های دیگر
pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ mutagen
```

### راه‌حل 3: نصب آفلاین
1. دانلود فایل‌های wheel از سایت PyPI
2. نصب محلی:
```bash
pip install mutagen-1.47.0-py3-none-any.whl
```

### راه‌حل 4: استفاده از conda
```bash
# نصب conda یا miniconda
conda install mutagen
conda install -c conda-forge python-telegram-bot
```

### راه‌حل 5: تنظیم pip برای عبور از فایروال
```bash
# اضافه کردن trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org mutagen

# یا تنظیم دائمی در pip.conf
mkdir -p ~/.pip
echo "[global]
trusted-host = pypi.org
               pypi.python.org  
               files.pythonhosted.org
timeout = 120" > ~/.pip/pip.conf
```

## 🔧 تنظیمات پیشرفته

### تنظیم pip.ini در ویندوز
مسیر: `%APPDATA%\pip\pip.ini`
```ini
[global]
trusted-host = pypi.org
               pypi.python.org
               files.pythonhosted.org
timeout = 120
retries = 5

[install]
find-links = https://pypi.org/simple/
```

### استفاده از VPN یا تغییر DNS
```bash
# تغییر DNS به Cloudflare
# Primary: 1.1.1.1
# Secondary: 1.0.0.1

# یا Google DNS
# Primary: 8.8.8.8  
# Secondary: 8.8.4.4
```

## 📦 نصب دستی وابستگی‌ها

### فایل‌های مورد نیاز:
1. **mutagen** - پردازش متادیتای صوتی
2. **python-telegram-bot** - API تلگرام
3. **aiofiles** - عملیات فایل async
4. **aiosqlite** - پایگاه داده async

### دانلود و نصب دستی:
```bash
# دانلود از لینک‌های مستقیم
wget https://files.pythonhosted.org/packages/.../mutagen-1.47.0-py3-none-any.whl
pip install mutagen-1.47.0-py3-none-any.whl
```

## 🚀 راه‌حل موقت: استفاده از نسخه دمو

تا زمان حل مشکل شبکه، می‌توانید از نسخه دمو استفاده کنید:

```bash
python bot_demo.py
```

این نسخه تمام قابلیت‌های ربات را بدون وابستگی خارجی نمایش می‌دهد.

## 🔍 تست اتصال

### اسکریپت تست اتصال:
```python
import urllib.request
import ssl

def test_connection():
    try:
        # تست اتصال به PyPI
        context = ssl.create_default_context()
        with urllib.request.urlopen('https://pypi.org', context=context, timeout=10) as response:
            print("✅ اتصال به PyPI موفق")
            return True
    except Exception as e:
        print(f"❌ خطا در اتصال: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

## 📞 پشتیبانی

اگر مشکل همچنان ادامه دارد:

1. **بررسی فایروال** شرکت یا سازمان
2. **تماس با مدیر شبکه** برای باز کردن دسترسی به PyPI
3. **استفاده از شبکه دیگر** (موبایل، وای‌فای خانگی)
4. **نصب در محیط مجازی** دیگر

## ⚡ راه‌حل سریع

برای شروع سریع کار:

```bash
# اجرای نسخه دمو
python bot_demo.py

# یا استفاده از Docker (اگر Docker نصب است)
docker run -it python:3.11 pip install mutagen python-telegram-bot
```

---

**نکته:** این مشکل معمولاً مربوط به تنظیمات شبکه، فایروال یا پروکسی است و با راه‌حل‌های بالا قابل حل است.