import os
import random
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
)

TOKEN = "8100312871:AAH12BXA8pgZWzdTiuxtMOL52a6YzZ_bQ40"
USER_DATA = {}
FFMPEG_PATH = r"C:\insall\ffmpeg-7.1.1-essentials_build\bin"

# 🎬 Media yuklash funksiyasi
async def download_media(url, mode, user_id):
    ext = 'mp3' if mode == 'audio' else 'mp4'
    filename = f"{mode}_{user_id}_{random.randint(1000,9999)}.{ext}"

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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename

# ▶ /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 YouTube yoki Instagram link yuboring.\n⬇ Video yoki musiqa yuklash uchun tugmani tanlang.")

# 🌐 Link yuborilganda
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    user_id = update.message.from_user.id

    if any(domain in url for domain in ["youtube.com", "youtu.be", "instagram.com"]):
        USER_DATA[user_id] = url
        buttons = [
            [InlineKeyboardButton("🎞 360p", callback_data="video_360"),
             InlineKeyboardButton("🎥 720p", callback_data="video_720"),
             InlineKeyboardButton("🎬 1080p", callback_data="video_1080")],
            [InlineKeyboardButton("🎵 Musiqa olish", callback_data="video_audio")]
        ]
        markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("⬇ Formatni tanlang:", reply_markup=markup)
    else:
        await update.message.reply_text("❌ Iltimos, YouTube yoki Instagram link yuboring.")

# ⏬ Tugma bosilganda
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    action = data.split("_")[1]
    url = USER_DATA.get(user_id)

    if not url:
        await query.message.reply_text("⚠ Link topilmadi. Qaytadan yuboring.")
        return

    if action == "audio":
        await query.edit_message_text("🎧 Musiqa yuklanmoqda...")
    else:
        await query.edit_message_text(f"📥 {action}p video yuklanmoqda...")

    try:
        filename = await download_media(url, action, user_id)

        if action == "audio":
            with open(filename, "rb") as f:
                await query.message.reply_audio(audio=f, title="🎵 Musiqa")
        else:
            with open(filename, "rb") as f:
                await query.message.reply_video(video=f, caption=f"🎬 {action}p video", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎵 Musiqani yuklash", callback_data="video_audio")]
                ]))

        os.remove(filename)

    except Exception as e:
        await query.message.reply_text(f"❌ Xatolik: {e}")

# 🚀 Botni ishga tushurish
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(button_callback))

print("✅ Mukammal bot ishga tushdi!")
app.run_polling()
