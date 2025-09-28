# 🌐 حل مشکل اتصال شبکه ربات تلگرام

## 🔍 تشخیص مشکل

ربات شما با موفقیت راه‌اندازی شده اما نمی‌تواند به سرورهای تلگرام متصل شود. خطای دریافتی:

```
telegram.error.NetworkError: httpx.ConnectError: All connection attempts failed
```

## 🛠️ راه‌حل‌های پیشنهادی

### 1️⃣ بررسی اتصال اینترنت

```bash
# تست اتصال به سرورهای تلگرام
ping api.telegram.org
```

### 2️⃣ بررسی تنظیمات پروکسی

اگر از پروکسی استفاده می‌کنید، ممکن است نیاز به تنظیمات خاص باشد:

```python
# اضافه کردن پروکسی به bot.py
from telegram.ext import Application
from telegram.request import HTTPXRequest

# تنظیم پروکسی
proxy_url = "http://proxy-server:port"  # آدرس پروکسی خود را وارد کنید
request = HTTPXRequest(proxy=proxy_url)

# ایجاد اپلیکیشن با پروکسی
application = Application.builder().token(Config.BOT_TOKEN).request(request).build()
```

### 3️⃣ استفاده از VPN

اگر دسترسی به تلگرام محدود است:
- از VPN معتبر استفاده کنید
- سرور VPN را به کشوری تغییر دهید که تلگرام آزاد است

### 4️⃣ تنظیم DNS

تغییر DNS به سرورهای عمومی:
- Google DNS: `8.8.8.8`, `8.8.4.4`
- Cloudflare DNS: `1.1.1.1`, `1.0.0.1`

### 5️⃣ بررسی فایروال

- فایروال ویندوز را بررسی کنید
- پورت‌های مورد نیاز تلگرام را باز کنید
- آنتی‌ویروس را موقتاً غیرفعال کنید

### 6️⃣ تست با ربات آفلاین

برای اطمینان از صحت کد، ربات آفلاین را اجرا کنید:

```bash
python bot_offline.py
```

## 🔧 تنظیمات پیشرفته

### اضافه کردن Timeout و Retry

```python
# در فایل bot.py
from telegram.request import HTTPXRequest

# تنظیمات شبکه پیشرفته
request = HTTPXRequest(
    connection_pool_size=8,
    connect_timeout=60.0,
    read_timeout=60.0,
    write_timeout=60.0,
    pool_timeout=60.0,
)

application = Application.builder().token(Config.BOT_TOKEN).request(request).build()
```

### استفاده از پروکسی SOCKS

```python
# نصب کتابخانه مورد نیاز
# pip install python-socks[asyncio]

from telegram.request import HTTPXRequest

# تنظیم پروکسی SOCKS
proxy_url = "socks5://127.0.0.1:1080"  # آدرس پروکسی SOCKS خود
request = HTTPXRequest(proxy=proxy_url)

application = Application.builder().token(Config.BOT_TOKEN).request(request).build()
```

## 📋 چک‌لیست عیب‌یابی

- [ ] اتصال اینترنت فعال است
- [ ] تلگرام در مرورگر کار می‌کند
- [ ] BOT_TOKEN صحیح است
- [ ] فایروال مشکلی ایجاد نمی‌کند
- [ ] پروکسی (در صورت استفاده) صحیح تنظیم شده
- [ ] DNS مناسب تنظیم شده
- [ ] VPN (در صورت نیاز) فعال است

## 🆘 راه‌حل‌های اضطراری

### 1. استفاده از شبکه دیگر
- موبایل هات‌اسپات
- شبکه اینترنت دیگر

### 2. تست در زمان دیگر
- ممکن است مشکل موقتی باشد
- چند ساعت بعد دوباره تست کنید

### 3. استفاده از سرور مجازی
- اجرای ربات روی VPS
- استفاده از سرویس‌های ابری

## 📞 دریافت کمک

اگر مشکل همچنان ادامه دارد:

1. **بررسی لاگ‌های کامل:**
   ```bash
   python bot.py > bot_log.txt 2>&1
   ```

2. **تست اتصال:**
   ```python
   import requests
   try:
       response = requests.get("https://api.telegram.org", timeout=10)
       print("اتصال موفق:", response.status_code)
   except Exception as e:
       print("خطای اتصال:", e)
   ```

3. **مشاوره با ادمین شبکه**

## ✅ تأیید عملکرد

پس از حل مشکل، برای تأیید عملکرد:

```bash
python bot.py
```

باید پیام زیر را ببینید:
```
🎵 ربات موزیک راه‌اندازی شد!
```

و ربات باید بدون خطا به کار خود ادامه دهد.

---

💡 **نکته:** کد ربات شما کاملاً صحیح است و مشکل فقط در اتصال شبکه می‌باشد.