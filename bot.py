# -*- coding: utf-8 -*-
import os
BOT_TOKEN = os.getenv("7828617294:AAEk-WlSN2ZJlttlvNdqF0XQr1hKu0IUAdc")  # получаем токен из переменных окружения
ADMINS = list(map(int, os.getenv("222771008").split(",")))  # получаем список админов
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)
import secrets
import time

# Глобальные переменные
EDITORS = {}  # {user_id: {"username": str, "invite_code": str, "added_by": int}}
NUMBERS_DB = []
USER_STATES = {}
INVITES = {}  # {"код": {"admin_id": int, "username": str, "expires": float}}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    
    # Обработка приглашения через /start invite_код
    if args and args[0].startswith('invite_'):
        invite_code = args[0][7:]
        await handle_invite_start(update, context, user_id, invite_code)
        return
    
    # Обычное меню
    buttons = [
        [KeyboardButton("🔍 Поиск по цене")],
        [KeyboardButton("🪞 Зеркалки"), KeyboardButton("🔢 Тройные")],
        [KeyboardButton("🟰 Ровные"), KeyboardButton("✨ Красивые буквы")]
    ]
    
    if user_id in ADMINS or user_id in EDITORS:
        buttons.append([KeyboardButton("➕ Добавить номер")])
    if user_id in ADMINS:
        buttons.append([KeyboardButton("👑 Админ-панель")])
    
    await update.message.reply_text(
        "🚗 Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

async def handle_invite_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, invite_code: str):
    """Обработка старта с приглашением"""
    if invite_code not in INVITES:
        await update.message.reply_text("❌ Недействительный код приглашения!")
        return
    
    if INVITES[invite_code]["expires"] < time.time():
        await update.message.reply_text("❌ Срок действия приглашения истёк!")
        del INVITES[invite_code]
        return
    
    username = update.effective_user.username
    if not username:
        await update.message.reply_text("❌ У вас должен быть username в Telegram!")
        return
    
    # Добавляем редактора
    EDITORS[user_id] = {
        "username": username.lower(),
        "invite_code": invite_code,
        "added_by": INVITES[invite_code]["admin_id"]
    }
    
    # Удаляем использованное приглашение
    del INVITES[invite_code]
    
    # Уведомляем админа
    admin_id = EDITORS[user_id]["added_by"]
    try:
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"✅ Пользователь @{username} принял ваше приглашение и теперь редактор!"
        )
    except Exception as e:
        print(f"Ошибка уведомления админа: {e}")
    
    # Приветствуем нового редактора
    await update.message.reply_text(
        "🎉 Теперь вы редактор бота!\n"
        "Вы можете добавлять новые номера через меню.",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/start")]], resize_keyboard=True)
    )

