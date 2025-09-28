# 🤝 راهنمای مشارکت در پروژه

## 🎯 خوش آمدید!

از علاقه شما به مشارکت در پروژه ربات موزیک تلگرام بسیار خوشحالیم! این راهنما به شما کمک می‌کند تا به بهترین شکل در توسعه این پروژه مشارکت کنید.

## 📋 فهرست مطالب

- [🚀 شروع سریع](#-شروع-سریع)
- [🔧 محیط توسعه](#-محیط-توسعه)
- [📝 استانداردهای کدنویسی](#-استانداردهای-کدنویسی)
- [🌿 مدیریت Branch](#-مدیریت-branch)
- [💡 انواع مشارکت](#-انواع-مشارکت)
- [🐛 گزارش باگ](#-گزارش-باگ)
- [✨ درخواست ویژگی](#-درخواست-ویژگی)
- [🔍 فرآیند Review](#-فرآیند-review)
- [📚 مستندات](#-مستندات)
- [🧪 تست‌ها](#-تست‌ها)

## 🚀 شروع سریع

### 1. Fork کردن پروژه
```bash
# Fork کردن repository در GitHub
# سپس clone کردن fork شده
git clone https://github.com/YOUR_USERNAME/telegram-music-bot.git
cd telegram-music-bot
```

### 2. تنظیم محیط توسعه
```bash
# اضافه کردن upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/telegram-music-bot.git

# ایجاد محیط مجازی
python -m venv venv
source venv/bin/activate  # Linux/macOS
# یا
venv\Scripts\activate     # Windows

# نصب وابستگی‌ها
pip install -r requirements.txt
pip install -r requirements-dev.txt  # اگر وجود دارد
```

### 3. تنظیم pre-commit hooks
```bash
# نصب pre-commit
pip install pre-commit

# نصب hooks
pre-commit install

# اجرای اولیه
pre-commit run --all-files
```

## 🔧 محیط توسعه

### ابزارهای مورد نیاز
- **Python 3.8+**
- **Git**
- **FFmpeg**
- **Code Editor** (VS Code, PyCharm, etc.)

### تنظیمات VS Code
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### Extensions پیشنهادی
- Python
- Python Docstring Generator
- GitLens
- Better Comments
- Error Lens

## 📝 استانداردهای کدنویسی

### Python Style Guide
ما از **PEP 8** و **Black** formatter استفاده می‌کنیم.

```python
# ✅ درست
def process_audio_file(file_path: str, metadata: Dict[str, str]) -> bool:
    """
    پردازش فایل صوتی و به‌روزرسانی متادیتا.
    
    Args:
        file_path: مسیر فایل صوتی
        metadata: دیکشنری متادیتای جدید
        
    Returns:
        True در صورت موفقیت، False در غیر این صورت
    """
    try:
        # پیاده‌سازی
        return True
    except Exception as e:
        logger.error(f"خطا در پردازش فایل: {e}")
        return False

# ❌ غلط
def processAudioFile(filePath,metadata):
    # بدون docstring و type hints
    pass
```

### نام‌گذاری
```python
# متغیرها و توابع: snake_case
user_id = 12345
def get_user_stats():
    pass

# کلاس‌ها: PascalCase
class AudioProcessor:
    pass

# ثابت‌ها: UPPER_CASE
MAX_FILE_SIZE = 50
SUPPORTED_FORMATS = ['mp3', 'flac']

# فایل‌ها: snake_case
audio_processor.py
batch_processor.py
```

### Type Hints
```python
from typing import Dict, List, Optional, Union

def update_metadata(
    file_path: str, 
    metadata: Dict[str, str]
) -> bool:
    pass

def process_files(
    file_paths: List[str]
) -> Optional[Dict[str, Union[str, int]]]:
    pass
```

### Docstrings
```python
def convert_format(self, input_path: str, output_format: str, 
                  quality: str = "medium") -> Optional[str]:
    """
    تبدیل فرمت فایل صوتی.
    
    این تابع فایل صوتی را از فرمت اصلی به فرمت مورد نظر تبدیل می‌کند
    با حفظ کیفیت و متادیتا.
    
    Args:
        input_path (str): مسیر فایل ورودی
        output_format (str): فرمت خروجی (mp3, flac, wav, m4a, ogg, aac)
        quality (str, optional): کیفیت خروجی. Defaults to "medium".
            - "low": 128 kbps
            - "medium": 192 kbps  
            - "high": 320 kbps
            - "lossless": بدون افت کیفیت
    
    Returns:
        Optional[str]: مسیر فایل خروجی در صورت موفقیت، None در صورت خطا
        
    Raises:
        UnsupportedFormatError: اگر فرمت پشتیبانی نشود
        FileNotFoundError: اگر فایل ورودی وجود نداشته باشد
        
    Example:
        >>> processor = AudioProcessor()
        >>> output = processor.convert_format("song.flac", "mp3", "high")
        >>> print(output)  # "output/song.mp3"
    """
```

## 🌿 مدیریت Branch

### نام‌گذاری Branch‌ها
```bash
# ویژگی جدید
feature/add-batch-processing
feature/improve-audio-quality

# رفع باگ
bugfix/fix-metadata-encoding
bugfix/handle-large-files

# بهبود عملکرد
performance/optimize-conversion
performance/reduce-memory-usage

# مستندات
docs/update-api-reference
docs/add-deployment-guide

# refactoring
refactor/cleanup-audio-processor
refactor/improve-error-handling
```

### Workflow
```bash
# 1. به‌روزرسانی main branch
git checkout main
git pull upstream main

# 2. ایجاد branch جدید
git checkout -b feature/your-feature-name

# 3. توسعه و commit
git add .
git commit -m "feat: add new feature"

# 4. push کردن
git push origin feature/your-feature-name

# 5. ایجاد Pull Request در GitHub
```

## 💡 انواع مشارکت

### 🐛 رفع باگ
1. **شناسایی مشکل** در Issues
2. **تحلیل علت** اصلی
3. **پیاده‌سازی راه‌حل**
4. **نوشتن تست** برای باگ
5. **ارسال Pull Request**

### ✨ ویژگی جدید
1. **بحث در Issues** قبل از شروع
2. **طراحی API** و interface
3. **پیاده‌سازی** به صورت تدریجی
4. **نوشتن تست‌ها**
5. **به‌روزرسانی مستندات**

### 📚 بهبود مستندات
1. **شناسایی کمبودها**
2. **نوشتن محتوای جدید**
3. **بررسی دقت** اطلاعات
4. **تست مثال‌ها**

### 🎨 بهبود UI/UX
1. **تحلیل تجربه کاربری**
2. **طراحی بهبودها**
3. **پیاده‌سازی تغییرات**
4. **تست با کاربران**

## 🐛 گزارش باگ

### قالب گزارش باگ
```markdown
## 🐛 توضیح باگ
توضیح مختصر و واضح از مشکل.

## 🔄 مراحل بازتولید
1. برو به '...'
2. کلیک روی '...'
3. اسکرول کن تا '...'
4. مشاهده خطا

## ✅ رفتار مورد انتظار
توضیح آنچه که انتظار داشتید اتفاق بیفتد.

## ❌ رفتار فعلی
توضیح آنچه که در واقع اتفاق افتاد.

## 📱 محیط
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python Version: [e.g. 3.9.7]
- Bot Version: [e.g. 1.2.3]

## 📎 فایل‌های مرتبط
اگر امکان دارد، فایل‌های نمونه یا لاگ‌ها را ضمیمه کنید.

## 📝 اطلاعات اضافی
هر اطلاعات دیگری که ممکن است مفید باشد.
```

## ✨ درخواست ویژگی

### قالب درخواست ویژگی
```markdown
## 🎯 مشکل مرتبط
آیا درخواست شما مربوط به مشکلی است؟ لطفاً توضیح دهید.

## 💡 راه‌حل پیشنهادی
توضیح واضح از آنچه که می‌خواهید اتفاق بیفتد.

## 🔄 جایگزین‌های در نظر گرفته شده
راه‌حل‌های جایگزین که در نظر گرفته‌اید.

## 📊 اولویت
- [ ] بحرانی
- [ ] بالا  
- [ ] متوسط
- [ ] پایین

## 🎨 طراحی UI (اختیاری)
اگر تغییر UI دارد، mockup یا توضیح ارائه دهید.

## 📝 اطلاعات اضافی
هر اطلاعات دیگری که مفید است.
```

## 🔍 فرآیند Review

### چک‌لیست Pull Request
- [ ] **کد تمیز** و قابل خواندن است
- [ ] **تست‌ها** نوشته شده و پاس می‌شوند
- [ ] **مستندات** به‌روزرسانی شده
- [ ] **Type hints** اضافه شده
- [ ] **Docstrings** نوشته شده
- [ ] **Performance** بررسی شده
- [ ] **Security** در نظر گرفته شده
- [ ] **Backward compatibility** حفظ شده

### معیارهای Review
1. **صحت عملکرد** - آیا کد کار می‌کند؟
2. **کیفیت کد** - آیا تمیز و قابل نگهداری است؟
3. **عملکرد** - آیا بهینه است؟
4. **امنیت** - آیا آسیب‌پذیری دارد؟
5. **تست‌ها** - آیا کافی هستند؟
6. **مستندات** - آیا کامل هستند؟

### نحوه پاسخ به Review
```markdown
## تغییرات اعمال شده
- ✅ رفع مشکل encoding در متادیتا
- ✅ اضافه کردن تست برای فایل‌های بزرگ
- ✅ بهبود error handling

## سوالات باقی‌مانده
- آیا باید timeout را افزایش دهیم؟
- نظرتان در مورد استفاده از async/await چیست؟

## تشکر
از بازخوردهای مفیدتان متشکرم! 🙏
```

## 📚 مستندات

### انواع مستندات
1. **API Reference** - مرجع کامل API
2. **User Guide** - راهنمای کاربر
3. **Developer Guide** - راهنمای توسعه‌دهنده
4. **Deployment Guide** - راهنمای استقرار
5. **Troubleshooting** - عیب‌یابی

### نوشتن مستندات
```markdown
# عنوان واضح و مفید

## مقدمه
توضیح مختصر از موضوع

## پیش‌نیازها
- Python 3.8+
- FFmpeg
- ...

## مراحل
### 1. نصب
\```bash
pip install requirements
\```

### 2. تنظیم
\```python
# کد نمونه
\```

## مثال‌های کاربردی
\```python
# مثال کامل
\```

## عیب‌یابی
### مشکل رایج 1
**علامت:** ...
**راه‌حل:** ...

## منابع بیشتر
- [لینک مفید 1](url)
- [لینک مفید 2](url)
```

## 🧪 تست‌ها

### انواع تست
1. **Unit Tests** - تست توابع منفرد
2. **Integration Tests** - تست تعامل بین ماژول‌ها
3. **End-to-End Tests** - تست کل سیستم
4. **Performance Tests** - تست عملکرد

### نوشتن تست
```python
import pytest
from unittest.mock import Mock, patch
from utils.audio_processor import AudioProcessor

class TestAudioProcessor:
    def setup_method(self):
        """تنظیم قبل از هر تست"""
        self.processor = AudioProcessor()
    
    def test_extract_metadata_success(self):
        """تست موفق استخراج متادیتا"""
        # Arrange
        file_path = "test_files/sample.mp3"
        
        # Act
        result = self.processor.extract_metadata(file_path)
        
        # Assert
        assert result is not None
        assert "title" in result
        assert "artist" in result
    
    def test_extract_metadata_file_not_found(self):
        """تست خطا در صورت عدم وجود فایل"""
        # Arrange
        file_path = "nonexistent.mp3"
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            self.processor.extract_metadata(file_path)
    
    @patch('utils.audio_processor.mutagen')
    def test_update_metadata_mock(self, mock_mutagen):
        """تست با mock کردن mutagen"""
        # Arrange
        mock_file = Mock()
        mock_mutagen.File.return_value = mock_file
        
        # Act
        result = self.processor.update_metadata("test.mp3", {"title": "test"})
        
        # Assert
        assert result is True
        mock_file.save.assert_called_once()

# تست‌های async
@pytest.mark.asyncio
async def test_batch_processing():
    """تست پردازش دسته‌ای"""
    processor = BatchProcessor()
    files = ["file1.mp3", "file2.mp3"]
    operations = {"metadata_update": {"artist": "test"}}
    
    result = await processor.process_files(files, operations)
    
    assert result["success"] is True
    assert len(result["processed_files"]) == 2
```

### اجرای تست‌ها
```bash
# اجرای همه تست‌ها
pytest

# اجرای تست‌های خاص
pytest tests/test_audio_processor.py

# اجرای با coverage
pytest --cov=utils --cov-report=html

# اجرای تست‌های async
pytest -v tests/test_async.py
```

## 📊 Performance و Profiling

### بررسی عملکرد
```python
import cProfile
import pstats
from utils.audio_processor import AudioProcessor

def profile_audio_processing():
    """پروفایل کردن پردازش صوتی"""
    processor = AudioProcessor()
    
    # اجرای عملیات
    processor.convert_format("large_file.flac", "mp3", "high")

# اجرای profiler
cProfile.run('profile_audio_processing()', 'profile_stats')

# تحلیل نتایج
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(10)
```

### بهینه‌سازی حافظه
```python
import tracemalloc
import psutil
import os

def monitor_memory_usage():
    """نظارت بر استفاده از حافظه"""
    tracemalloc.start()
    
    # کد مورد نظر
    process_large_batch()
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    
    tracemalloc.stop()
```

## 🏆 تشویق و تقدیر

### سیستم امتیازدهی
- **🥇 First Contribution** - اولین مشارکت
- **🐛 Bug Hunter** - رفع 5 باگ
- **✨ Feature Creator** - اضافه کردن 3 ویژگی
- **📚 Documentation Master** - بهبود مستندات
- **🧪 Test Champion** - نوشتن تست‌های جامع
- **🔍 Code Reviewer** - review کردن 10 PR
- **🌟 Top Contributor** - بیشترین مشارکت در ماه

### Hall of Fame
مشارکت‌کنندگان برتر در فایل `CONTRIBUTORS.md` ذکر می‌شوند.

## 📞 ارتباط با تیم

### کانال‌های ارتباطی
- **GitHub Issues** - برای باگ‌ها و ویژگی‌ها
- **GitHub Discussions** - برای بحث‌های عمومی
- **Telegram Group** - برای چت سریع
- **Email** - برای موارد خاص

### زمان پاسخ‌گویی
- **Issues**: حداکثر 48 ساعت
- **Pull Requests**: حداکثر 72 ساعت
- **Security Issues**: حداکثر 24 ساعت

## 🎉 تشکر

از تمام مشارکت‌کنندگان عزیز که با وقت و تلاش خود به بهبود این پروژه کمک می‌کنند، صمیمانه تشکر می‌کنیم! 

هر مشارکت، از کوچک تا بزرگ، ارزشمند است و به پیشرفت پروژه کمک می‌کند.

---

**🚀 آماده‌اید که شروع کنید؟ اولین Issue را انتخاب کنید و مشارکت خود را آغاز کنید!**