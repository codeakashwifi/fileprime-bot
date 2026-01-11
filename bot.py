import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters

BOT_TOKEN = "8409603507:AAHhhazMyXgSZFYrRspeXDUJ9AVwdJDbKe4"
RAPIDAPI_KEY = "7566dd4eeamsh59a4b8ee5ea97e2p112454jsn1b19a2f22ec0"
SHORTLINK_KEY = "c3ca14abfbd0a06e53691ba9af2ba97e4265c7a1"

HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "youtube-downloader-api.p.rapidapi.com"
}

def monetize(url):
    api = f"https://shrinkme.io/api?api={SHORTLINK_KEY}&url={url}"
    r = requests.get(api).json()
    return r.get("shortenedUrl", url)

def get_video(url):
    api_url = "https://youtube-downloader-api.p.rapidapi.com/yt"
    r = requests.get(api_url, headers=HEADERS, params={"url": url}).json()
    return r

def search(query):
    api_url = "https://youtube-downloader-api.p.rapidapi.com/search"
    r = requests.get(api_url, headers=HEADERS, params={"query": query}).json()
    return r.get("videos", [])

async def handle(update: Update, context):
    text = update.message.text.strip()

    # YouTube link
    if "youtube.com" in text or "youtu.be" in text:
        data = get_video(text)
        context.user_data["video"] = data

        title = data.get("title", "Video")
        thumb = data.get("thumbnail")

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎞 720p", callback_data="720"),
                InlineKeyboardButton("🎞 1080p", callback_data="1080")
            ],
            [
                InlineKeyboardButton("🎵 MP3", callback_data="mp3")
            ]
        ])

        if thumb:
            await update.message.reply_photo(photo=thumb, caption=title, reply_markup=buttons)
        else:
            await update.message.reply_text(title, reply_markup=buttons)
        return

    # Search
    results = search(text)
    if not results:
        await update.message.reply_text("No results found.")
        return

    reply = "🔍 Search Results:\n\n"
    for v in results[:5]:
        reply += f"{v['title']}\nhttps://youtu.be/{v['videoId']}\n\n"

    await update.message.reply_text(reply)

async def buttons(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = context.user_data["video"]

    quality = query.data

    try:
        if quality == "720":
            link = data["formats"]["mp4"]["720p"]
        elif quality == "1080":
            link = data["formats"]["mp4"]["1080p"]
        elif quality == "mp3":
            link = data["formats"]["mp3"]

        await query.edit_message_caption(caption=f"Your download link:\n{monetize(link)}")

    except:
        await query.edit_message_caption(caption="Download not available for this quality.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle))
app.add_handler(CallbackQueryHandler(buttons))
app.run_polling()
