# -*- coding: utf-8 -*-
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ===== FLASK =====
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Бот активен. Сервер работает.", 200

# ===== TELEGRAM BOT =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот работает через Web Service!")

def run_bot():
    print("🟢 Запускаем Telegram бота...")
    bot = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    
    # Очистка старых подключений
    bot.post_init = lambda app: app.bot.delete_webhook(drop_pending_updates=True)
    
    # Команды
    bot.add_handler(CommandHandler("start", start))
    
    print("🔎 Бот готов к работе")
    bot.run_polling()

# ===== ЗАПУСК =====
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Запускаем Flask
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 10000)),  # Render сам подставит порт
        debug=False
    )
