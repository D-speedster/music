import os
import tempfile
from typing import Optional, Dict, Any, Tuple
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, TDRC, TRCK
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover

# Conditional import for pydub (may not work in Python 3.13)
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None

# Conditional import for PIL
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

import io

class AudioProcessor:
    """Handle audio file metadata editing and format conversion"""
    
    def __init__(self):
        self.supported_formats = ['.mp3', '.flac', '.wav', '.m4a', '.ogg', '.aac']
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from audio file"""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                return {}
            
            metadata = {
                'title': '',
                'artist': '',
                'album': '',
                'genre': '',
                'year': '',
                'track': '',
                'has_cover': False,
                'format': os.path.splitext(file_path)[1].lower(),
                'duration': getattr(audio_file.info, 'length', 0),
                'bitrate': getattr(audio_file.info, 'bitrate', 0)
            }
            
            # Extract metadata based on file format
            if hasattr(audio_file, 'tags') and audio_file.tags:
                tags = audio_file.tags
                
                if file_path.lower().endswith('.mp3'):
                    metadata.update({
                        'title': str(tags.get('TIT2', [''])[0]) if tags.get('TIT2') else '',
                        'artist': str(tags.get('TPE1', [''])[0]) if tags.get('TPE1') else '',
                        'album': str(tags.get('TALB', [''])[0]) if tags.get('TALB') else '',
                        'genre': str(tags.get('TCON', [''])[0]) if tags.get('TCON') else '',
                        'year': str(tags.get('TDRC', [''])[0]) if tags.get('TDRC') else '',
                        'track': str(tags.get('TRCK', [''])[0]) if tags.get('TRCK') else '',
                        'has_cover': 'APIC:' in tags or any(key.startswith('APIC') for key in tags.keys())
                    })
                
                elif file_path.lower().endswith('.flac'):
                    metadata.update({
                        'title': tags.get('TITLE', [''])[0] if tags.get('TITLE') else '',
                        'artist': tags.get('ARTIST', [''])[0] if tags.get('ARTIST') else '',
                        'album': tags.get('ALBUM', [''])[0] if tags.get('ALBUM') else '',
                        'genre': tags.get('GENRE', [''])[0] if tags.get('GENRE') else '',
                        'year': tags.get('DATE', [''])[0] if tags.get('DATE') else '',
                        'track': tags.get('TRACKNUMBER', [''])[0] if tags.get('TRACKNUMBER') else '',
                        'has_cover': len(audio_file.pictures) > 0
                    })
                
                elif file_path.lower().endswith('.m4a'):
                    metadata.update({
                        'title': tags.get('©nam', [''])[0] if tags.get('©nam') else '',
                        'artist': tags.get('©ART', [''])[0] if tags.get('©ART') else '',
                        'album': tags.get('©alb', [''])[0] if tags.get('©alb') else '',
                        'genre': tags.get('©gen', [''])[0] if tags.get('©gen') else '',
                        'year': str(tags.get('©day', [''])[0]) if tags.get('©day') else '',
                        'track': str(tags.get('trkn', [0])[0][0]) if tags.get('trkn') else '',
                        'has_cover': 'covr' in tags
                    })
            
            return metadata
            
        except Exception as e:
            print(f"Error reading metadata: {e}")
            return {}
    
    def update_metadata(self, file_path: str, metadata: Dict[str, str]) -> bool:
        """Update metadata in audio file"""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                return False
            
            # Ensure tags exist
            if audio_file.tags is None:
                audio_file.add_tags()
            
            if file_path.lower().endswith('.mp3'):
                self._update_mp3_metadata(audio_file, metadata)
            elif file_path.lower().endswith('.flac'):
                self._update_flac_metadata(audio_file, metadata)
            elif file_path.lower().endswith('.m4a'):
                self._update_m4a_metadata(audio_file, metadata)
            
            audio_file.save()
            return True
            
        except Exception as e:
            print(f"Error updating metadata: {e}")
            return False
    
    def _update_mp3_metadata(self, audio_file, metadata: Dict[str, str]):
        """Update MP3 metadata"""
        tags = audio_file.tags
        
        if metadata.get('title'):
            tags['TIT2'] = TIT2(encoding=3, text=metadata['title'])
        if metadata.get('artist'):
            tags['TPE1'] = TPE1(encoding=3, text=metadata['artist'])
        if metadata.get('album'):
            tags['TALB'] = TALB(encoding=3, text=metadata['album'])
        if metadata.get('genre'):
            tags['TCON'] = TCON(encoding=3, text=metadata['genre'])
        if metadata.get('year'):
            tags['TDRC'] = TDRC(encoding=3, text=metadata['year'])
        if metadata.get('track'):
            tags['TRCK'] = TRCK(encoding=3, text=metadata['track'])
    
    def _update_flac_metadata(self, audio_file, metadata: Dict[str, str]):
        """Update FLAC metadata"""
        tags = audio_file.tags
        
        if metadata.get('title'):
            tags['TITLE'] = metadata['title']
        if metadata.get('artist'):
            tags['ARTIST'] = metadata['artist']
        if metadata.get('album'):
            tags['ALBUM'] = metadata['album']
        if metadata.get('genre'):
            tags['GENRE'] = metadata['genre']
        if metadata.get('year'):
            tags['DATE'] = metadata['year']
        if metadata.get('track'):
            tags['TRACKNUMBER'] = metadata['track']
    
    def _update_m4a_metadata(self, audio_file, metadata: Dict[str, str]):
        """Update M4A metadata"""
        tags = audio_file.tags
        
        if metadata.get('title'):
            tags['©nam'] = [metadata['title']]
        if metadata.get('artist'):
            tags['©ART'] = [metadata['artist']]
        if metadata.get('album'):
            tags['©alb'] = [metadata['album']]
        if metadata.get('genre'):
            tags['©gen'] = [metadata['genre']]
        if metadata.get('year'):
            tags['©day'] = [metadata['year']]
        if metadata.get('track'):
            tags['trkn'] = [(int(metadata['track']), 0)]
    
    def add_cover_art(self, file_path: str, cover_data: bytes, mime_type: str = 'image/jpeg') -> bool:
        """Add cover art to audio file"""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                return False
            
            if file_path.lower().endswith('.mp3'):
                if audio_file.tags is None:
                    audio_file.add_tags()
                
                audio_file.tags['APIC'] = APIC(
                    encoding=3,
                    mime=mime_type,
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=cover_data
                )
            
            elif file_path.lower().endswith('.flac'):
                picture = Picture()
                picture.type = 3  # Cover (front)
                picture.mime = mime_type
                picture.desc = 'Cover'
                picture.data = cover_data
                
                audio_file.clear_pictures()
                audio_file.add_picture(picture)
            
            elif file_path.lower().endswith('.m4a'):
                if audio_file.tags is None:
                    audio_file.add_tags()
                
                if mime_type == 'image/jpeg':
                    format_type = MP4Cover.FORMAT_JPEG
                else:
                    format_type = MP4Cover.FORMAT_PNG
                
                audio_file.tags['covr'] = [MP4Cover(cover_data, format_type)]
            
            audio_file.save()
            return True
            
        except Exception as e:
            print(f"Error adding cover art: {e}")
            return False
    
    def remove_cover_art(self, file_path: str) -> bool:
        """Remove cover art from audio file"""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                return False
            
            if file_path.lower().endswith('.mp3'):
                if audio_file.tags:
                    # Remove all APIC frames
                    keys_to_remove = [key for key in audio_file.tags.keys() if key.startswith('APIC')]
                    for key in keys_to_remove:
                        del audio_file.tags[key]
            
            elif file_path.lower().endswith('.flac'):
                audio_file.clear_pictures()
            
            elif file_path.lower().endswith('.m4a'):
                if audio_file.tags and 'covr' in audio_file.tags:
                    del audio_file.tags['covr']
            
            audio_file.save()
            return True
            
        except Exception as e:
            print(f"Error removing cover art: {e}")
            return False
    
    def extract_cover_art(self, file_path: str) -> Optional[bytes]:
        """Extract cover art from audio file"""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                return None
            
            if file_path.lower().endswith('.mp3'):
                if audio_file.tags:
                    for key in audio_file.tags.keys():
                        if key.startswith('APIC'):
                            return audio_file.tags[key].data
            
            elif file_path.lower().endswith('.flac'):
                if audio_file.pictures:
                    return audio_file.pictures[0].data
            
            elif file_path.lower().endswith('.m4a'):
                if audio_file.tags and 'covr' in audio_file.tags:
                    return bytes(audio_file.tags['covr'][0])
            
            return None
            
        except Exception as e:
            print(f"Error extracting cover art: {e}")
            return None
    
    def convert_format(self, input_path: str, output_path: str, target_format: str, bitrate: Optional[int] = None) -> bool:
        """Convert audio file to different format"""
        if not PYDUB_AVAILABLE:
            print("❌ تبدیل فرمت در دسترس نیست - pydub نصب نشده است")
            print("💡 برای استفاده از این قابلیت، pydub را نصب کنید:")
            print("   pip install pydub")
            return False
            
        try:
            audio = AudioSegment.from_file(input_path)
            
            export_params = {}
            if target_format.lower() == 'mp3':
                export_params['format'] = 'mp3'
                if bitrate:
                    export_params['bitrate'] = f"{bitrate}k"
            elif target_format.lower() == 'flac':
                export_params['format'] = 'flac'
            elif target_format.lower() == 'wav':
                export_params['format'] = 'wav'
            elif target_format.lower() == 'm4a':
                export_params['format'] = 'mp4'
                export_params['codec'] = 'aac'
                if bitrate:
                    export_params['bitrate'] = f"{bitrate}k"
            
            audio.export(output_path, **export_params)
            return True
            
        except Exception as e:
            print(f"Error converting format: {e}")
            return False
    
    def generate_filename(self, metadata: Dict[str, str], template: str = "{artist} - {title}") -> str:
        """Generate filename based on metadata and template"""
        try:
            # Clean metadata values
            clean_metadata = {}
            for key, value in metadata.items():
                if value:
                    # Remove invalid filename characters
                    clean_value = str(value).replace('/', '_').replace('\\', '_').replace(':', '_')
                    clean_value = clean_value.replace('*', '_').replace('?', '_').replace('"', '_')
                    clean_value = clean_value.replace('<', '_').replace('>', '_').replace('|', '_')
                    clean_metadata[key] = clean_value
                else:
                    clean_metadata[key] = 'Unknown'
            
            filename = template.format(**clean_metadata)
            return filename
            
        except Exception as e:
            print(f"Error generating filename: {e}")
            return "output"