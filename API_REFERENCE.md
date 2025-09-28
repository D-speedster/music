# 📚 مرجع API ربات موزیک تلگرام

## 🏗️ معماری کلی

### ساختار پروژه
```
telegram-music-bot/
├── bot.py                 # فایل اصلی ربات
├── config.py             # تنظیمات و پیکربندی
├── requirements.txt      # وابستگی‌های Python
├── utils/               # ماژول‌های کمکی
│   ├── __init__.py
│   ├── audio_processor.py    # پردازش فایل‌های صوتی
│   ├── batch_processor.py    # پردازش دسته‌ای
│   └── admin_panel.py       # پنل مدیریت
├── temp/                # فایل‌های موقت
├── output/              # فایل‌های خروجی
└── data/                # پایگاه داده و لاگ‌ها
```

## 🎵 AudioProcessor Class

### مقدمه
کلاس `AudioProcessor` مسئول پردازش فایل‌های صوتی، ویرایش متادیتا، مدیریت کاور آلبوم و تبدیل فرمت است.

### Constructor
```python
class AudioProcessor:
    def __init__(self, temp_dir: str = "temp", output_dir: str = "output")
```

**پارامترها:**
- `temp_dir` (str): مسیر دایرکتوری فایل‌های موقت
- `output_dir` (str): مسیر دایرکتوری فایل‌های خروجی

### Methods

#### extract_metadata()
```python
def extract_metadata(self, file_path: str) -> Dict[str, Any]
```
استخراج متادیتا از فایل صوتی.

**پارامترها:**
- `file_path` (str): مسیر فایل صوتی

**خروجی:**
```python
{
    "title": str,
    "artist": str,
    "album": str,
    "genre": str,
    "year": str,
    "track": str,
    "duration": float,
    "bitrate": int,
    "format": str,
    "has_cover": bool
}
```

**مثال:**
```python
processor = AudioProcessor()
metadata = processor.extract_metadata("song.mp3")
print(f"Title: {metadata['title']}")
```

#### update_metadata()
```python
def update_metadata(self, file_path: str, metadata: Dict[str, str]) -> bool
```
به‌روزرسانی متادیتا فایل صوتی.

**پارامترها:**
- `file_path` (str): مسیر فایل صوتی
- `metadata` (Dict[str, str]): دیکشنری متادیتای جدید

**کلیدهای قابل قبول:**
- `title`: نام آهنگ
- `artist`: نام هنرمند
- `album`: نام آلبوم
- `genre`: ژانر موسیقی
- `year`: سال انتشار
- `track`: شماره ترک

**خروجی:**
- `bool`: True در صورت موفقیت، False در غیر این صورت

**مثال:**
```python
new_metadata = {
    "title": "آهنگ جدید",
    "artist": "هنرمند",
    "album": "آلبوم جدید",
    "year": "2024"
}
success = processor.update_metadata("song.mp3", new_metadata)
```

#### add_cover_art()
```python
def add_cover_art(self, audio_path: str, cover_path: str) -> bool
```
اضافه کردن کاور آلبوم به فایل صوتی.

**پارامترها:**
- `audio_path` (str): مسیر فایل صوتی
- `cover_path` (str): مسیر فایل تصویر کاور

**خروجی:**
- `bool`: True در صورت موفقیت

**مثال:**
```python
success = processor.add_cover_art("song.mp3", "cover.jpg")
```

#### remove_cover_art()
```python
def remove_cover_art(self, file_path: str) -> bool
```
حذف کاور آلبوم از فایل صوتی.

#### extract_cover_art()
```python
def extract_cover_art(self, audio_path: str, output_path: str) -> bool
```
استخراج کاور آلبوم و ذخیره به عنوان فایل جداگانه.

#### convert_format()
```python
def convert_format(self, input_path: str, output_format: str, 
                  quality: str = "medium") -> Optional[str]
```
تبدیل فرمت فایل صوتی.

**پارامترها:**
- `input_path` (str): مسیر فایل ورودی
- `output_format` (str): فرمت خروجی (mp3, flac, wav, m4a, ogg, aac)
- `quality` (str): کیفیت (low, medium, high, lossless)

**خروجی:**
- `Optional[str]`: مسیر فایل خروجی یا None در صورت خطا

**مثال:**
```python
output_file = processor.convert_format("song.flac", "mp3", "high")
```

