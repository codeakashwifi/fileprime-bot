import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters

BOT_TOKEN = "8409603507:AAGqFx6avuhpVvrr9YHRzye_P-lgkCnU55E"
API_KEY = "c3ca14abfbd0a06e53691ba9af2ba97e4265c7a1"

def monetize(url):
    api = f"https://shrinkme.io/api?api={API_KEY}&url={url}"
    r = requests.get(api).json()
    return r.get("shortenedUrl", url)

def search_archive(query):
    url = f"https://archive.org/advancedsearch.php?q={query}&fl[]=identifier&fl[]=title&rows=5&page=1&output=json"
    return requests.get(url).json()["response"]["docs"]

async def handle(update: Update, context):
    msg = update.message.text.strip()

    # If link is sent
    if "archive.org/details/" in msg:
        item = msg.split("archive.org/details/")[1].split("/")[0]
        meta = requests.get(f"https://archive.org/metadata/{item}").json()

        if "files" not in meta:
            await update.message.reply_text("Invalid Archive.org item.")
            return

        reply = ""
        for f in meta["files"]:
            name = f.get("name","")
            if name.endswith(("mp4","mkv","mp3","pdf")):
                real = f"https://archive.org/download/{item}/{name}"
                reply += f"{name} → {monetize(real)}\n"

        await update.message.reply_text(reply if reply else "No files found.")
        return

    # Otherwise treat message as search
    results = search_archive(msg)

    if not results:
        await update.message.reply_text("No results found.")
        return

    reply = "🎬 Search Results:\n\n"
    for r in results:
        title = r.get("title","No title")
        ident = r.get("identifier")
        reply += f"{title}\nhttps://archive.org/details/{ident}\n\n"

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle))
app.run_polling()
