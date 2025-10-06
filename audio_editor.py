import os
import shutil
from typing import Optional, Dict, Any, Union
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, TDRC, TRCK, TPE2
from mutagen.mp3 import MP3
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class AudioEditor:
    """کلاس ویرایش فایل‌های صوتی و متادیتا"""
    
    def __init__(self):
        self.supported_formats = ['.mp3', '.flac', '.wav', '.m4a', '.ogg', '.aac']
        
    def load_file(self, file_path: str) -> Optional[MutagenFile]:
        """بارگذاری فایل صوتی"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
                
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                logger.error(f"Unsupported audio format: {file_path}")
                return None
                
            return audio_file
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return None
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """استخراج متادیتا از فایل صوتی"""
        audio_file = self.load_file(file_path)
        if not audio_file:
            return {}
        
        metadata = {
            'title': '',
            'artist': '',
            'album': '',
            'genre': '',
            'year': '',
            'track': '',
            'albumartist': '',
            'duration': 0,
            'bitrate': 0,
            'has_cover': False
        }
        
        try:
            # Get basic info
            if hasattr(audio_file, 'info'):
                metadata['duration'] = getattr(audio_file.info, 'length', 0)
                metadata['bitrate'] = getattr(audio_file.info, 'bitrate', 0)
            
            # Extract tags based on file type
            if isinstance(audio_file, MP3):
                metadata.update(self._extract_mp3_tags(audio_file))
            elif isinstance(audio_file, FLAC):
                metadata.update(self._extract_flac_tags(audio_file))
            elif isinstance(audio_file, MP4):
                metadata.update(self._extract_mp4_tags(audio_file))
            else:
                # Generic extraction for other formats
                metadata.update(self._extract_generic_tags(audio_file))
                
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
        
        return metadata
    
    def _extract_mp3_tags(self, audio_file: MP3) -> Dict[str, Any]:
        """استخراج تگ‌های MP3"""
        tags = {}
        
        if audio_file.tags:
            tags['title'] = str(audio_file.tags.get('TIT2', [''])[0])
            tags['artist'] = str(audio_file.tags.get('TPE1', [''])[0])
            tags['album'] = str(audio_file.tags.get('TALB', [''])[0])
            tags['genre'] = str(audio_file.tags.get('TCON', [''])[0])
            tags['year'] = str(audio_file.tags.get('TDRC', [''])[0])
            tags['track'] = str(audio_file.tags.get('TRCK', [''])[0])
            tags['albumartist'] = str(audio_file.tags.get('TPE2', [''])[0])
            # Check for any APIC frame (cover art)
            has_apic = False
            for key in audio_file.tags.keys():
                if key.startswith('APIC'):
                    has_apic = True
                    break
            tags['has_cover'] = has_apic
        
        return tags
    
    def _extract_flac_tags(self, audio_file: FLAC) -> Dict[str, Any]:
        """استخراج تگ‌های FLAC"""
        tags = {}
        
        if audio_file.tags:
            tags['title'] = audio_file.tags.get('TITLE', [''])[0]
            tags['artist'] = audio_file.tags.get('ARTIST', [''])[0]
            tags['album'] = audio_file.tags.get('ALBUM', [''])[0]
            tags['genre'] = audio_file.tags.get('GENRE', [''])[0]
            tags['year'] = audio_file.tags.get('DATE', [''])[0]
            tags['track'] = audio_file.tags.get('TRACKNUMBER', [''])[0]
            tags['albumartist'] = audio_file.tags.get('ALBUMARTIST', [''])[0]
            tags['has_cover'] = bool(audio_file.pictures)
        
        return tags
    
    def _extract_mp4_tags(self, audio_file: MP4) -> Dict[str, Any]:
        """استخراج تگ‌های MP4/M4A"""
        tags = {}
        
        if audio_file.tags:
            tags['title'] = audio_file.tags.get('\xa9nam', [''])[0]
            tags['artist'] = audio_file.tags.get('\xa9ART', [''])[0]
            tags['album'] = audio_file.tags.get('\xa9alb', [''])[0]
            tags['genre'] = audio_file.tags.get('\xa9gen', [''])[0]
            tags['year'] = str(audio_file.tags.get('\xa9day', [''])[0])
            track_info = audio_file.tags.get('trkn', [(0, 0)])[0]
            tags['track'] = str(track_info[0]) if track_info[0] > 0 else ''
            tags['albumartist'] = audio_file.tags.get('aART', [''])[0]
            tags['has_cover'] = bool(audio_file.tags.get('covr'))
        
        return tags
    
    def _extract_generic_tags(self, audio_file: MutagenFile) -> Dict[str, Any]:
        """استخراج تگ‌های عمومی"""
        tags = {}
        
        if audio_file.tags:
            # Try common tag names
            for key, value in audio_file.tags.items():
                key_lower = key.lower()
                if 'title' in key_lower:
                    tags['title'] = str(value[0]) if isinstance(value, list) else str(value)
                elif 'artist' in key_lower and 'album' not in key_lower:
                    tags['artist'] = str(value[0]) if isinstance(value, list) else str(value)
                elif 'album' in key_lower and 'artist' not in key_lower:
                    tags['album'] = str(value[0]) if isinstance(value, list) else str(value)
                elif 'genre' in key_lower:
                    tags['genre'] = str(value[0]) if isinstance(value, list) else str(value)
                elif 'date' in key_lower or 'year' in key_lower:
                    tags['year'] = str(value[0]) if isinstance(value, list) else str(value)
                elif 'track' in key_lower:
                    tags['track'] = str(value[0]) if isinstance(value, list) else str(value)
        
        return tags
    
    def update_metadata(self, file_path: str, metadata: Dict[str, str], output_path: str = None) -> bool:
        """به‌روزرسانی متادیتا فایل صوتی"""
        try:
            if output_path and output_path != file_path:
                shutil.copy2(file_path, output_path)
                target_path = output_path
            else:
                target_path = file_path
            
            audio_file = self.load_file(target_path)
            if not audio_file:
                return False
            
            # Update tags based on file type
            if isinstance(audio_file, MP3):
                return self._update_mp3_tags(audio_file, metadata, target_path)
            elif isinstance(audio_file, FLAC):
                return self._update_flac_tags(audio_file, metadata, target_path)
            elif isinstance(audio_file, MP4):
                return self._update_mp4_tags(audio_file, metadata, target_path)
            else:
                return self._update_generic_tags(audio_file, metadata, target_path)
                
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            return False
    
    def _update_mp3_tags(self, audio_file: MP3, metadata: Dict[str, str], file_path: str) -> bool:
        """به‌روزرسانی تگ‌های MP3"""
        try:
            if audio_file.tags is None:
                audio_file.add_tags()
            
            if 'title' in metadata and metadata['title']:
                audio_file.tags['TIT2'] = TIT2(encoding=3, text=metadata['title'])
            if 'artist' in metadata and metadata['artist']:
                audio_file.tags['TPE1'] = TPE1(encoding=3, text=metadata['artist'])
            if 'album' in metadata and metadata['album']:
                audio_file.tags['TALB'] = TALB(encoding=3, text=metadata['album'])
            if 'genre' in metadata and metadata['genre']:
                audio_file.tags['TCON'] = TCON(encoding=3, text=metadata['genre'])
            if 'year' in metadata and metadata['year']:
                audio_file.tags['TDRC'] = TDRC(encoding=3, text=metadata['year'])
            if 'track' in metadata and metadata['track']:
                audio_file.tags['TRCK'] = TRCK(encoding=3, text=metadata['track'])
            if 'albumartist' in metadata and metadata['albumartist']:
                audio_file.tags['TPE2'] = TPE2(encoding=3, text=metadata['albumartist'])
            
            audio_file.save()
            return True
            
        except Exception as e:
            logger.error(f"Error updating MP3 tags: {e}")
            return False
    
    def _update_flac_tags(self, audio_file: FLAC, metadata: Dict[str, str], file_path: str) -> bool:
        """به‌روزرسانی تگ‌های FLAC"""
        try:
            if audio_file.tags is None:
                audio_file.add_tags()
            
            if 'title' in metadata and metadata['title']:
                audio_file.tags['TITLE'] = metadata['title']
            if 'artist' in metadata and metadata['artist']:
                audio_file.tags['ARTIST'] = metadata['artist']
            if 'album' in metadata and metadata['album']:
                audio_file.tags['ALBUM'] = metadata['album']
            if 'genre' in metadata and metadata['genre']:
                audio_file.tags['GENRE'] = metadata['genre']
            if 'year' in metadata and metadata['year']:
                audio_file.tags['DATE'] = metadata['year']
            if 'track' in metadata and metadata['track']:
                audio_file.tags['TRACKNUMBER'] = metadata['track']
            if 'albumartist' in metadata and metadata['albumartist']:
                audio_file.tags['ALBUMARTIST'] = metadata['albumartist']
            
            audio_file.save()
            return True
            
        except Exception as e:
            logger.error(f"Error updating FLAC tags: {e}")
            return False
    
    def _update_mp4_tags(self, audio_file: MP4, metadata: Dict[str, str], file_path: str) -> bool:
        """به‌روزرسانی تگ‌های MP4"""
        try:
            if audio_file.tags is None:
                audio_file.add_tags()
            
            if 'title' in metadata and metadata['title']:
                audio_file.tags['\xa9nam'] = metadata['title']
            if 'artist' in metadata and metadata['artist']:
                audio_file.tags['\xa9ART'] = metadata['artist']
            if 'album' in metadata and metadata['album']:
                audio_file.tags['\xa9alb'] = metadata['album']
            if 'genre' in metadata and metadata['genre']:
                audio_file.tags['\xa9gen'] = metadata['genre']
            if 'year' in metadata and metadata['year']:
                audio_file.tags['\xa9day'] = metadata['year']
            if 'track' in metadata and metadata['track']:
                try:
                    track_num = int(metadata['track'])
                    audio_file.tags['trkn'] = [(track_num, 0)]
                except ValueError:
                    pass
            if 'albumartist' in metadata and metadata['albumartist']:
                audio_file.tags['aART'] = metadata['albumartist']
            
            audio_file.save()
            return True
            
        except Exception as e:
            logger.error(f"Error updating MP4 tags: {e}")
            return False
    
    def _update_generic_tags(self, audio_file: MutagenFile, metadata: Dict[str, str], file_path: str) -> bool:
        """به‌روزرسانی تگ‌های عمومی"""
        try:
            if audio_file.tags is None:
                audio_file.add_tags()
            
            # Use generic tag names
            tag_mapping = {
                'title': 'TITLE',
                'artist': 'ARTIST', 
                'album': 'ALBUM',
                'genre': 'GENRE',
                'year': 'DATE',
                'track': 'TRACKNUMBER',
                'albumartist': 'ALBUMARTIST'
            }
            
            for key, value in metadata.items():
                if key in tag_mapping and value:
                    audio_file.tags[tag_mapping[key]] = value
            
            audio_file.save()
            return True
            
        except Exception as e:
            logger.error(f"Error updating generic tags: {e}")
            return False
    
    def add_cover_art(self, file_path: str, cover_path: str, output_path: str = None) -> bool:
        """اضافه کردن کاور آرت به فایل صوتی"""
        try:
            if output_path and output_path != file_path:
                shutil.copy2(file_path, output_path)
                target_path = output_path
            else:
                target_path = file_path
            
            audio_file = self.load_file(target_path)
            if not audio_file:
                return False
            
            # Read and process cover image
            with open(cover_path, 'rb') as cover_file:
                cover_data = cover_file.read()
            
            # Get image format
            img = Image.open(cover_path)
            img_format = img.format.lower()
            
            if isinstance(audio_file, MP3):
                return self._add_mp3_cover(audio_file, cover_data, img_format, target_path)
            elif isinstance(audio_file, FLAC):
                return self._add_flac_cover(audio_file, cover_data, img_format, target_path)
            elif isinstance(audio_file, MP4):
                return self._add_mp4_cover(audio_file, cover_data, img_format, target_path)
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding cover art: {e}")
            return False
    
    def _add_mp3_cover(self, audio_file: MP3, cover_data: bytes, img_format: str, file_path: str) -> bool:
        """اضافه کردن کاور به MP3"""
        try:
            if audio_file.tags is None:
                audio_file.add_tags()
            
            # Remove existing covers
            audio_file.tags.delall('APIC')
            
            # Add new cover
            audio_file.tags['APIC'] = APIC(
                encoding=3,
                mime=f'image/{img_format}',
                type=3,  # Cover (front)
                desc='Cover',
                data=cover_data
            )
            
            audio_file.save()
            return True
            
        except Exception as e:
            logger.error(f"Error adding MP3 cover: {e}")
            return False
    
    def _add_flac_cover(self, audio_file: FLAC, cover_data: bytes, img_format: str, file_path: str) -> bool:
        """اضافه کردن کاور به FLAC"""
        try:
            # Clear existing pictures
            audio_file.clear_pictures()
            
            # Create new picture
            picture = Picture()
            picture.type = 3  # Cover (front)
            picture.mime = f'image/{img_format}'
            picture.desc = 'Cover'
            picture.data = cover_data
            
            audio_file.add_picture(picture)
            audio_file.save()
            return True
            
        except Exception as e:
            logger.error(f"Error adding FLAC cover: {e}")
            return False
    
    def _add_mp4_cover(self, audio_file: MP4, cover_data: bytes, img_format: str, file_path: str) -> bool:
        """اضافه کردن کاور به MP4"""
        try:
            if audio_file.tags is None:
                audio_file.add_tags()
            
            # Determine cover format
            if img_format in ['jpeg', 'jpg']:
                cover_format = MP4Cover.FORMAT_JPEG
            elif img_format == 'png':
                cover_format = MP4Cover.FORMAT_PNG
            else:
                cover_format = MP4Cover.FORMAT_JPEG
            
            audio_file.tags['covr'] = [MP4Cover(cover_data, cover_format)]
            audio_file.save()
            return True
            
        except Exception as e:
            logger.error(f"Error adding MP4 cover: {e}")
            return False
    
    def remove_cover_art(self, file_path: str, output_path: str = None) -> bool:
        """حذف کاور آرت از فایل صوتی"""
        try:
            if output_path and output_path != file_path:
                shutil.copy2(file_path, output_path)
                target_path = output_path
            else:
                target_path = file_path
            
            audio_file = self.load_file(target_path)
            if not audio_file:
                return False
            
            if isinstance(audio_file, MP3):
                if audio_file.tags:
                    audio_file.tags.delall('APIC')
                    audio_file.save()
            elif isinstance(audio_file, FLAC):
                audio_file.clear_pictures()
                audio_file.save()
            elif isinstance(audio_file, MP4):
                if audio_file.tags and 'covr' in audio_file.tags:
                    del audio_file.tags['covr']
                    audio_file.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing cover art: {e}")
            return False
    
    def extract_cover_art(self, file_path: str, output_path: str) -> bool:
        """استخراج کاور آرت از فایل صوتی"""
        try:
            audio_file = self.load_file(file_path)
            if not audio_file:
                return False
            
            cover_data = None
            
            if isinstance(audio_file, MP3):
                if audio_file.tags:
                    apic = audio_file.tags.get('APIC:')
                    if apic:
                        cover_data = apic.data
            elif isinstance(audio_file, FLAC):
                if audio_file.pictures:
                    cover_data = audio_file.pictures[0].data
            elif isinstance(audio_file, MP4):
                if audio_file.tags and 'covr' in audio_file.tags:
                    cover_data = audio_file.tags['covr'][0]
            
            if cover_data:
                with open(output_path, 'wb') as f:
                    f.write(cover_data)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error extracting cover art: {e}")
            return False
    
    def generate_filename(self, metadata: Dict[str, str], template: str = "{artist} - {title}") -> str:
        """تولید نام فایل بر اساس متادیتا"""
        try:
            # Clean metadata values
            clean_metadata = {}
            for key, value in metadata.items():
                if value:
                    # Remove invalid filename characters
                    clean_value = str(value).strip()
                    for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
                        clean_value = clean_value.replace(char, '')
                    clean_metadata[key] = clean_value
                else:
                    clean_metadata[key] = 'Unknown'
            
            # Format filename
            filename = template.format(**clean_metadata)
            
            # Ensure filename is not too long
            if len(filename) > 200:
                filename = filename[:200]
            
            return filename
            
        except Exception as e:
            logger.error(f"Error generating filename: {e}")
            return "output"