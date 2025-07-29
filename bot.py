import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
import requests

# Получаем токены из переменных окружения (для безопасности)
TOKEN = os.getenv('BOT_TOKEN') or '8008209339:AAHfqQcOnF81bC4GeceqI-DYZEqGljDBw6E'
API_TOKEN = os.getenv(
    'API_TOKEN') or 'io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjA0M2UyYWRjLWNlMGQtNDdhMy1hY2RlLTEyMWU2MTk3MjcyZCIsImV4cCI6NDkwNzQwNDA3OX0.anZEz7MidIKi4NdLzAmvRyLzL0Ay_qVppUyTcymYrqcWWPZAjKNqgexgZiQYTEjAgh0AsvHEymAbJS4vR0eNhQ'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


# КОМАНДА СТАРТ
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer('Привет! Я бот с подключенной нейросетью, отправь свой запрос', parse_mode='HTML')


# ОБРАБОТЧИК ЛЮБОГО СООБЩЕНИЯ
@dp.message()
async def filter_messages(message: Message):
    url = "https://api.intelligence.io.solutions/api/v1/chat/completions"  # Убран лишний пробел

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",  # Используем переменную окружения
    }

    data = {
        "model": "deepseek-ai/DeepSeek-R1-0528",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant"
            },
            {
                "role": "user",
                "content": message.text
            }
        ],
    }

    try:
        # Добавлен таймаут для запроса
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print("Status code:", response.status_code)  # Для отладки
        print("Response:", response.text)  # Для отладки

        if response.status_code != 200:
            await message.answer("Ошибка API: " + response.text)
            return

        data_response = response.json()

        # Проверка наличия ключей
        if 'choices' not in data_response or not data_response['choices']:
            await message.answer("Неправильный формат ответа от API")
            return

        text = data_response['choices'][0]['message']['content']

        # Исправлено экранирование для split
        if '</think>\n\n' in text:
            bot_text = text.split('</think>\n\n')[1]
        else:
            bot_text = text

        await message.answer(bot_text, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await message.answer("Произошла ошибка, попробуйте позже")


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())