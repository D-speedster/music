import os
import io
import asyncio
import logging
from typing import Optional

from telethon import TelegramClient, events, Button
from telethon.tl import types

from config import Config
from utils.audio_processor import AudioProcessor
from utils.uploader import upload_file_async


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


audio_processor = AudioProcessor()


def _mb(size_bytes: int) -> float:
    return round(size_bytes / (1024 * 1024), 2)


async def _send_large_file_in_parts(client: TelegramClient, chat_id: int, file_path: str) -> None:
    part_size = Config.LARGE_FILE_PART_SIZE_BYTES
    file_size = os.path.getsize(file_path)
    total_parts = (file_size + part_size - 1) // part_size
    base_name = os.path.basename(file_path)

    await client.send_message(
        chat_id,
        f'فایل بزرگ‌تر از حد تلگرام است. ارسال در {total_parts} پارت شروع شد. '\
        f'اندازهٔ هر پارت ≈ {_mb(part_size)}MB'
    )

    with open(file_path, 'rb') as src:
        idx = 1
        while True:
            chunk = src.read(part_size)
            if not chunk:
                break
            part_name = f'{base_name}.part{idx:03d}'
            part_path = os.path.join(Config.TEMP_DIR, part_name)
            with open(part_path, 'wb') as p:
                p.write(chunk)

            caption = f'{part_name} / {idx}/{total_parts} — {_mb(len(chunk))}MB'
            try:
                await client.send_file(chat_id, part_path, caption=caption)
            finally:
                try:
                    os.remove(part_path)
                except Exception:
                    pass
            idx += 1

    await client.send_message(
        chat_id,
        'برای ادغام پارت‌ها:\n'
        'Windows: `copy /b base.part001+base.part002+... full_file`\n'
        'Linux/macOS: `cat base.part* > full_file`'
    )


async def _deliver_file_auto(client: TelegramClient, chat_id: int, file_path: str) -> None:
    try:
        size = os.path.getsize(file_path)

        if size <= Config.TELEGRAM_UPLOAD_LIMIT_BYTES:
            # Try to generate a small thumb to improve UX
            thumb_bytes: Optional[bytes] = None
            try:
                thumb_io = audio_processor.generate_waveform_cover(file_path)
                if thumb_io:
                    thumb_bytes = thumb_io.getvalue() if hasattr(thumb_io, 'getvalue') else None
            except Exception as e:
                logger.warning(f'Thumb generation failed: {e}')

            attrs = [
                types.DocumentAttributeAudio(
                    duration=0,
                    title=os.path.basename(file_path),
                    performer=''
                )
            ]

            await client.send_file(
                chat_id,
                file_path,
                attributes=attrs,
                thumb=thumb_bytes,
                supports_streaming=True,
                caption=f'ارسال مستقیم ✅ — اندازه: {_mb(size)}MB'
            )
            return

        # Try external upload if enabled
        if Config.ENABLE_EXTERNAL_UPLOAD:
            try:
                url = await upload_file_async(file_path, provider=Config.EXTERNAL_UPLOAD_PROVIDER)
                if url:
                    await client.send_message(
                        chat_id,
                        f'فایل بزرگ بود و به‌صورت خارجی آپلود شد:\n{url}'
                    )

                    # Send 30s audio preview
                    try:
                        preview_io = audio_processor.generate_preview(file_path)
                        if preview_io:
                            await client.send_file(
                                chat_id,
                                preview_io,
                                file_name='preview_30s.mp3',
                                caption='پیش‌نمایش ۳۰ ثانیه‌ای 🎧'
                            )
                    except Exception as e:
                        logger.warning(f'Preview generation failed: {e}')
                    return
            except Exception as e:
                logger.warning(f'External upload failed: {e}')

        # Fallback: send in parts
        await _send_large_file_in_parts(client, chat_id, file_path)

    except Exception as e:
        logger.error(f'Deliver failed: {e}', exc_info=True)
        # Offer retry button
        await client.send_message(
            chat_id,
            'ارسال با خطا مواجه شد. می‌خواهید دوباره تلاش کنم؟',
            buttons=[Button.inline('🔁 Retry Send', data=f'retry|{file_path}'.encode())]
        )


def _require_telethon_credentials() -> None:
    if not Config.BOT_TOKEN:
        raise RuntimeError('BOT_TOKEN در محیط تنظیم نشده است')
    if not Config.TELEGRAM_API_ID or not Config.TELEGRAM_API_HASH:
        raise RuntimeError('برای Telethon باید TELEGRAM_API_ID و TELEGRAM_API_HASH را در .env تنظیم کنید')


async def main() -> None:
    _require_telethon_credentials()

    client = TelegramClient('bot_session', Config.TELEGRAM_API_ID, Config.TELEGRAM_API_HASH)
    await client.start(bot_token=Config.BOT_TOKEN)
    logger.info('🎵 بات Telethon راه‌اندازی شد! آمادهٔ دریافت فایل‌های بزرگ هستم.')

    @client.on(events.NewMessage(pattern='/start'))
    async def handler_start(event: events.NewMessage.Event) -> None:
        await event.respond(
            'سلام! فایل صوتی یا مستند را بفرستید تا آن را ارسال کنم.\n'
            '• تا ~49MB مستقیم ارسال می‌کنم.\n'
            '• بزرگ‌ترها را آپلود خارجی + پیش‌نمایش، یا به پارت تقسیم می‌کنم.',
            buttons=[[Button.text('راهنما'), Button.text('Retry Send')]]
        )

    @client.on(events.NewMessage(func=lambda e: e.message and e.message.media))
    async def handler_media(event: events.NewMessage.Event) -> None:
        chat_id = event.chat_id
        try:
            file_path = await client.download_media(event.message, file=Config.TEMP_DIR)
            if not file_path:
                await event.reply('دانلود رسانه ناموفق بود. دوباره تلاش کنید.')
                return
            await _deliver_file_auto(client, chat_id, file_path)
        except Exception as e:
            logger.error(f'Media handler error: {e}', exc_info=True)
            await event.reply('خطا در پردازش رسانه رخ داد.')

    @client.on(events.CallbackQuery)
    async def handler_retry(event: events.CallbackQuery.Event) -> None:
        data = event.data or b''
        if data.startswith(b'retry|'):
            file_path = data.decode(errors='ignore').split('|', 1)[1]
            await event.answer('در حال تلاش مجدد...')
            await _deliver_file_auto(client, event.chat_id, file_path)

    # Keep running
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f'Bot crashed: {e}')
        raise