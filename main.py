from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

TOKEN = '7551358810:AAGa61l5J_k-MPzffFmxh6EvsIhLrR8WCjM'  # 👉 Bu yerga o‘z tokeningni yoz

# Viloyatlar (har biri ekranda gorizontal bo‘lib chiqadi)
regions = ["Toshkent", "Andijon", "Namangan", "Farg‘ona", "Buxoro", "Jizzax", "Xorazm", "Surxondaryo", "Qashqadaryo", "Samarqand", "Sirdaryo", "Navoiy", "Qoraqalpog‘iston"]

# Banklar (gorizontal chiqadi)
banks = ["Hamkorbank", "Agrobank", "Ipoteka Bank", "NBU", "Xalq Bank"]

# ✅ cbu.uz API orqali real USD kursini olish
def get_usd_from_cbu():
    try:
        url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
        res = requests.get(url)
        data = res.json()
        for item in data:
            if item['Ccy'] == "USD":
                return {
                    'buy': item['Rate'],
                    'sell': str(round(float(item['Rate']) + 100, 2))
                }
        return {'error': 'USD topilmadi'}
    except Exception as e:
        return {'error': str(e)}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 📌 Viloyatlarni gorizontal formatda chiqarish (2 tadan)
    buttons = []
    row = []
    for i, region in enumerate(regions, start=1):
        row.append(InlineKeyboardButton(region, callback_data=region))
        if i % 2 == 0:
            buttons.append(row)
            row = []
    if row:  # oxirgi qator qolsa
        buttons.append(row)

    await update.message.reply_text("🗺 Viloyatni tanlang:", reply_markup=InlineKeyboardMarkup(buttons))

# Viloyat tanlanganda
async def handle_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    region = query.data
    context.user_data['region'] = region

    # Banklar tugmalari ham gorizontal (2 tadan)
    buttons = []
    row = []
    for i, bank in enumerate(banks, start=1):
        row.append(InlineKeyboardButton(bank, callback_data=f"bank|{bank}"))
        if i % 2 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    await query.edit_message_text(
        text=f"✅ {region} viloyati tanlandi.\n🏦 Endi bankni tanlang:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Bank tanlanganda
async def handle_bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, bank = query.data.split("|")
    region = context.user_data.get("region", "Viloyat tanlanmagan")
    kurs = get_usd_from_cbu()

    if 'error' in kurs:
        await query.edit_message_text(f"❌ Xatolik: {kurs['error']}")
        return

    await query.edit_message_text(
        f"📍 *{region}* - *{bank}*\n"
        f"💵 *Sotib olish*: {kurs['buy']} so‘m\n"
        f"💸 *Sotish*: {kurs['sell']} so‘m\n"
        f"🌐 *Manba*: [cbu.uz](https://cbu.uz)",
        parse_mode="Markdown"
    )

# Botni ishga tushirish
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_bank, pattern="^bank\|"))
app.add_handler(CallbackQueryHandler(handle_region))

if __name__ == '__main__':
    print("✅ Bot ishga tushdi!")
    app.run_polling()
