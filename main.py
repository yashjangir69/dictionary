import os
import json
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Load environment
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_GROUP_ID = int(os.getenv("ALLOWED_GROUP_ID"))
ALLOWED_TOPIC_ID = os.getenv("ALLOWED_TOPIC_ID")
if ALLOWED_TOPIC_ID is not None:
    ALLOWED_TOPIC_ID = int(ALLOWED_TOPIC_ID)

# Load JSON data
with open("all_wordnet_words_cleaned.json", "r", encoding="utf-8") as f:
    word_data = json.load(f)

# Restriction logic
def is_allowed_location(update: Update) -> bool:
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    if ALLOWED_TOPIC_ID:
        return chat_id == ALLOWED_GROUP_ID and thread_id == ALLOWED_TOPIC_ID
    else:
        return chat_id == ALLOWED_GROUP_ID

# --- Bot Handlers ---

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_location(update): return
    if not context.args:
        await update.message.reply_text("❗ Usage: /ask <word>")
        return
    word = context.args[0].lower()
    if word not in word_data:
        await update.message.reply_text(f"❌ Word '{word}' not found.")
        return
    data = word_data[word]
    reply = f"📘 *{word.capitalize()}*\n"
    reply += f"📌 *Part of Speech:* {', '.join(data['part_of_speech'])}\n\n"
    if data["definitions"]:
        reply += "*Definitions:*\n"
        for i, d in enumerate(data["definitions"], 1):
            reply += f"{i}. {d}\n"
    if data["examples"]:
        reply += "\n*Examples:*\n"
        for ex in data["examples"]:
            reply += f"• {ex}\n"
    if data["synonyms"]:
        reply += f"\n*Synonyms:* {', '.join(data['synonyms'])}\n"
    if data["antonyms"]:
        reply += f"*Antonyms:* {', '.join(data['antonyms'])}\n"
    await update.message.reply_text(reply, parse_mode="Markdown")

async def syno_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_location(update): return
    if not context.args:
        await update.message.reply_text("❗ Usage: /syno <word>")
        return
    word = context.args[0].lower()
    if word not in word_data or not word_data[word]["synonyms"]:
        await update.message.reply_text(f"⚠️ No synonyms found for '{word}'.")
        return
    await update.message.reply_text(
        f"🔁 *Synonyms for {word}:*\n{', '.join(word_data[word]['synonyms'])}",
        parse_mode="Markdown"
    )

async def anto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_location(update): return
    if not context.args:
        await update.message.reply_text("❗ Usage: /anto <word>")
        return
    word = context.args[0].lower()
    if word not in word_data or not word_data[word]["antonyms"]:
        await update.message.reply_text(f"⚠️ No antonyms found for '{word}'.")
        return
    await update.message.reply_text(
        f"🔃 *Antonyms for {word}:*\n{', '.join(word_data[word]['antonyms'])}",
        parse_mode="Markdown"
    )

async def get_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await update.message.reply_text(
        f"Group ID: `{chat_id}`\nThread ID: `{thread_id}`",
        parse_mode="Markdown"
    )

async def ignore_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

# --- Bot App ---
def start_bot():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("ask", ask_command))
    app.add_handler(CommandHandler("syno", syno_command))
    app.add_handler(CommandHandler("anto", anto_command))
    app.add_handler(CommandHandler("getid", get_ids))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ignore_all))

    print("✅ Bot is running...")
    app.run_polling()

# --- Flask App for UptimeRobot ---
flask_app = Flask(__name__)
@flask_app.route("/")
def home():
    return "✅ Vocab bot is alive."

# --- Run both Flask + Bot together ---
if __name__ == "__main__":
    Thread(target=start_bot).start()
    flask_app.run(host="0.0.0.0", port=10000)
