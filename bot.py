import os
import asyncio
import time
import tempfile
import shutil
from typing import Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode
import aiofiles
from config import Config
from utils.audio_processor import AudioProcessor
from utils.batch_processor import BatchProcessor
from utils.admin_panel import AdminPanel

class MusicBot:
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.batch_processor = BatchProcessor()
        self.admin_panel = AdminPanel()
        self.user_sessions: Dict[int, Dict] = {}
        self.batch_sessions = {}  # For batch processing sessions
        Config.ensure_directories()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        user = update.effective_user
        
        # Log user activity
        await self.admin_panel.log_user_activity(
            user.id, user.username, user.first_name
        )
        
        welcome_text = """
🎵 **ربات ویرایش موزیک** 🎵

سلام! من می‌تونم فایل‌های صوتی شما رو ویرایش کنم.

**امکانات:**
• ویرایش تگ‌های ID3 (نام آهنگ، هنرمند، آلبوم و...)
• مدیریت کاور آلبوم (اضافه/حذف/تغییر)
• تبدیل فرمت صوتی
• تغییر کیفیت و بیت‌ریت
• نام‌گذاری شخصی‌سازی شده
• پردازش دسته‌ای چندین فایل

**فرمت‌های پشتیبانی شده:**
MP3, FLAC, WAV, M4A, OGG, AAC

برای شروع، فایل صوتی خود را ارسال کنید یا از دستورات زیر استفاده کنید:

/batch - پردازش دسته‌ای فایل‌ها
/stats - آمار شخصی شما
/help - راهنما

برای شروع، فایل صوتی خود را ارسال کنید! 🎶
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle audio file uploads"""
        user_id = update.effective_user.id
        
        # Check file size
        if update.message.audio:
            file_obj = update.message.audio
        elif update.message.document:
            file_obj = update.message.document
        else:
            await update.message.reply_text("❌ لطفاً یک فایل صوتی ارسال کنید.")
            return
        
        # Check user limits
        limits_check = self.admin_panel.check_user_limits(user_id, file_obj.file_size)
        if not limits_check['allowed']:
            await update.message.reply_text(f"❌ {limits_check['reason']}")
            return
        
        if file_obj.file_size > Config.MAX_FILE_SIZE_BYTES:
            await update.message.reply_text(
                f"❌ حجم فایل بیش از حد مجاز است. حداکثر: {Config.MAX_FILE_SIZE_MB}MB"
            )
            return
        
        # Check file format
        file_extension = os.path.splitext(file_obj.file_name or '')[1].lower()
        if file_extension not in Config.SUPPORTED_AUDIO_FORMATS:
            await update.message.reply_text(
                f"❌ فرمت فایل پشتیبانی نمی‌شود.\n"
                f"فرمت‌های مجاز: {', '.join(Config.SUPPORTED_AUDIO_FORMATS)}"
            )
            return
        
        # Download file
        status_msg = await update.message.reply_text("⏳ در حال دانلود فایل...")
        
        try:
            start_time = time.time()
            
            file = await context.bot.get_file(file_obj.file_id)
            temp_path = os.path.join(Config.TEMP_DIR, f"{user_id}_{file_obj.file_name}")
            await file.download_to_drive(temp_path)
            
            # Extract metadata
            metadata = self.audio_processor.get_metadata(temp_path)
            
            # Store session data
            self.user_sessions[user_id] = {
                'file_path': temp_path,
                'original_filename': file_obj.file_name,
                'file_size': file_obj.file_size,
                'format': file_extension,
                'metadata': metadata,
                'cover_data': None,
                'operations': []
            }
            
            processing_time = time.time() - start_time
            
            # Log file processing
            await self.admin_panel.log_file_processing(
                user_id=user_id,
                file_name=file_obj.file_name,
                file_size=file_obj.file_size,
                file_format=file_extension,
                operations=['upload'],
                processing_time=processing_time
            )
            
            await status_msg.edit_text("✅ فایل با موفقیت دریافت شد!")
            await self.show_main_menu(update, context)
            
        except Exception as e:
            await status_msg.edit_text(f"❌ خطا در پردازش فایل: {str(e)}")
            # Clean up
            if user_id in self.user_sessions:
                temp_path = self.user_sessions[user_id].get('file_path')
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                del self.user_sessions[user_id]
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main editing menu"""
        user_id = update.effective_user.id
        if user_id not in self.user_sessions:
            await update.message.reply_text("❌ ابتدا یک فایل صوتی ارسال کنید.")
            return
        
        session = self.user_sessions[user_id]
        metadata = session['metadata']
        
        info_text = f"""
