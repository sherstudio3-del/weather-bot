import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ====== FAQAT SHU 2 TASINI O'ZGARTIRASIZ ======
TOKEN = "8665348129:AAG_fP0yB_Cf7wnMma5asEiDsgRJDozngl8"
API_KEY = "73ec21bc9dbea02959c92a6b228dbd1d"

users = set()

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    admin_id = 8006832970

    if update.message.chat_id != admin_id:
        return

    count = len(users)

    await update.message.reply_text(f"Botdan foydalanayotganlar soni: {count} ta")
# ==============================================

keyboard = [[KeyboardButton("📍 Lokatsiya yuborish", request_location=True)]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    users.add(update.message.chat_id)

    await update.message.reply_text(
        "Salom 👋\nOb-havo bilish uchun lokatsiyangizni yuboring 📍",
        reply_markup=markup)


def get_weather(lat, lon):

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=uz"
    data = requests.get(url).json()

    today_day = []
    today_night = []
    rain = False
    cloud = False

    for item in data["list"]:

        hour = int(item["dt_txt"][11:13])
        temp = item["main"]["temp"]
        weather = item["weather"][0]["main"]

        if weather == "Rain":
            rain = True

        if weather == "Clouds":
            cloud = True

        if 9 <= hour <= 18:
            today_day.append(temp)
        else:
            today_night.append(temp)

    day_avg = round(sum(today_day) / len(today_day), 1)
    night_avg = round(sum(today_night) / len(today_night), 1)
    overall = round((day_avg + night_avg) / 2, 1)

    msg = f"""
🌤 BUGUNGI OB-HAVO

🌡 O‘rtacha: {overall}°C
☀️ Kunduz: {day_avg}°C
🌙 Kechasi: {night_avg}°C
"""

    if rain:
        msg += "🌧 Bugun yomg‘ir bo‘lishi mumkin\n"
    elif cloud:
        msg += "☁️ Bugun bulutli bo‘lishi mumkin\n"
    else:
        msg += "☀️ Bugun ochiq ob-havo\n"

    msg += "\n📅 Keyingi kunlar:\n"

    days = {}

    for item in data["list"]:

        date = item["dt_txt"][:10]
        hour = int(item["dt_txt"][11:13])
        temp = item["main"]["temp"]

        if 11 <= hour <= 15:

            if date not in days:
                days[date] = []

            days[date].append(temp)

    for d in list(days.keys())[1:6]:

        avg = round(sum(days[d]) / len(days[d]), 1)

        msg += f"{d} — ☀️ {avg}°C\n"

    return msg


# 📍 Lokatsiya kelganda ishlaydi
async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):

    lat = update.message.location.latitude
    lon = update.message.location.longitude

    weather = get_weather(lat, lon)

    await update.message.reply_text(weather)


# 📢 Hammaga xabar yuborish
async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):

    admin_id = 8006832970  # ⚠️ BU YERGA O'Z TELEGRAM ID INGIZNI YOZASIZ

    if update.message.chat_id != admin_id:
        return

    text = " ".join(context.args)

    for user in users:
        try:
            await context.bot.send_message(chat_id=user, text=text)
        except:
            pass


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.LOCATION, location))
app.add_handler(CommandHandler("send", send))
app.add_handler(CommandHandler("stats", stats))

print("Bot ishga tushdi...")

app.run_polling()
