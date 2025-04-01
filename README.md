# 🚗 Бот для поиска автомобильных номеров

Telegram-бот для поиска красивых номеров (зеркальные, тройные и т.д.).  
Работает на Python 3.10+ с библиотекой `python-telegram-bot`.

## 📌 Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш_логин/car_numbers_bot.git
   cd car_numbers_bot
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Создайте файл `.env` (на основе `.env.example`) и добавьте токен:
   ```ini
   BOT_TOKEN=7828617294:AAEk-WlSN2ZJlttlvNdqF0XQr1hKu0IUAdc
   ADMINS=222771008
   ```

4. Запустите бота:
   ```bash
   python3 bot.py
   ```

## 🛠 Команды бота
- `/start` — начать работу.
- Поиск по цене, категориям и добавление номеров.

**Разработано для macOS/Linux.**