#### generate_filename()
```python
def generate_filename(self, metadata: Dict[str, str], 
                     template: str, extension: str) -> str
```
تولید نام فایل بر اساس قالب و متادیتا.

**قالب‌های پشتیبانی شده:**
- `{title}`: نام آهنگ
- `{artist}`: نام هنرمند
- `{album}`: نام آلبوم
- `{year}`: سال انتشار
- `{track}`: شماره ترک
- `{genre}`: ژانر

**مثال:**
```python
filename = processor.generate_filename(
    metadata, 
    "{artist} - {title}", 
    "mp3"
)
```

## 📦 BatchProcessor Class

### مقدمه
کلاس `BatchProcessor` برای پردازش همزمان چندین فایل صوتی طراحی شده است.

### Constructor
```python
class BatchProcessor:
    def __init__(self, audio_processor: AudioProcessor, max_concurrent: int = 3)
```

### Methods

#### process_files()
```python
async def process_files(self, file_paths: List[str], 
                       operations: Dict[str, Any]) -> Dict[str, Any]
```
پردازش دسته‌ای فایل‌ها.

**پارامترها:**
- `file_paths` (List[str]): لیست مسیر فایل‌ها
- `operations` (Dict[str, Any]): عملیات مورد نظر

**ساختار operations:**
```python
{
    "metadata_update": {
        "title": "نام جدید",
        "artist": "هنرمند جدید"
    },
    "cover_action": {
        "action": "add",  # add, remove, extract
        "cover_path": "path/to/cover.jpg"
    },
    "format_conversion": {
        "format": "mp3",
        "quality": "high"
    },
    "filename_template": "{artist} - {title}"
}
```

**خروجی:**
```python
{
    "success": bool,
    "processed_files": List[str],
    "failed_files": List[str],
    "errors": List[str],
    "processing_time": float
}
```

#### estimate_processing_time()
```python
def estimate_processing_time(self, file_paths: List[str], 
                           operations: Dict[str, Any]) -> float
```
تخمین زمان پردازش.

## 👑 AdminPanel Class

### مقدمه
کلاس `AdminPanel` برای مدیریت آمار، کاربران و تنظیمات ربات استفاده می‌شود.

### Constructor
```python
class AdminPanel:
    def __init__(self, db_path: str = "data/admin.db")
```

### Methods

#### log_user_activity()
```python
async def log_user_activity(self, user_id: int, username: str = None, 
                           action: str = "start") -> None
```
ثبت فعالیت کاربر.

#### log_file_processing()
```python
async def log_file_processing(self, user_id: int, filename: str, 
                             file_size: int, format_type: str, 
                             operations: List[str], processing_time: float) -> None
```
ثبت پردازش فایل.

#### check_user_limits()
```python
async def check_user_limits(self, user_id: int) -> Dict[str, Any]
```
بررسی محدودیت‌های کاربر.

**خروجی:**
```python
{
    "can_process": bool,
    "daily_count": int,
    "daily_limit": int,
    "remaining": int,
    "is_banned": bool
}
```

#### get_user_stats()
```python
async def get_user_stats(self, user_id: int) -> UserStats
```
دریافت آمار کاربر.

#### get_system_stats()
```python
async def get_system_stats(self) -> SystemStats
```
دریافت آمار سیستم.

## 🤖 MusicBot Class

### مقدمه
کلاس اصلی ربات که تمام عملکردها را مدیریت می‌کند.

### Constructor
```python
class MusicBot:
    def __init__(self)
```

### Handler Methods

#### start_command()
```python
async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE)
```
پردازش دستور `/start`.

#### handle_audio()
```python
async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE)
```
پردازش فایل‌های صوتی آپلود شده.

#### handle_photo()
```python
async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE)
```
پردازش تصاویر کاور آپلود شده.

#### handle_text()
```python
async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE)
```
پردازش متن‌های ارسالی برای ویرایش تگ‌ها.

#### button_callback()
```python
async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE)
```
پردازش کلیک‌های دکمه‌های inline.

### Utility Methods

#### create_main_menu()
```python
def create_main_menu(self) -> InlineKeyboardMarkup
```
ایجاد منوی اصلی.

#### create_tag_menu()
```python
def create_tag_menu(self) -> InlineKeyboardMarkup
```
ایجاد منوی ویرایش تگ‌ها.