📁 **اطلاعات فایل:**
🎵 نام آهنگ: `{metadata.get('title', 'نامشخص')}`
👤 هنرمند: `{metadata.get('artist', 'نامشخص')}`
💿 آلبوم: `{metadata.get('album', 'نامشخص')}`
🎭 ژانر: `{metadata.get('genre', 'نامشخص')}`
📅 سال: `{metadata.get('year', 'نامشخص')}`
🔢 شماره ترک: `{metadata.get('track', 'نامشخص')}`
🖼️ کاور: `{'دارد' if metadata.get('has_cover') else 'ندارد'}`
⏱️ مدت: `{int(metadata.get('duration', 0))//60}:{int(metadata.get('duration', 0))%60:02d}`
🎚️ بیت‌ریت: `{metadata.get('bitrate', 'نامشخص')} kbps`
        """
        
        keyboard = [
            [InlineKeyboardButton("✏️ ویرایش تگ‌ها", callback_data="edit_tags")],
            [InlineKeyboardButton("🖼️ مدیریت کاور", callback_data="manage_cover")],
            [InlineKeyboardButton("🔄 تبدیل فرمت", callback_data="convert_format")],
            [InlineKeyboardButton("📝 تنظیم نام فایل", callback_data="set_filename")],
            [InlineKeyboardButton("💾 ذخیره و دانلود", callback_data="save_download")],
            [InlineKeyboardButton("🗑️ حذف فایل", callback_data="delete_file")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                info_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                info_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        
        user_id = update.effective_user.id
        if user_id not in self.user_sessions:
            await query.answer()
            await query.edit_message_text("❌ جلسه منقضی شده. فایل جدید ارسال کنید.")
            return
        
        # Handle different callback types
        if query.data == "edit_tags":
            await query.answer()
            await self.show_tag_menu(update, context)
        elif query.data == "manage_cover":
            await query.answer()
            await self.show_cover_menu(update, context)
        elif query.data == "convert_format":
            await query.answer()
            await self.show_format_menu(update, context)
        elif query.data == "set_filename":
            await query.answer()
            await self.show_filename_menu(update, context)
        elif query.data == "save_download":
            await query.answer()
            await self.save_and_download(update, context)
        elif query.data == "delete_file":
            await query.answer()
            await self.delete_user_file(update, context)
        elif query.data == "back_main":
            await query.answer()
            await self.show_main_menu(update, context)
        elif query.data.startswith("edit_"):
            await query.answer()
            await self.handle_tag_edit(update, context)
        elif query.data.startswith("cover_"):
            await query.answer()
            await self.handle_cover_action(update, context)
        elif query.data.startswith("format_"):
            # Don't answer immediately for format conversion - it's handled in the method
            await self.handle_format_conversion(update, context)
    
    async def show_tag_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show tag editing menu"""
        keyboard = [
            [InlineKeyboardButton("🎵 نام آهنگ", callback_data="edit_title")],
            [InlineKeyboardButton("👤 هنرمند", callback_data="edit_artist")],
            [InlineKeyboardButton("💿 آلبوم", callback_data="edit_album")],
            [InlineKeyboardButton("🎭 ژانر", callback_data="edit_genre")],
            [InlineKeyboardButton("📅 سال", callback_data="edit_year")],
            [InlineKeyboardButton("🔢 شماره ترک", callback_data="edit_track")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            "کدام تگ را می‌خواهید ویرایش کنید؟",
            reply_markup=reply_markup
        )
    
    async def show_cover_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show cover art management menu"""
        user_id = update.effective_user.id
        session = self.user_sessions[user_id]
        has_cover = session['metadata'].get('has_cover', False)
        
        keyboard = []
        if has_cover:
            keyboard.append([InlineKeyboardButton("👁️ مشاهده کاور", callback_data="cover_view")])
            keyboard.append([InlineKeyboardButton("🗑️ حذف کاور", callback_data="cover_remove")])
        
        keyboard.extend([
            [InlineKeyboardButton("➕ اضافه کردن کاور", callback_data="cover_add")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            "مدیریت کاور آلبوم:",
            reply_markup=reply_markup
        )
    
    async def show_format_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show format conversion menu"""
        keyboard = [
            [InlineKeyboardButton("🎵 MP3", callback_data="format_mp3")],
            [InlineKeyboardButton("🎼 FLAC", callback_data="format_flac")],
            [InlineKeyboardButton("🔊 WAV", callback_data="format_wav")],
            [InlineKeyboardButton("📱 M4A", callback_data="format_m4a")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            "به کدام فرمت تبدیل شود؟",
            reply_markup=reply_markup
        )
    
    async def show_filename_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show filename template menu"""
        keyboard = [
            [InlineKeyboardButton("🎵 Title", callback_data="filename_{title}")],
            [InlineKeyboardButton("👤 Artist - Title", callback_data="filename_{artist} - {title}")],
            [InlineKeyboardButton("💿 Album - Title", callback_data="filename_{album} - {title}")],
            [InlineKeyboardButton("📝 سفارشی", callback_data="filename_custom")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            "الگوی نام‌گذاری فایل را انتخاب کنید:",
            reply_markup=reply_markup
        )
    
    async def handle_tag_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tag editing requests"""
        query = update.callback_query
        tag_type = query.data.replace("edit_", "")
        
        tag_names = {
            'title': 'نام آهنگ',
            'artist': 'هنرمند',
            'album': 'آلبوم',
            'genre': 'ژانر',
            'year': 'سال',
            'track': 'شماره ترک'
        }
        
        context.user_data['editing_tag'] = tag_type
        await query.edit_message_text(
            f"مقدار جدید برای {tag_names.get(tag_type, tag_type)} را وارد کنید:"
        )
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input for tag editing"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions:
            return
        
        if 'editing_tag' in context.user_data:
            tag_type = context.user_data['editing_tag']
            new_value = update.message.text
            
            # Update metadata
            session = self.user_sessions[user_id]
            session['metadata'][tag_type] = new_value
            
            # Update file
            success = self.audio_processor.update_metadata(
                session['file_path'],
                {tag_type: new_value}
            )
            
            if success:
                await update.message.reply_text(f"✅ {tag_type} با موفقیت به‌روزرسانی شد!")
            else:
                await update.message.reply_text("❌ خطا در به‌روزرسانی تگ")
            
            del context.user_data['editing_tag']
            await self.show_main_menu(update, context)
    
    async def handle_cover_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle cover art actions"""
        query = update.callback_query
        action = query.data.replace("cover_", "")
        user_id = update.effective_user.id
        session = self.user_sessions[user_id]
        
        if action == "view":
            cover_data = self.audio_processor.extract_cover_art(session['file_path'])
            if cover_data:
                await query.message.reply_photo(
                    photo=cover_data,
                    caption="کاور فعلی آلبوم"
                )
            else:
                await query.edit_message_text("❌ کاور یافت نشد")
        
        elif action == "remove":
            success = self.audio_processor.remove_cover_art(session['file_path'])
            if success:
                # Refresh metadata after removing cover
                session['metadata'] = self.audio_processor.get_metadata(session['file_path'])
                await query.edit_message_text("✅ کاور حذف شد")
            else:
                await query.edit_message_text("❌ خطا در حذف کاور")
        
        elif action == "add":
            context.user_data['adding_cover'] = True
            await query.edit_message_text("🖼️ تصویر کاور جدید را ارسال کنید:")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo uploads for cover art"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions:
            return
        
        if context.user_data.get('adding_cover'):
            try:
                # Get largest photo size
                photo = update.message.photo[-1]
                file = await context.bot.get_file(photo.file_id)
                
                # Download photo
                photo_data = await file.download_as_bytearray()
                
                # Add cover to audio file
                session = self.user_sessions[user_id]
                success = self.audio_processor.add_cover_art(
                    session['file_path'],
                    bytes(photo_data),
                    'image/jpeg'
                )
                
                if success:
                    # Refresh metadata after adding cover to ensure has_cover is updated
                    session['metadata'] = self.audio_processor.get_metadata(session['file_path'])
                    await update.message.reply_text("✅ کاور با موفقیت اضافه شد!")
                else:
                    await update.message.reply_text("❌ خطا در اضافه کردن کاور")
                
                del context.user_data['adding_cover']
                await self.show_main_menu(update, context)
                
            except Exception as e:
                await update.message.reply_text(f"❌ خطا در پردازش تصویر: {str(e)}")
                print(f"Cover art error: {e}")  # Log for debugging
    
    async def handle_format_conversion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle format conversion"""
        query = update.callback_query
        target_format = query.data.replace("format_", "")
        user_id = update.effective_user.id
        session = self.user_sessions[user_id]
        
        # Answer the callback query first to prevent timeout
        await query.answer()
        
        status_msg = await query.edit_message_text("⏳ در حال تبدیل فرمت...")
        
        try:
            # Create output path
            base_name = os.path.splitext(session['original_filename'])[0]
            output_path = os.path.join(Config.OUTPUT_DIR, f"{base_name}.{target_format}")
            
            # Convert format
            success = self.audio_processor.convert_format(
                session['file_path'],
                output_path,
                target_format
            )
            
            if success and os.path.exists(output_path):
                # Update session
                session['file_path'] = output_path
                session['metadata']['format'] = f".{target_format}"
                
                await status_msg.edit_text(f"✅ فایل به فرمت {target_format.upper()} تبدیل شد!")
                
                # Send the converted file to user
                with open(output_path, 'rb') as audio_file:
                    # Extract cover art for thumbnail if available
                    cover_data = None
                    if session['metadata'].get('has_cover', False):
                        cover_data = self.audio_processor.extract_cover_art(output_path)
                    
                    if cover_data:
                        await context.bot.send_audio(
                            chat_id=user_id,
                            audio=audio_file,
                            thumbnail=cover_data,
                            filename=f"{base_name}.{target_format}",
                            caption=f"🎵 فایل تبدیل شده به فرمت {target_format.upper()}"
                        )
                    else:
                        await context.bot.send_audio(
                            chat_id=user_id,
                            audio=audio_file,
                            filename=f"{base_name}.{target_format}",
                            caption=f"🎵 فایل تبدیل شده به فرمت {target_format.upper()}"
                        )
                
                # Show main menu again
                await self.show_main_menu(update, context)
            else:
                await status_msg.edit_text("❌ خطا در تبدیل فرمت")
                
        except Exception as e:
            await status_msg.edit_text(f"❌ خطا در تبدیل: {str(e)}")
            print(f"Format conversion error: {e}")  # Log for debugging
    
    async def save_and_download(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save and send the edited file"""
        user_id = update.effective_user.id
        session = self.user_sessions[user_id]
        
        status_msg = await update.callback_query.edit_message_text("⏳ در حال آماده‌سازی فایل...")
        
        try:
            # Generate filename
            filename_template = context.user_data.get('filename_template', '{artist} - {title}')
            base_filename = self.audio_processor.generate_filename(
                session['metadata'],
                filename_template
            )
            
            # Add extension
            extension = session['metadata'].get('format', '.mp3')
            if not extension.startswith('.'):
                extension = f".{extension}"
            
            final_filename = f"{base_filename}{extension}"
            
            # Extract cover art for thumbnail if available
            cover_data = None
            if session['metadata'].get('has_cover', False):
                cover_data = self.audio_processor.extract_cover_art(session['file_path'])
            
            # Send file with cover as thumbnail if available
            with open(session['file_path'], 'rb') as audio_file:
                if cover_data:
                    await context.bot.send_audio(
                        chat_id=update.effective_chat.id,
                        audio=audio_file,
                        thumbnail=cover_data,
                        filename=final_filename,
                        caption="✅ فایل ویرایش شده آماده است!"
                    )
                else:
                    await context.bot.send_audio(
                        chat_id=update.effective_chat.id,
                        audio=audio_file,
                        filename=final_filename,
                        caption="✅ فایل ویرایش شده آماده است!"
                    )
            
            await status_msg.edit_text("✅ فایل با موفقیت ارسال شد!")
            
        except Exception as e:
            await status_msg.edit_text(f"❌ خطا در ارسال فایل: {str(e)}")
            print(f"Save and download error: {e}")  # Log for debugging
    
    async def delete_user_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Delete user's file and session"""
        user_id = update.effective_user.id
        
        if user_id in self.user_sessions:
            session = self.user_sessions[user_id]
            
            # Delete file
            try:
                if os.path.exists(session['file_path']):
                    os.remove(session['file_path'])
            except:
                pass
            
            # Delete session
            del self.user_sessions[user_id]
            
            await update.callback_query.edit_message_text("🗑️ فایل حذف شد. فایل جدید ارسال کنید.")
    
    async def batch_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /batch command for batch processing"""
        user_id = update.effective_user.id
        
        # Check if user has admin privileges for large batches
        is_admin = user_id == Config.ADMIN_USER_ID
        max_batch = 20 if is_admin else 10
        
        text = f"""
📦 **پردازش دسته‌ای فایل‌ها**

حداکثر تعداد فایل: {max_batch}

مراحل:
1️⃣ فایل‌های صوتی خود را یکی یکی ارسال کنید
2️⃣ پس از ارسال همه فایل‌ها، /batch_process را بزنید
3️⃣ عملیات مورد نظر را انتخاب کنید
4️⃣ تنظیمات را اعمال کنید

دستورات:
/batch_process - شروع پردازش
/batch_clear - پاک کردن لیست
/batch_list - نمایش فایل‌های اضافه شده

برای لغو: /start
        """
        
        # Initialize batch session
        self.batch_sessions[user_id] = {
            'files': [],
            'operations': [],
            'settings': {}
        }
        
        await update.message.reply_text(text)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user_id = update.effective_user.id
        user_stats = self.admin_panel.get_user_stats(user_id)
        
        if not user_stats:
            await update.message.reply_text("📊 آماری برای شما یافت نشد.")
            return
        
        # Format file size
        def format_size(bytes_size):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_size < 1024:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024
            return f"{bytes_size:.1f} TB"
        
        # Check daily limits
        limits_check = self.admin_panel.check_user_limits(user_id, 0)
        daily_remaining = limits_check['limits']['daily_remaining']
        
        stats_text = f"""
📊 **آمار شخصی شما**

👤 **کاربر:** {user_stats.first_name or 'نامشخص'}
📅 **عضویت:** {user_stats.join_date.strftime('%Y/%m/%d')}
🎵 **فایل‌های پردازش شده:** {user_stats.files_processed}
💾 **حجم کل پردازش شده:** {format_size(user_stats.total_file_size)}
📈 **آخرین فعالیت:** {user_stats.last_activity.strftime('%Y/%m/%d %H:%M')}

📋 **محدودیت‌های روزانه:**
• باقی‌مانده امروز: {daily_remaining} فایل
• حداکثر حجم فایل: {format_size(limits_check['limits']['max_file_size'])}

🏆 **وضعیت:** {'🔴 مسدود' if user_stats.is_banned else '🟢 فعال'}
        """
        
        await update.message.reply_text(stats_text)
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        user_id = update.effective_user.id
        
        if user_id != Config.ADMIN_USER_ID:
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
            return
        
        system_stats = self.admin_panel.get_system_stats()
        
        def format_size(bytes_size):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_size < 1024:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024
            return f"{bytes_size:.1f} TB"
        
        admin_text = f"""
🔧 **پنل مدیریت**

📊 **آمار سیستم:**
👥 کل کاربران: {system_stats.total_users}
🎵 کل فایل‌های پردازش شده: {system_stats.total_files_processed}
💾 کل حجم پردازش شده: {format_size(system_stats.total_data_processed)}
📈 کاربران فعال امروز: {system_stats.active_users_today}
📅 کاربران فعال این هفته: {system_stats.active_users_week}
📊 میانگین حجم فایل: {format_size(system_stats.average_file_size)}
🎼 محبوب‌ترین فرمت: {system_stats.most_popular_format}

دستورات ادمین:
/admin_users - لیست کاربران برتر
/admin_activity - فعالیت‌های اخیر
/admin_limits - تنظیم محدودیت‌ها
/admin_export - خروجی آمار
        """
        
        keyboard = [
            [InlineKeyboardButton("👥 کاربران برتر", callback_data="admin_top_users")],
            [InlineKeyboardButton("📊 فعالیت‌های اخیر", callback_data="admin_recent_activity")],
            [InlineKeyboardButton("⚙️ تنظیم محدودیت‌ها", callback_data="admin_limits")],
            [InlineKeyboardButton("📤 خروجی آمار", callback_data="admin_export")]
        ]
        
        await update.message.reply_text(
            admin_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📖 **راهنمای ربات ویرایش موزیک**

🎵 **امکانات اصلی:**
• ویرایش تگ‌های ID3 (نام، هنرمند، آلبوم، ژانر، سال)
• مدیریت کاور آلبوم (اضافه، حذف، جایگزینی)
• تبدیل فرمت صوتی
• تغییر کیفیت و بیت‌ریت
• نام‌گذاری سفارشی فایل‌ها
• پردازش دسته‌ای چندین فایل

📋 **دستورات:**
/start - شروع و منوی اصلی
/batch - پردازش دسته‌ای فایل‌ها
/stats - نمایش آمار شخصی
/help - نمایش این راهنما

🎼 **فرمت‌های پشتیبانی شده:**
MP3, FLAC, WAV, M4A, OGG, AAC

📏 **محدودیت‌ها:**
• حداکثر حجم فایل: 50 مگابایت
• حداکثر فایل روزانه: 20 فایل
• حداکثر پردازش دسته‌ای: 10 فایل

💡 **نکات:**
• برای بهترین کیفیت، از فرمت FLAC استفاده کنید
• کاور آلبوم باید کمتر از 5 مگابایت باشد
• در پردازش دسته‌ای، همه فایل‌ها باید فرمت یکسان داشته باشند

❓ **پشتیبانی:**
در صورت بروز مشکل، با ادمین تماس بگیرید.
        """
        
        await update.message.reply_text(help_text)
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors that occur during bot operation"""
        import traceback
        
        # Log the error
        print(f"❌ خطای ربات: {context.error}")
        print(f"Update: {update}")
        traceback.print_exception(type(context.error), context.error, context.error.__traceback__)
        
        # Try to send error message to user if possible
        try:
            if update and hasattr(update, 'effective_chat') and update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ خطایی در ربات رخ داده است. لطفاً دوباره تلاش کنید."
                )
        except Exception as e:
            print(f"Could not send error message to user: {e}")
    
    def run(self):
        """Run the bot"""
        if not Config.BOT_TOKEN:
            print("❌ BOT_TOKEN تنظیم نشده است!")
            return
        
        # Create application
        application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Add error handler
        application.add_error_handler(self.error_handler)
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("batch", self.batch_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("admin", self.admin_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(MessageHandler(filters.AUDIO | filters.Document.AUDIO, self.handle_audio))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_input))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        print("🎵 ربات موزیک راه‌اندازی شد!")
        application.run_polling()

if __name__ == "__main__":
    bot = MusicBot()
    bot.run()