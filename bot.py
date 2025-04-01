# -*- coding: utf-8 -*-
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =====================
# НАСТРОЙКИ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS_STR = os.getenv("ADMINS", "")  # Второй аргумент "" - значение по умолчанию

# Проверка обязательных переменных
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не установлен! Добавьте его в Environment Variables на Render")

if not ADMINS_STR:
    raise ValueError("❌ ADMINS не установлены! Добавьте ID админов через запятую в Render")

# Преобразуем ADMINS в список чисел
try:
    ADMINS = [int(admin_id.strip()) for admin_id in ADMINS_STR.split(",") if admin_id.strip()]
except ValueError:
    raise ValueError("❌ Неверный формат ADMINS! Используйте числа, разделенные запятыми (например: 123,456)")

# =====================
# ОСНОВНОЙ КОД БОТА
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMINS:
        await update.message.reply_text("⛔ У вас нет доступа!")
        return

    buttons = [
        [KeyboardButton("🔍 Поиск по цене")],
        [KeyboardButton("🪞 Зеркалки"), KeyboardButton("🔢 Тройные")],
    ]
    await update.message.reply_text(
        "🚗 Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔍 Поиск по цене":
        await update.message.reply_text("Введите диапазон цен (например: 1000-5000):")
    elif text in ["🪞 Зеркалки", "🔢 Тройные"]:
        await update.message.reply_text(f"Вы выбрали категорию: {text}")

# =====================
# ЗАПУСК БОТА
# =====================
def main():
    print("🟢 Бот запускается...")
    print(f"👑 Админы: {ADMINS}")

    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🔎 Бот запущен. Ожидаем сообщения...")
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        raise
