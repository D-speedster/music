import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # File Settings
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 2048))
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Directory Settings
    TEMP_DIR = os.getenv('TEMP_DIR', './temp')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output')
    
    # Admin Settings
    ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')
    
    # Supported Audio Formats
    SUPPORTED_AUDIO_FORMATS = [
        '.mp3', '.flac', '.wav', '.m4a', '.ogg', '.aac', '.wma'
    ]
    
    # Supported Image Formats for Cover Art
    SUPPORTED_IMAGE_FORMATS = [
        '.jpg', '.jpeg', '.png', '.bmp', '.gif'
    ]
    
    # Audio Quality Presets
    BITRATE_PRESETS = {
        'low': 128,
        'medium': 192,
        'high': 320,
        'lossless': None
    }
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)