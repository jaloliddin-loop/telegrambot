from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "7982248929:AAH7Srov2kuUTzyvaiVqOn-YuW6tn-l-kvs"  # ← bu yerga o'z tokeningizni qo'ying

# 🎬 20 ta kino kodi va silkasi
movies = {
    "1": ("Qasoskorlar", "https://t.me/+6b4QGPPCgw9mZTli"),
    "2": ("Nafas olmay tur", "https://t.me/+ncQlj_cHEzpkM2Vi"),
    "3": ("Janob Uyqu", "https://t.me/+CakcUA2nSTY4MWRi"),
    "4": ("172 kun", "https://t.me/+LVJIJ44UuTAxNDBi"),
    "5": ("Qasoskorlar: Intiho", "https://t.me/avengers_link"),
    "6": ("Havaskor ", "https://t.me/+1Z8WtZ-nHHBhZWJi"),
    "7": ("Tasavvur qil", "https://t.me/+u5ADJz-RbtZkNGUy"),
    "8": ("Tuzoq kinosi", "https://t.me/+5SXKGl228D5hMWVi"),
    "9": ("Uni olimdan qaytar", "https://t.me/+4xZeQz1ANs9mODAy"),
    "10": ("Qorqinchli Tun", "https://t.me/horror_link"),
    "11": ("Ko‘cha hayoti", "https://t.me/streetlife_link"),
    "12": ("Sherlok Xolms", "https://t.me/sherlock_link"),
    "13": ("Kung Fu Panda 4", "https://t.me/kungfu4_link"),
    "14": ("Deadpool 3", "https://t.me/deadpool3_link"),
    "15": ("Yuraklar jangi", "https://t.me/heartbattle_link"),
    "16": ("Harry Potter", "https://t.me/harrypotter_link"),
    "17": ("Yashil yo‘l", "https://t.me/greenmile_link"),
    "18": ("King Kong", "https://t.me/kingkong_link"),
    "19": ("Haqiqiy qahramon", "https://t.me/realhero_link"),
    "20": ("No‘xat donasi", "https://t.me/nuxatdonasi_link"),
}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Xush kelibsiz!\nKino kodini yuboring yoki /royhat buyrug'ini bering.")

# /royhat komandasi
async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🎬 Mavjud kinolar:\n"
    for code, (name, _) in movies.items():
        text += f"• {code} – {name}\n"
    await update.message.reply_text(text)

# Kino kodi yozilganda
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    if code in movies:
        name, link = movies[code]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 Kinoni ko‘rish", url=link)]
        ])
        await update.message.reply_text(f"✅ {name} topildi:", reply_markup=keyboard)
    else:
        await update.message.reply_text("❌ Bunday kod topilmadi.")

# Botni ishga tushirish
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("royhat", show_list))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
app.run_polling()
