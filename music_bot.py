import os
import asyncio
import logging
from typing import Dict, Optional
from telethon import TelegramClient, events, Button
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeFilename
import aiofiles
from config import Config
from audio_editor import AudioEditor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MusicBot:
    """ربات ویرایش فایل‌های صوتی با Telethon"""
    
    def __init__(self):
        self.config = Config()
        self.config.validate_config()
        
        # Initialize Telethon client
        self.client = TelegramClient(
            'music_bot_session',
            self.config.API_ID,
            self.config.API_HASH
        )
        
        # Initialize audio editor
        self.audio_editor = AudioEditor()
        
        # User sessions for tracking editing state
        self.user_sessions: Dict[int, Dict] = {}
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """ثبت handlers برای رویدادهای مختلف"""
        
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await self.handle_start(event)
        
        @self.client.on(events.NewMessage(pattern='/help'))
        async def help_handler(event):
            await self.handle_help(event)
        
        @self.client.on(events.NewMessage(pattern='/cancel'))
        async def cancel_handler(event):
            await self.handle_cancel(event)
        
        @self.client.on(events.NewMessage(func=lambda e: e.document))
        async def document_handler(event):
            await self.handle_document(event)
        
        @self.client.on(events.NewMessage(func=lambda e: e.photo))
        async def photo_handler(event):
            await self.handle_photo(event)
        
        @self.client.on(events.CallbackQuery)
        async def callback_handler(event):
            await self.handle_callback(event)
        
        @self.client.on(events.NewMessage(func=lambda e: e.text and not e.text.startswith('/')))
        async def text_handler(event):
            await self.handle_text(event)
    
    async def handle_start(self, event):
        """پردازش دستور /start"""
        user_id = event.sender_id
        
        welcome_text = """
🎵 **خوش آمدید به ربات ویرایش فایل‌های صوتی!**

این ربات امکانات زیر را ارائه می‌دهد:

🎶 **ویرایش متادیتا:**
• تغییر نام آهنگ (Title)
• تغییر نام هنرمند (Artist)  
• تغییر آلبوم (Album)
• تغییر ژانر (Genre)
• تغییر سال انتشار (Year)
• تغییر شماره ترک (Track Number)

🖼️ **ویرایش کاور:**
• اضافه کردن کاور جدید
• حذف کاور موجود
• جایگزینی کاور
• استخراج کاور موجود

📁 **تنظیمات فایل:**
• تغییر نام فایل خروجی
• پشتیبانی از فرمت‌های مختلف

**برای شروع، فایل صوتی خود را ارسال کنید!**

/help - راهنمای کامل
/cancel - لغو عملیات جاری
        """
        
        await event.respond(welcome_text)
    
    async def handle_help(self, event):
        """پردازش دستور /help"""
        help_text = """
📖 **راهنمای استفاده از ربات**

**مراحل ویرایش:**
1️⃣ فایل صوتی خود را ارسال کنید
2️⃣ از منوی ظاهر شده، نوع ویرایش را انتخاب کنید
3️⃣ اطلاعات جدید را وارد کنید
4️⃣ فایل ویرایش شده را دریافت کنید

**فرمت‌های پشتیبانی شده:**
🎵 MP3, FLAC, WAV, M4A, OGG, AAC

**حداکثر حجم فایل:** 2GB

**نکات مهم:**
• برای لغو عملیات از /cancel استفاده کنید
• می‌توانید چندین تغییر را همزمان اعمال کنید
• کیفیت فایل حفظ می‌شود

**پشتیبانی:** @YourSupportUsername
        """
        
        await event.respond(help_text)
    
    async def handle_cancel(self, event):
        """لغو عملیات جاری کاربر"""
        user_id = event.sender_id
        
        if user_id in self.user_sessions:
            # Clean up user session
            session = self.user_sessions[user_id]
            if 'temp_file' in session and os.path.exists(session['temp_file']):
                os.remove(session['temp_file'])
            
            del self.user_sessions[user_id]
            await event.respond("✅ عملیات لغو شد.")
        else:
            await event.respond("❌ هیچ عملیاتی در حال انجام نیست.")
    
    async def handle_document(self, event):
        """پردازش فایل‌های ارسالی"""
        user_id = event.sender_id
        document = event.document
        
        if not document:
            return
        
        # Check file size
        if document.size > self.config.MAX_FILE_SIZE:
            await event.respond(f"❌ حجم فایل بیش از حد مجاز است. حداکثر: {self.config.MAX_FILE_SIZE // (1024*1024)}MB")
            return
        
        # Check if it's an audio file
        file_name = None
        is_audio = False
        
        for attr in document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                file_name = attr.file_name
                break
            elif isinstance(attr, DocumentAttributeAudio):
                is_audio = True
                if hasattr(attr, 'title') and attr.title:
                    file_name = f"{attr.title}.mp3"
        
        if not file_name:
            file_name = f"audio_{document.id}"
        
        # Check file extension
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext not in self.config.SUPPORTED_AUDIO_FORMATS and not is_audio:
            await event.respond(
                f"❌ فرمت فایل پشتیبانی نمی‌شود.\n"
                f"فرمت‌های مجاز: {', '.join(self.config.SUPPORTED_AUDIO_FORMATS)}"
            )
            return
        
        # Send processing message
        processing_msg = await event.respond("⏳ در حال دانلود و پردازش فایل...")
        
        try:
            # Download file
            temp_file_path = os.path.join(self.config.TEMP_DIR, f"temp_{user_id}_{file_name}")
            await self.client.download_media(document, temp_file_path)
            
            # Extract metadata
            metadata = self.audio_editor.get_metadata(temp_file_path)
            
            # Create user session
            self.user_sessions[user_id] = {
                'temp_file': temp_file_path,
                'original_filename': file_name,
                'metadata': metadata,
                'editing_state': 'main_menu'
            }
            
            # Show main menu
            await self.show_main_menu(event, processing_msg)
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            await processing_msg.edit("❌ خطا در پردازش فایل. لطفاً دوباره تلاش کنید.")
            
            # Clean up
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    async def show_main_menu(self, event, message_to_edit=None):
        """نمایش منوی اصلی ویرایش"""
        user_id = event.sender_id
        
        if user_id not in self.user_sessions:
            await event.respond("❌ لطفاً ابتدا فایل صوتی ارسال کنید.")
            return
        
        session = self.user_sessions[user_id]
        metadata = session['metadata']
        
        # Create info text
        info_text = f"""
🎵 **اطلاعات فایل:**

📝 **نام:** {metadata.get('title', 'نامشخص')}
👤 **هنرمند:** {metadata.get('artist', 'نامشخص')}
💿 **آلبوم:** {metadata.get('album', 'نامشخص')}
🎭 **ژانر:** {metadata.get('genre', 'نامشخص')}
📅 **سال:** {metadata.get('year', 'نامشخص')}
🔢 **ترک:** {metadata.get('track', 'نامشخص')}
⏱️ **مدت:** {int(metadata.get('duration', 0))} ثانیه
🖼️ **کاور:** {'✅ دارد' if metadata.get('has_cover') else '❌ ندارد'}

**چه کاری می‌خواهید انجام دهید؟**
        """
        
        # Create buttons
        buttons = [
            [Button.inline("✏️ ویرایش متادیتا", b"edit_metadata")],
            [Button.inline("🖼️ ویرایش کاور", b"edit_cover")],
            [Button.inline("📁 تغییر نام فایل", b"change_filename")],
            [Button.inline("💾 ذخیره و دانلود", b"save_download")],
            [Button.inline("❌ لغو", b"cancel")]
        ]
        
        if message_to_edit:
            await message_to_edit.edit(info_text, buttons=buttons)
        else:
            await event.respond(info_text, buttons=buttons)
    
    async def handle_callback(self, event):
        """پردازش callback query ها"""
        user_id = event.sender_id
        data = event.data.decode('utf-8')
        
        if user_id not in self.user_sessions:
            await event.answer("❌ لطفاً ابتدا فایل صوتی ارسال کنید.", alert=True)
            return
        
        session = self.user_sessions[user_id]
        
        if data == "edit_metadata":
            await self.show_metadata_menu(event)
        elif data == "edit_cover":
            await self.show_cover_menu(event)
        elif data == "change_filename":
            await self.start_filename_change(event)
        elif data == "save_download":
            await self.save_and_download(event)
        elif data == "cancel":
            await self.handle_cancel_callback(event)
        elif data == "back_main":
            await self.show_main_menu(event, event.query.message)
        elif data.startswith("edit_"):
            await self.start_metadata_edit(event, data)
        elif data.startswith("cover_"):
            await self.handle_cover_action(event, data)
        
        await event.answer()
    
    async def show_metadata_menu(self, event):
        """نمایش منوی ویرایش متادیتا"""
        text = "✏️ **کدام قسمت را می‌خواهید ویرایش کنید؟**"
        
        buttons = [
            [Button.inline("📝 نام آهنگ (Title)", b"edit_title")],
            [Button.inline("👤 هنرمند (Artist)", b"edit_artist")],
            [Button.inline("💿 آلبوم (Album)", b"edit_album")],
            [Button.inline("🎭 ژانر (Genre)", b"edit_genre")],
            [Button.inline("📅 سال انتشار (Year)", b"edit_year")],
            [Button.inline("🔢 شماره ترک (Track)", b"edit_track")],
            [Button.inline("🔙 بازگشت", b"back_main")]
        ]
        
        await event.edit(text, buttons=buttons)
    
    async def show_cover_menu(self, event):
        """نمایش منوی ویرایش کاور"""
        user_id = event.sender_id
        session = self.user_sessions[user_id]
        has_cover = session['metadata'].get('has_cover', False)
        
        text = "🖼️ **ویرایش کاور آلبوم**"
        
        buttons = [
            [Button.inline("➕ اضافه کردن کاور جدید", b"cover_add")],
        ]
        
        if has_cover:
            buttons.extend([
                [Button.inline("🔄 جایگزینی کاور", b"cover_replace")],
                [Button.inline("📥 استخراج کاور موجود", b"cover_extract")],
                [Button.inline("🗑️ حذف کاور", b"cover_remove")]
            ])
        
        buttons.append([Button.inline("🔙 بازگشت", b"back_main")])
        
        await event.edit(text, buttons=buttons)
    
    async def start_metadata_edit(self, event, edit_type):
        """شروع ویرایش متادیتا"""
        user_id = event.sender_id
        session = self.user_sessions[user_id]
        
        field_map = {
            'edit_title': ('title', 'نام آهنگ'),
            'edit_artist': ('artist', 'نام هنرمند'),
            'edit_album': ('album', 'نام آلبوم'),
            'edit_genre': ('genre', 'ژانر'),
            'edit_year': ('year', 'سال انتشار'),
            'edit_track': ('track', 'شماره ترک')
        }
        
        if edit_type not in field_map:
            return
        
        field, field_name = field_map[edit_type]
        current_value = session['metadata'].get(field, 'تنظیم نشده')
        
        session['editing_state'] = f'editing_{field}'
        
        text = f"""
✏️ **ویرایش {field_name}**

**مقدار فعلی:** {current_value}

لطفاً مقدار جدید را وارد کنید:
        """
        
        buttons = [[Button.inline("❌ لغو", b"edit_metadata")]]
        
        await event.edit(text, buttons=buttons)
    
    async def start_filename_change(self, event):
        """شروع تغییر نام فایل"""
        user_id = event.sender_id
        session = self.user_sessions[user_id]
        session['editing_state'] = 'editing_filename'
        
        current_name = session.get('custom_filename', session['original_filename'])
        
        text = f"""
📁 **تغییر نام فایل خروجی**

**نام فعلی:** {current_name}

**قالب‌های پیشنهادی:**
• `{{artist}} - {{title}}`
• `{{title}} ({{year}})`
• `{{album}} - {{track}} - {{title}}`

**متغیرهای قابل استفاده:**
• `{{title}}` - نام آهنگ
• `{{artist}}` - نام هنرمند
• `{{album}}` - نام آلبوم
• `{{year}}` - سال انتشار
• `{{track}}` - شماره ترک
• `{{genre}}` - ژانر

لطفاً نام یا قالب جدید را وارد کنید:
        """
        
        buttons = [[Button.inline("❌ لغو", b"back_main")]]
        
        await event.edit(text, buttons=buttons)
    
    async def handle_cover_action(self, event, action):
        """پردازش عملیات کاور"""
        user_id = event.sender_id
        session = self.user_sessions[user_id]
        
        if action == "cover_add" or action == "cover_replace":
            session['editing_state'] = 'waiting_cover'
            session['cover_action'] = action
            text = "🖼️ لطفاً تصویر کاور جدید را ارسال کنید."
            buttons = [[Button.inline("❌ لغو", b"edit_cover")]]
            await event.edit(text, buttons=buttons)
            
        elif action == "cover_extract":
            await self.extract_cover(event)
            
        elif action == "cover_remove":
            await self.remove_cover(event)
    
    async def handle_text(self, event):
        """پردازش پیام‌های متنی"""
        user_id = event.sender_id
        
        if user_id not in self.user_sessions:
            return
        
        session = self.user_sessions[user_id]
        state = session.get('editing_state', '')
        text = event.text.strip()
        
        if state.startswith('editing_'):
            field = state.replace('editing_', '')
            
            if field == 'filename':
                await self.update_filename(event, text)
            else:
                await self.update_metadata_field(event, field, text)
    
    async def update_metadata_field(self, event, field, value):
        """به‌روزرسانی فیلد متادیتا"""
        user_id = event.sender_id
        session = self.user_sessions[user_id]
        
        # Update metadata
        session['metadata'][field] = value
        session['editing_state'] = 'main_menu'
        
        field_names = {
            'title': 'نام آهنگ',
            'artist': 'نام هنرمند',
            'album': 'نام آلبوم',
            'genre': 'ژانر',
            'year': 'سال انتشار',
            'track': 'شماره ترک'
        }
        
        field_name = field_names.get(field, field)
        
        await event.respond(f"✅ {field_name} به '{value}' تغییر یافت.")
        await self.show_main_menu(event)
    
    async def update_filename(self, event, template):
        """به‌روزرسانی نام فایل"""
        user_id = event.sender_id
        session = self.user_sessions[user_id]
        
        try:
            # Generate filename using template
            filename = self.audio_editor.generate_filename(session['metadata'], template)
            
            # Add original extension
            original_ext = os.path.splitext(session['original_filename'])[1]
            if not filename.endswith(original_ext):
                filename += original_ext
            
            session['custom_filename'] = filename
            session['editing_state'] = 'main_menu'
            
            await event.respond(f"✅ نام فایل به '{filename}' تغییر یافت.")
            await self.show_main_menu(event)
            
        except Exception as e:
            logger.error(f"Error updating filename: {e}")
            await event.respond("❌ خطا در تولید نام فایل. لطفاً قالب صحیح وارد کنید.")
    
    async def extract_cover(self, event):
        """استخراج کاور موجود"""
        user_id = event.sender_id
        session = self.user_sessions[user_id]
        
        try:
            cover_path = os.path.join(self.config.TEMP_DIR, f"cover_{user_id}.jpg")
            
            if self.audio_editor.extract_cover_art(session['temp_file'], cover_path):
                await self.client.send_file(
                    event.chat_id,
                    cover_path,
                    caption="🖼️ کاور استخراج شده از فایل صوتی"
                )
                os.remove(cover_path)
            else:
                await event.respond("❌ کاوری برای استخراج یافت نشد.")
                
        except Exception as e:
            logger.error(f"Error extracting cover: {e}")
            await event.respond("❌ خطا در استخراج کاور.")
        
        await self.show_cover_menu(event)
    
    async def remove_cover(self, event):
        """حذف کاور موجود"""
        user_id = event.sender_id
        session = self.user_sessions[user_id]
        
        try:
            if self.audio_editor.remove_cover_art(session['temp_file']):
                session['metadata']['has_cover'] = False
                await event.respond("✅ کاور با موفقیت حذف شد.")
            else:
                await event.respond("❌ خطا در حذف کاور.")
                
        except Exception as e:
            logger.error(f"Error removing cover: {e}")
            await event.respond("❌ خطا در حذف کاور.")
        
        await self.show_cover_menu(event)
    
    async def save_and_download(self, event):
        """ذخیره و ارسال فایل ویرایش شده"""
        user_id = event.sender_id
        session = self.user_sessions[user_id]
        
        processing_msg = await event.respond("⏳ در حال ذخیره تغییرات...")
        
        try:
            # Generate output filename
            if 'custom_filename' in session:
                output_filename = session['custom_filename']
            else:
                output_filename = self.audio_editor.generate_filename(
                    session['metadata'],
                    "{artist} - {title}"
                )
                original_ext = os.path.splitext(session['original_filename'])[1]
                if not output_filename.endswith(original_ext):
                    output_filename += original_ext
            
            output_path = os.path.join(self.config.OUTPUT_DIR, output_filename)
            
            # Update metadata
            if self.audio_editor.update_metadata(
                session['temp_file'],
                session['metadata'],
                output_path
            ):
                # Send the file
                await self.client.send_file(
                    event.chat_id,
                    output_path,
                    caption=f"✅ فایل ویرایش شده آماده است!\n📁 **نام:** {output_filename}",
                    attributes=[DocumentAttributeFilename(output_filename)]
                )
                
                # Clean up
                os.remove(output_path)
                await processing_msg.delete()
                
                # Reset session
                if os.path.exists(session['temp_file']):
                    os.remove(session['temp_file'])
                del self.user_sessions[user_id]
                
            else:
                await processing_msg.edit("❌ خطا در ذخیره فایل.")
                
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            await processing_msg.edit("❌ خطا در پردازش فایل.")
    
    async def handle_cancel_callback(self, event):
        """پردازش لغو از طریق callback"""
        user_id = event.sender_id
        
        if user_id in self.user_sessions:
            session = self.user_sessions[user_id]
            if 'temp_file' in session and os.path.exists(session['temp_file']):
                os.remove(session['temp_file'])
            del self.user_sessions[user_id]
        
        await event.edit("✅ عملیات لغو شد.")
    
    async def handle_photo(self, event):
        """پردازش تصاویر کاور"""
        user_id = event.sender_id
        
        # Check if user has an active session
        if user_id not in self.user_sessions:
            await event.respond("❌ لطفاً ابتدا فایل صوتی ارسال کنید.")
            return
        
        session = self.user_sessions[user_id]
        
        # Check if user is waiting for cover
        if session.get('editing_state') != 'waiting_cover':
            await event.respond("❌ شما در حال انتظار برای کاور نیستید. لطفاً از منو گزینه ویرایش کاور را انتخاب کنید.")
            return
        
        try:
            # Send processing message
            processing_msg = await event.respond("⏳ در حال پردازش کاور...")
            
            # Download photo
            temp_cover_path = os.path.join(self.config.TEMP_DIR, f"temp_cover_{user_id}.jpg")
            await self.client.download_media(event.photo, temp_cover_path)
            
            # Get the action from session
            action = session.get('cover_action', 'add')
            temp_file = session['temp_file']
            
            if action in ['add', 'replace']:
                # Add/replace cover
                success = self.audio_editor.add_cover_art(temp_file, temp_cover_path)
                
                if success:
                    # Update metadata
                    session['metadata'] = self.audio_editor.get_metadata(temp_file)
                    session['editing_state'] = 'main_menu'
                    
                    await processing_msg.edit("✅ کاور با موفقیت اضافه شد!")
                    await self.show_main_menu(event)
                else:
                    await processing_msg.edit("❌ خطا در افزودن کاور. لطفاً دوباره تلاش کنید.")
            
            # Clean up temp cover file
            if os.path.exists(temp_cover_path):
                os.remove(temp_cover_path)
                
        except Exception as e:
            logger.error(f"Error processing cover: {e}")
            await event.respond("❌ خطا در پردازش کاور. لطفاً دوباره تلاش کنید.")
    
    async def start(self):
        """شروع ربات"""
        try:
            await self.client.start(bot_token=self.config.BOT_TOKEN)
            logger.info("🎵 Music Bot started successfully!")
            
            # Get bot info
            me = await self.client.get_me()
            logger.info(f"Bot username: @{me.username}")
            
            # Keep the bot running
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise

async def main():
    """تابع اصلی"""
    bot = MusicBot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())