#### create_cover_menu()
```python
def create_cover_menu(self, has_cover: bool = False) -> InlineKeyboardMarkup
```
ایجاد منوی مدیریت کاور.

#### create_format_menu()
```python
def create_format_menu(self) -> InlineKeyboardMarkup
```
ایجاد منوی تبدیل فرمت.

## ⚙️ Config Module

### متغیرهای محیطی
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# تنظیمات ربات
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', 0))

# محدودیت‌ها
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50))  # مگابایت
DAILY_LIMIT = int(os.getenv('DAILY_LIMIT', 100))     # فایل در روز
MAX_CONCURRENT = int(os.getenv('MAX_CONCURRENT', 3))  # پردازش همزمان

# مسیرها
TEMP_DIR = os.getenv('TEMP_DIR', 'temp')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
DATA_DIR = os.getenv('DATA_DIR', 'data')

# فرمت‌های پشتیبانی شده
SUPPORTED_FORMATS = ['mp3', 'flac', 'wav', 'm4a', 'ogg', 'aac']
SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'webp']

# تنظیمات کیفیت
QUALITY_SETTINGS = {
    'low': {'bitrate': '128k'},
    'medium': {'bitrate': '192k'},
    'high': {'bitrate': '320k'},
    'lossless': {'codec': 'flac'}
}
```

## 🔧 Custom Exceptions

### AudioProcessingError
```python
class AudioProcessingError(Exception):
    """خطا در پردازش فایل صوتی"""
    pass
```

### UnsupportedFormatError
```python
class UnsupportedFormatError(Exception):
    """فرمت پشتیبانی نشده"""
    pass
```

### FileSizeError
```python
class FileSizeError(Exception):
    """خطا در اندازه فایل"""
    pass
```

## 📊 Data Models

### UserStats
```python
@dataclass
class UserStats:
    user_id: int
    username: str
    total_files: int
    total_size: int
    last_activity: datetime
    join_date: datetime
    favorite_format: str
    total_processing_time: float
```

### SystemStats
```python
@dataclass
class SystemStats:
    total_users: int
    active_users_today: int
    files_processed_today: int
    total_files_processed: int
    total_data_processed: int
    average_processing_time: float
    most_popular_format: str
    uptime: float
```

## 🎯 Usage Examples

### پردازش ساده فایل
```python
from utils.audio_processor import AudioProcessor

# ایجاد instance
processor = AudioProcessor()

# استخراج متادیتا
metadata = processor.extract_metadata("song.mp3")
print(f"آهنگ: {metadata['title']}")

# به‌روزرسانی تگ‌ها
new_tags = {"title": "آهنگ جدید", "artist": "هنرمند جدید"}
processor.update_metadata("song.mp3", new_tags)

# تبدیل فرمت
output_file = processor.convert_format("song.mp3", "flac", "lossless")
```

### پردازش دسته‌ای
```python
from utils.batch_processor import BatchProcessor
from utils.audio_processor import AudioProcessor

# ایجاد processors
audio_proc = AudioProcessor()
batch_proc = BatchProcessor(audio_proc)

# تعریف عملیات
operations = {
    "metadata_update": {"artist": "هنرمند جدید"},
    "format_conversion": {"format": "mp3", "quality": "high"}
}

# پردازش فایل‌ها
files = ["song1.flac", "song2.wav", "song3.m4a"]
result = await batch_proc.process_files(files, operations)
```

### مدیریت آمار
```python
from utils.admin_panel import AdminPanel

# ایجاد admin panel
admin = AdminPanel()

# ثبت فعالیت
await admin.log_user_activity(12345, "username", "file_upload")

# بررسی محدودیت‌ها
limits = await admin.check_user_limits(12345)
if limits["can_process"]:
    print("کاربر می‌تواند فایل پردازش کند")

# دریافت آمار
user_stats = await admin.get_user_stats(12345)
system_stats = await admin.get_system_stats()
```

## 🔍 Debugging و Logging

### تنظیم Logging
```python
import logging

# تنظیم سطح لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Debug Mode
```python
# فعال‌سازی حالت debug
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
```

---

**📖 این مرجع API راهنمای کاملی برای توسعه‌دهندگان جهت درک و توسعه ربات موزیک تلگرام است.**