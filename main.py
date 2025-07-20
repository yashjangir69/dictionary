import os
import json
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Load word data
with open("all_wordnet_words_cleaned.json", "r", encoding="utf-8") as f:
    word_data = json.load(f)

# Environment variables
TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_TOPIC_ID = int(os.getenv("ALLOWED_TOPIC_ID", "12345"))  # Replace 12345 or use real ID

# Flask setup
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot is running!"

# Check if the command is from the allowed topic
def in_allowed_topic(update: Update):
    thread_id = update.message.message_thread_id
    return thread_id == ALLOWED_TOPIC_ID

# ----------------- Command Handlers -----------------

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not in_allowed_topic(update):
        return
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
    if not in_allowed_topic(update):
        return
    if not context.args:
        await update.message.reply_text("❗ Usage: /syno <word>")
        return
    word = context.args[0].lower()
    if word not in word_data or not word_data[word]["synonyms"]:
        await update.message.reply_text(f"⚠️ No synonyms found for '{word}'.")
        return
    await update.message.reply_text(f"🔁 *Synonyms for {word}:*\n{', '.join(word_data[word]['synonyms'])}", parse_mode="Markdown")

async def anto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not in_allowed_topic(update):
        return
    if not context.args:
        await update.message.reply_text("❗ Usage: /anto <word>")
        return
    word = context.args[0].lower()
    if word not in word_data or not word_data[word]["antonyms"]:
        await update.message.reply_text(f"⚠️ No antonyms found for '{word}'.")
        return
    await update.message.reply_text(f"🔃 *Antonyms for {word}:*\n{', '.join(word_data[word]['antonyms'])}", parse_mode="Markdown")

async def ignore_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return  # Ignore any non-command message

# ----------------- Run Bot -----------------

def run_bot():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("syno", syno_command))
    application.add_handler(CommandHandler("anto", anto_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ignore_all))

    application.run_polling()

if __name__ == "__main__":
    run_bot()
