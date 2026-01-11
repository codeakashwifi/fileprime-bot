import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters

BOT_TOKEN = "8409603507:AAESQBHejMHTqvXhctGAXUktYh2Wg-t5Jl8"
API_KEY = "c3ca14abfbd0a06e53691ba9af2ba97e4265c7a1"

def monetize(url):
    api = f"https://shrinkme.io/api?api={API_KEY}&url={url}"
    r = requests.get(api).json()
    return r.get("shortenedUrl", url)

async def handle(update: Update, context):
    msg = update.message.text.strip()

    if "archive.org/details/" not in msg:
        await update.message.reply_text("Send a valid Archive.org link")
        return

    item = msg.split("archive.org/details/")[1].split("/")[0]
    meta = requests.get(f"https://archive.org/metadata/{item}").json()

    if "files" not in meta:
        await update.message.reply_text("Invalid Archive.org item.")
        return

    reply = ""
    for f in meta["files"]:
        name = f.get("name", "")
        if name.endswith(("mp4", "mkv", "mp3", "pdf")):
            real = f"https://archive.org/download/{item}/{name}"
            money = monetize(real)
            reply += f"{name} → {money}\n"

    if reply == "":
        reply = "No downloadable files found."

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle))
app.run_polling()
