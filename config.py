import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Bot credentials
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    if BOT_TOKEN == 'your_bot_token_here' or not BOT_TOKEN:
        raise ValueError("❌ لطفاً BOT_TOKEN واقعی را در فایل .env وارد کنید. فایل .env.example را مشاهده کنید.")
    
    # Check for API_ID
    api_id_str = os.getenv('API_ID', '0')
    if api_id_str == 'your_api_id_here' or not api_id_str.isdigit():
        raise ValueError("❌ لطفاً API_ID واقعی را در فایل .env وارد کنید. فایل .env.example را مشاهده کنید.")
    API_ID = int(api_id_str)
    
    API_HASH = os.getenv('API_HASH', '')
    if API_HASH == 'your_api_hash_here' or not API_HASH:
        raise ValueError("❌ لطفاً API_HASH واقعی را در فایل .env وارد کنید. فایل .env.example را مشاهده کنید.")
    
    # Admin settings
    ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', 0))
    
    # Directory settings
    TEMP_DIR = os.getenv('TEMP_DIR', 'temp')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
    
    # File settings
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 2000)) * 1024 * 1024  # Convert MB to bytes
    
    # Supported audio formats
    SUPPORTED_AUDIO_FORMATS = [
        '.mp3', '.flac', '.wav', '.m4a', '.ogg', '.aac', '.wma'
    ]
    
    # Supported image formats for covers
    SUPPORTED_IMAGE_FORMATS = [
        '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'
    ]
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        if not cls.API_ID:
            raise ValueError("API_ID is required")
        if not cls.API_HASH:
            raise ValueError("API_HASH is required")
        
        cls.ensure_directories()
        return True