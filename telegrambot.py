import os
import yt_dlp
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
)

TOKEN = "8100312871:AAH12BXA8pgZWzdTiuxtMOL52a6YzZ_bQ40"
USER_DATA = {}
FFMPEG_PATH = r"C:\insall\ffmpeg-7.1.1-essentials_build\bin"

# Har bir so‘rovni alohida bajarish uchun async yuklash
async def download_media(url, mode, uid):
    filename = f'{uid}_video.%(ext)s' if mode != 'audio' else f'{uid}_audio.%(ext)s'

    ydl_opts = {
        'format': 'bestaudio/best' if mode == 'audio' else f'bestvideo[height<={mode}]+bestaudio/best',
        'outtmpl': filename,
        'merge_output_format': 'mp4' if mode != 'audio' else None,
        'ffmpeg_location': FFMPEG_PATH,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if mode == 'audio' else []
    }

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 YouTube yoki Instagram havolasini yuboring.")

# Link yuborilganda
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    uid = update.message.from_user.id

    if any(domain in url for domain in ["youtube.com", "youtu.be", "instagram.com"]):
        USER_DATA[uid] = url
        buttons = [
            [InlineKeyboardButton("🎞 360p", callback_data="video_360"),
             InlineKeyboardButton("🎥 720p", callback_data="video_720"),
             InlineKeyboardButton("🎬 1080p", callback_data="video_1080")],
            [InlineKeyboardButton("🎵 Musiqa", callback_data="video_audio")]
        ]
        markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("⬇ Formatni tanlang:", reply_markup=markup)
    else:
        await update.message.reply_text("❗ Faqat YouTube yoki Instagram havolasi yuboring.")

# Tugma bosilganda
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = query.data
    action = data.split("_")[1]
    url = USER_DATA.get(uid)

    if not url:
        await query.message.reply_text("⚠ Link topilmadi.")
        return

    await query.edit_message_text("⏳ Yuklanmoqda...")

    try:
        await download_media(url, action, uid)

        if action == "audio":
            path = f"{uid}_audio.mp3"
            with open(path, "rb") as f:
                await query.message.reply_audio(audio=f, title="🎵 Musiqa")
            os.remove(path)
        else:
            path = f"{uid}_video.mp4"
            with open(path, "rb") as f:
                await query.message.reply_video(video=f, caption=f"{action}p video", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎵 Musiqa", callback_data="video_audio")]
                ]))
            os.remove(path)

    except Exception as e:
        await query.message.reply_text(f"❌ Xatolik: {str(e)}")

# Botni ishga tushirish
app = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(button_callback))

print("✅ Ko‘p foydalanuvchi uchun tayyor bot ishga tushdi!")
app.run_polling()
