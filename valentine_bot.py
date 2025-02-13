import logging
import os
import sqlite3
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database setup
conn = sqlite3.connect('valentines.db', check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS valentines
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              sender_id INTEGER,
              recipient_id INTEGER,
              message TEXT,
              timestamp DATETIME)''')
conn.commit()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
RECIPIENT, MESSAGE = range(2)

# Get bot token from environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in .env file")

# Custom keyboard markup
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("/sendvalentine"), KeyboardButton("/myvalentines")],
            [KeyboardButton("/help")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    c.execute('''INSERT OR REPLACE INTO users 
                 (user_id, username, first_name, last_name) 
                 VALUES (?, ?, ?, ?)''',
              (user.id, user.username, user.first_name, user.last_name))
    conn.commit()
    
    await update.message.reply_text(
        f"❤️ Welcome to Anonymous Valentines Bot, {user.first_name}!\n\n"
        "Use the buttons below to send or check valentines!",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "💝 Bot Commands:\n"
        "/sendvalentine - Send anonymous Valentine\n"
        "/myvalentines - Check received Valentines\n"
        "/help - Show this message",
        reply_markup=get_main_keyboard()
    )

async def send_valentine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Enter the recipient's @username:",
        reply_markup=ReplyKeyboardRemove()
    )
    return RECIPIENT

async def recipient_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    recipient_username = update.message.text.strip('@')
    context.user_data['recipient'] = recipient_username
    
    c.execute('SELECT user_id FROM users WHERE username = ?', (recipient_username,))
    result = c.fetchone()
    
    if not result:
        await update.message.reply_text(
            "❌ User not found. They need to start the bot first!",
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
    
    await update.message.reply_text("💌 Write your anonymous message:")
    return MESSAGE

async def message_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message.text
    sender = update.effective_user
    recipient_username = context.user_data['recipient']
    
    try:
        c.execute('SELECT user_id FROM users WHERE username = ?', (recipient_username,))
        recipient_id = c.fetchone()[0]
        
        c.execute('''INSERT INTO valentines 
                     (sender_id, recipient_id, message, timestamp)
                     VALUES (?, ?, ?, ?)''',
                  (sender.id, recipient_id, message, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        
        await update.message.reply_text(
            "✅ Valentine sent successfully!",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            "❌ Failed to send. Please try again!",
            reply_markup=get_main_keyboard()
        )
    
    return ConversationHandler.END

async def show_valentines(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    try:
        c.execute('''SELECT message, timestamp 
                     FROM valentines 
                     WHERE recipient_id = ? 
                     ORDER BY timestamp DESC''', (user.id,))
        valentines = c.fetchall()
        
        if not valentines:
            await update.message.reply_text(
                "💔 No Valentines yet! Send some love first!",
                reply_markup=get_main_keyboard()
            )
            return
        
        response = "💌 Your Secret Valentines:\n\n"
        for i, (message, timestamp) in enumerate(valentines, 1):
            response += f"{i}. {message}\n"
            response += f"   🕒 {timestamp}\n\n"
        
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            "❌ Failed to load Valentines. Try again!",
            reply_markup=get_main_keyboard()
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Operation cancelled.",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

def main() -> None:
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('sendvalentine', send_valentine)],
        states={
            RECIPIENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, recipient_received)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myvalentines", show_valentines))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()