async def show_admin_panel(update: Update):
    buttons = [
        [KeyboardButton("👥 Список редакторов")],
        [KeyboardButton("✉️ Создать приглашение")],
        [KeyboardButton("➖ Удалить редактора")],
        [KeyboardButton("↩️ В меню")]
    ]
    await update.message.reply_text(
        "Админ-панель:",
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Основной обработчик сообщений"""
    user_id = update.effective_user.id
    text = update.message.text

    # Обработка навигации
    if text in ["↩️ Назад", "↩️ В меню"]:
        await start(update, context)
        return

    # Проверка состояния пользователя
    if user_id in USER_STATES:
        await handle_user_state(update, context, user_id, text)
        return

    # Основные команды
    if text == "🔍 Поиск по цене":
        await update.message.reply_text("Введите диапазон цен (например: 1000-5000):")
    
    elif text == "➕ Добавить номер":
        if user_id not in ADMINS and user_id not in EDITORS:
            await update.message.reply_text("❌ Недостаточно прав!")
            return
        USER_STATES[user_id] = {"step": "waiting_number"}
        await update.message.reply_text("Введите номер (формат: А123АА или А123АА77):")
    
    elif text == "👑 Админ-панель":
        if user_id not in ADMINS:
            await update.message.reply_text("❌ Только для админов!")
            return
        await show_admin_panel(update)
    
    elif text == "👥 Список редакторов":
        if user_id not in ADMINS:
            await update.message.reply_text("❌ Только для админов!")
            return
        
        editors_list = []
        for editor_id, data in EDITORS.items():
            status = f"👤 @{data['username']} (добавил: {data['added_by']})"
            editors_list.append(status)
        
        response = "Текущие редакторы:\n" + "\n".join(editors_list) if editors_list else "Нет редакторов"
        await update.message.reply_text(response)
    
    elif text == "✉️ Создать приглашение":
        if user_id not in ADMINS:
            await update.message.reply_text("❌ Только для админов!")
            return
        
        # Генерируем уникальный код
        invite_code = secrets.token_hex(8)
        INVITES[invite_code] = {
            "admin_id": user_id,
            "username": None,
            "expires": time.time() + 86400  # 24 часа
        }
        
        invite_link = f"https://t.me/{context.bot.username}?start=invite_{invite_code}"
        
        await update.message.reply_text(
            "🔐 Одноразовое приглашение создано!\n\n"
            f"Код: <code>{invite_code}</code>\n"
            f"Ссылка: {invite_link}\n\n"
            "Отправьте этот код пользователю, который должен стать редактором.",
            parse_mode="HTML"
        )
    
    elif text == "➖ Удалить редактора":
        if user_id not in ADMINS:
            await update.message.reply_text("❌ Только для админов!")
            return
        
        USER_STATES[user_id] = {"step": "waiting_editor_remove"}
        buttons = [[KeyboardButton("↩️ Отмена")]]
        
        editors_list = []
        for editor_id, data in EDITORS.items():
            editors_list.append([KeyboardButton(f"👤 @{data['username']} (удалить)")])
        
        if not editors_list:
            await update.message.reply_text("Нет редакторов для удаления")
            return
        
        buttons = editors_list + [[KeyboardButton("↩️ Отмена")]]
        
        await update.message.reply_text(
            "Выберите редактора для удаления:",
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        )
    
    elif "-" in text:
        await handle_price_search(update, text)
    
    elif text in ["🪞 Зеркалки", "🔢 Тройные", "🟰 Ровные", "✨ Красивые буквы"]:
        await handle_category_search(update, text)

async def handle_user_state(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, text: str):
    state = USER_STATES[user_id]
    
    if text == "↩️ Отмена":
        del USER_STATES[user_id]
        await show_admin_panel(update) if user_id in ADMINS else await start(update, context)
        return

    # Удаление редактора
    if state["step"] == "waiting_editor_remove":
        if text.startswith("👤 @"):
            username = text.split("@")[1].split(" ")[0]
            
            # Находим редактора по username
            editor_id = next((uid for uid, data in EDITORS.items() if data["username"] == username.lower()), None)
            
            if editor_id:
                del EDITORS[editor_id]
                await update.message.reply_text(
                    f"✅ Редактор @{username} удалён!",
                    reply_markup=ReplyKeyboardMarkup([[KeyboardButton("👑 Админ-панель")]], resize_keyboard=True)
                )
            else:
                await update.message.reply_text(
                    f"❌ Редактор @{username} не найден",
                    reply_markup=ReplyKeyboardMarkup([[KeyboardButton("👑 Админ-панель")]], resize_keyboard=True)
                )
        else:
            await update.message.reply_text("❌ Используйте кнопки для выбора")
        
        del USER_STATES[user_id]
    
    # Добавление номера
    elif state["step"] == "waiting_number":
        if not (len(text) in [6, 8] and 
                text[:1].isalpha() and 
                text[1:4].isdigit() and 
                text[4:6].isalpha() and
                (len(text) == 6 or text[6:].isdigit())):
            await update.message.reply_text("❌ Неверный формат! Примеры: А123АА или А123АА77")
            return
        
        state["number"] = text.upper()
        state["step"] = "waiting_price"
        await update.message.reply_text("Введите цену (только цифры):")
    
    elif state["step"] == "waiting_price":
        if not text.isdigit():
            await update.message.reply_text("❌ Цена должна быть числом!")
            return
        state["price"] = int(text)
        state["step"] = "waiting_types"
        state["selected_types"] = []
        
        buttons = [
            [KeyboardButton("🪞 Зеркальный")],
            [KeyboardButton("🔢 Тройной")],
            [KeyboardButton("🟰 Ровный")],
            [KeyboardButton("✨ Красивый")],
            [KeyboardButton("✅ Готово")]
        ]
        
        await update.message.reply_text(
            "Выберите один или несколько типов (нажимайте кнопки несколько раз):\n"
            "Выбрано: " + ", ".join(state["selected_types"]) if state["selected_types"] else "Ничего не выбрано",
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        )
    
    elif state["step"] == "waiting_types":
        type_map = {
            "🪞 Зеркальный": "зеркальный",
            "🔢 Тройной": "тройной",
            "🟰 Ровный": "ровный",
            "✨ Красивый": "красивый"
        }
        
        if text == "✅ Готово":
            if not state["selected_types"]:
                await update.message.reply_text("❌ Выберите хотя бы один тип!")
                return
            
            # Сохраняем номер в базу
            NUMBERS_DB.append({
                "number": state["number"],
                "price": state["price"],
                "types": state["selected_types"],
                "added_by": user_id
            })
            
            del USER_STATES[user_id]
            await update.message.reply_text(
                f"✅ Номер {state['number']} добавлен!\n"
                f"Типы: {', '.join(state['selected_types'])}",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("/start")]], resize_keyboard=True)
            )
        elif text in type_map:
            type_name = type_map[text]
            if type_name in state["selected_types"]:
                state["selected_types"].remove(type_name)
            else:
                state["selected_types"].append(type_name)
            
            # Обновляем сообщение с текущим выбором
            buttons = [
                [KeyboardButton("🪞 Зеркальный")],
                [KeyboardButton("🔢 Тройной")],
                [KeyboardButton("🟰 Ровный")],
                [KeyboardButton("✨ Красивый")],
                [KeyboardButton("✅ Готово")]
            ]
            
            await update.message.reply_text(
                "Выберите один или несколько типов:\n"
                f"Выбрано: {', '.join(state['selected_types']) if state['selected_types'] else 'Ничего не выбрано'}",
                reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            )

async def handle_price_search(update: Update, text: str):
    try:
        price_from, price_to = map(int, text.split("-"))
        results = [n for n in NUMBERS_DB if price_from <= n["price"] <= price_to]
        
        if not results:
            await update.message.reply_text("❌ Нет номеров в этом диапазоне")
            return
            
        response = "🔎 Результаты:\n" + "\n".join(
            f"{n['number']} - {n['price']} руб. (Типы: {', '.join(n['types'])})"
            for n in sorted(results, key=lambda x: x["price"])
        )
        await update.message.reply_text(response)
    except:
        await update.message.reply_text("❌ Неверный формат! Введите 'от-до' (например: 1000-5000)")

async def handle_category_search(update: Update, category: str):
    category_map = {
        "🪞 Зеркалки": "зеркальный",
        "🔢 Тройные": "тройной",
        "🟰 Ровные": "ровный",
        "✨ Красивые буквы": "красивый"
    }
    category_name = category_map[category]
    
    results = [n for n in NUMBERS_DB if category_name in n["types"]]
    
    if not results:
        await update.message.reply_text(f"❌ Нет номеров в категории '{category}'")
        return
        
    response = f"📋 {category}:\n" + "\n".join(
        f"{n['number']} - {n['price']} руб. (Типы: {', '.join(n['types'])})"
        for n in sorted(results, key=lambda x: x["price"])
    )
    await update.message.reply_text(response)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("accept_invite_"):
        invite_code = query.data.split("_")[2]
        user_id = query.from_user.id
        username = query.from_user.username

        if not username:
            await query.edit_message_text("❌ У вас должен быть username в Telegram!")
            return

        if invite_code not in INVITES:
            await query.edit_message_text("❌ Приглашение недействительно или истекло!")
            return

        # Добавляем редактора
        EDITORS[user_id] = {
            "username": username.lower(),
            "invite_code": invite_code,
            "added_by": INVITES[invite_code]["admin_id"]
        }

        # Удаляем использованное приглашение
        del INVITES[invite_code]

        # Уведомляем админа
        admin_id = EDITORS[user_id]["added_by"]
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"✅ Пользователь @{username} принял ваше приглашение!"
            )
        except:
            pass

        await query.edit_message_text(
            "🎉 Теперь вы редактор бота!\n"
            "Вы можете добавлять новые номера через меню."
        )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    application.run_polling()

if __name__ == "__main__":
    main()
