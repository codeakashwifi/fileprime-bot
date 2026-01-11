import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters

BOT_TOKEN = "PASTE_YOUR_NEW_TELEGRAM_TOKEN"
API_KEY = "PASTE_YOUR_SHRINKME_KEY"

def monetize(url):
    api = f"https://shrinkme.io/api?api={c3ca14abfbd0a06e53691ba9af2ba97e4265c7a1}&url={url}"
    return requests.get(api).json()["shortenedUrl"]

async def handle(update: Update, context):
    msg = update.message.text

    if "archive.org/details/" not in msg:
        await update.message.reply_text("Send Archive.org link only")
        return

    item = msg.split("archive.org/details/")[1].split("/")[0]
    data = requests.get(f"https://archive.org/metadata/{item}").json()

    reply = ""
    for f in data["files"]:
        if f["name"].endswith(("mp4","pdf","mkv","mp3")):
            real = f"https://archive.org/download/{item}/{f['name']}"
            money = monetize(real)
            reply += f"{f['name']} → {money}\n"

    await update.message.reply_text(reply)

app = ApplicationBuilder().token("8409603507:AAESQBHejMHTqvXhctGAXUktYh2Wg-t5Jl8").build()
app.add_handler(MessageHandler(filters.TEXT, handle))
app.run_polling()
