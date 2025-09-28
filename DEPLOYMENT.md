# 🚀 راهنمای استقرار ربات موزیک تلگرام

## 📋 پیش‌نیازهای استقرار

### سیستم‌عامل‌های پشتیبانی شده
- **🐧 Linux** (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- **🪟 Windows** (Windows 10+, Windows Server 2019+)
- **🍎 macOS** (macOS 11+)

### نرم‌افزارهای مورد نیاز
- **🐍 Python 3.8+**
- **🎵 FFmpeg 4.0+**
- **💾 SQLite 3.0+** (برای پایگاه داده)
- **📦 pip** (مدیر بسته‌های Python)

## 🏠 استقرار محلی (Local Development)

### 1. آماده‌سازی محیط
```bash
# کلون کردن پروژه
git clone https://github.com/your-username/telegram-music-bot.git
cd telegram-music-bot

# ایجاد محیط مجازی
python -m venv venv

# فعال‌سازی محیط مجازی
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt
```

### 2. تنظیم متغیرهای محیطی
```bash
# کپی کردن فایل نمونه
cp .env.example .env

# ویرایش فایل .env
nano .env
```

### 3. اجرای ربات
```bash
# اجرای مستقیم
python bot.py

# یا استفاده از اسکریپت
# Windows:
run.bat
# Linux/macOS:
chmod +x run.sh && ./run.sh
```

## ☁️ استقرار ابری (Cloud Deployment)

### 🔷 Heroku

#### 1. آماده‌سازی فایل‌ها
```bash
# ایجاد Procfile
echo "worker: python bot.py" > Procfile

# ایجاد runtime.txt
echo "python-3.11.0" > runtime.txt

# ایجاد heroku.yml (اختیاری)
cat > heroku.yml << EOF
build:
  docker:
    worker: Dockerfile
run:
  worker: python bot.py
EOF
```

#### 2. استقرار
```bash
# نصب Heroku CLI
# ورود به حساب
heroku login

# ایجاد اپلیکیشن
heroku create your-music-bot

# تنظیم متغیرهای محیطی
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set ADMIN_USER_ID=your_user_id

# نصب buildpack FFmpeg
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

# استقرار
git push heroku main

# فعال‌سازی worker
heroku ps:scale worker=1
```

### 🔶 Railway

#### 1. تنظیم پروژه
```bash
# نصب Railway CLI
npm install -g @railway/cli

# ورود به حساب
railway login

# ایجاد پروژه جدید
railway init

# لینک کردن به پروژه موجود
railway link
```

#### 2. استقرار
```bash
# تنظیم متغیرهای محیطی
railway variables set BOT_TOKEN=your_bot_token
railway variables set ADMIN_USER_ID=your_user_id

# استقرار
railway up
```

### 🔵 DigitalOcean App Platform

#### 1. ایجاد app.yaml
```yaml
name: telegram-music-bot
services:
- name: worker
  source_dir: /
  github:
    repo: your-username/telegram-music-bot
    branch: main
  run_command: python bot.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: BOT_TOKEN
    value: your_bot_token
  - key: ADMIN_USER_ID
    value: your_user_id
```

#### 2. استقرار
```bash
# استفاده از doctl CLI
doctl apps create app.yaml

# یا از طریق وب پنل DigitalOcean
```

## 🐳 استقرار با Docker

### 1. ایجاد Dockerfile
```dockerfile
FROM python:3.11-slim

# نصب FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی فایل‌های پروژه
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ایجاد دایرکتوری‌های مورد نیاز
RUN mkdir -p temp output data

# اجرای ربات
CMD ["python", "bot.py"]
```

### 2. ایجاد docker-compose.yml
```yaml
version: '3.8'

services:
  music-bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_USER_ID=${ADMIN_USER_ID}
      - MAX_FILE_SIZE=${MAX_FILE_SIZE:-50}
      - DAILY_LIMIT=${DAILY_LIMIT:-100}
    volumes:
      - ./data:/app/data
      - ./temp:/app/temp
      - ./output:/app/output
    restart: unless-stopped
    
  # اختیاری: پایگاه داده PostgreSQL
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=musicbot
      - POSTGRES_USER=musicbot
      - POSTGRES_PASSWORD=your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### 3. اجرای Docker
```bash
# ساخت و اجرا
docker-compose up -d

# مشاهده لاگ‌ها
docker-compose logs -f

# توقف
docker-compose down
```

## 🖥️ استقرار روی VPS

### 1. آماده‌سازی سرور (Ubuntu)
```bash
# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب Python و ابزارهای مورد نیاز
sudo apt install -y python3 python3-pip python3-venv git ffmpeg

# ایجاد کاربر برای ربات
sudo useradd -m -s /bin/bash musicbot
sudo su - musicbot
```

### 2. نصب پروژه
```bash
# کلون پروژه
git clone https://github.com/your-username/telegram-music-bot.git
cd telegram-music-bot

# ایجاد محیط مجازی
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# تنظیم متغیرهای محیطی
cp .env.example .env
nano .env
```

### 3. تنظیم Systemd Service
```bash
# ایجاد فایل سرویس
sudo nano /etc/systemd/system/musicbot.service
```

```ini
[Unit]
Description=Telegram Music Bot
After=network.target

[Service]
Type=simple
User=musicbot
WorkingDirectory=/home/musicbot/telegram-music-bot
Environment=PATH=/home/musicbot/telegram-music-bot/venv/bin
ExecStart=/home/musicbot/telegram-music-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# فعال‌سازی و شروع سرویس
sudo systemctl daemon-reload
sudo systemctl enable musicbot
sudo systemctl start musicbot

# بررسی وضعیت
sudo systemctl status musicbot
```

### 4. تنظیم Nginx (اختیاری)
```bash
# نصب Nginx
sudo apt install -y nginx

# تنظیم پروکسی معکوس
sudo nano /etc/nginx/sites-available/musicbot
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# فعال‌سازی سایت
sudo ln -s /etc/nginx/sites-available/musicbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 📊 نظارت و لاگ‌گیری

### 1. مشاهده لاگ‌ها
```bash
# لاگ‌های systemd
sudo journalctl -u musicbot -f

# لاگ‌های فایلی
tail -f logs/bot.log
```

### 2. نظارت با htop
```bash
# نصب htop
sudo apt install htop

# مشاهده منابع
htop
```

### 3. تنظیم Log Rotation
```bash
# ایجاد فایل logrotate
sudo nano /etc/logrotate.d/musicbot
```

```
/home/musicbot/telegram-music-bot/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 musicbot musicbot
}
```

## 🔒 امنیت و بهینه‌سازی

### 1. تنظیمات فایروال
```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

### 2. تنظیم SSL (Let's Encrypt)
```bash
# نصب Certbot
sudo apt install certbot python3-certbot-nginx

# دریافت گواهی SSL
sudo certbot --nginx -d your-domain.com
```

### 3. بهینه‌سازی عملکرد
```bash
# تنظیم محدودیت‌های سیستم
echo "musicbot soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "musicbot hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# تنظیم kernel parameters
echo "net.core.somaxconn = 65536" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 🔄 به‌روزرسانی و نگهداری

### 1. به‌روزرسانی خودکار
```bash
# ایجاد اسکریپت به‌روزرسانی
cat > update.sh << 'EOF'
#!/bin/bash
cd /home/musicbot/telegram-music-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart musicbot
EOF

chmod +x update.sh
```

### 2. پشتیبان‌گیری
```bash
# اسکریپت پشتیبان‌گیری
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backups/musicbot_$DATE.tar.gz \
    /home/musicbot/telegram-music-bot \
    --exclude=venv \
    --exclude=temp \
    --exclude=__pycache__
EOF

# اجرای خودکار با cron
echo "0 2 * * * /home/musicbot/backup.sh" | crontab -
```

## 🚨 عیب‌یابی

### مشکلات رایج

#### 1. خطای FFmpeg
```bash
# بررسی نصب FFmpeg
ffmpeg -version

# نصب مجدد
sudo apt install --reinstall ffmpeg
```

#### 2. مشکل حافظه
```bash
# بررسی استفاده از حافظه
free -h

# افزایش swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 3. خطای دسترسی فایل
```bash
# تنظیم مجوزها
sudo chown -R musicbot:musicbot /home/musicbot/telegram-music-bot
chmod -R 755 /home/musicbot/telegram-music-bot
```

### لاگ‌های مفید
```bash
# لاگ‌های سیستم
sudo journalctl -xe

# لاگ‌های Nginx
sudo tail -f /var/log/nginx/error.log

# لاگ‌های Python
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

---

**🎯 با این راهنمای کامل، می‌توانید ربات موزیک تلگرام خود را در هر محیطی با موفقیت مستقر کنید!**