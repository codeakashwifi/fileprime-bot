import yt_dlp
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters

BOT_TOKEN = "8409603507:AAGqFx6avuhpVvrr9YHRzye_P-lgkCnU55E"
API_KEY = "c3ca14abfbd0a06e53691ba9af2ba97e4265c7a1"

def monetize(url):
    api = f"https://shrinkme.io/api?api={API_KEY}&url={url}"
    r = requests.get(api).json()
    return r.get("shortenedUrl", url)

def get_video_info(url):
    ydl_opts = {"quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

def search_youtube(query):
    ydl_opts = {"quiet": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(f"ytsearch5:{query}", download=False)["entries"]

async def handle(update: Update, context):
    text = update.message.text

    # Search mode
    if "youtube.com" not in text and "youtu.be" not in text:
        results = search_youtube(text)
        reply = "🔍 Search Results:\n\n"
        for r in results:
            reply += f"{r['title']}\nhttps://youtu.be/{r['id']}\n\n"
        await update.message.reply_text(reply)
        return

    # Video mode
    info = get_video_info(text)
    thumb = info.get("thumbnail")
    context.user_data["url"] = text

    buttons = [
        [InlineKeyboardButton("🎞️ 720p", callback_data="720"),
         InlineKeyboardButton("🎞️ 1080p", callback_data="1080")],
        [InlineKeyboardButton("🎵 MP3", callback_data="mp3")]
    ]

    await update.message.reply_photo(
        photo=thumb,
        caption=info["title"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    url = context.user_data["url"]
    quality = query.data

    ydl_opts = {"quiet": True}
    if quality == "mp3":
        ydl_opts["format"] = "bestaudio"
    elif quality == "720":
        ydl_opts["format"] = "bestvideo[height<=720]+bestaudio/best"
    elif quality == "1080":
        ydl_opts["format"] = "bestvideo[height<=1080]+bestaudio/best"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        link = info["url"]

    msg = f"Your download link:\n{monetize(link)}"

    # Captions
    subs = info.get("subtitles")
    if subs:
        msg += "\n\n📝 Subtitles available on YouTube."

    await query.edit_message_caption(caption=msg)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()
