import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.webhook.aiohttp import SimpleRequestHandler, setup_application
from aiohttp import web
import requests

# Получаем токены из переменных окружения (для безопасности)
TOKEN = os.getenv('BOT_TOKEN') or '8008209339:AAHfqQcOnF81bC4GeceqI-DYZEqGljDBw6E'
API_TOKEN = os.getenv(
    'API_TOKEN') or 'io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjA0M2UyYWRjLWNlMGQtNDdhMy1hY2RlLTEyMWU2MTk3MjcyZCIsImV4cCI6NDkwNzQwNDA3OX0.anZEz7MidIKi4NdLzAmvRyLzL0Ay_qVppUyTcymYrqcWWPZAjKNqgexgZiQYTEjAgh0AsvHEymAbJS4vR0eNhQ'

# URL для вебхука (Render предоставит его)
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', 'https://your-app.onrender.com')
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

PORT = int(os.environ.get('PORT', 8000))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


# КОМАНДА СТАРТ
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('Привет! Я бот с подключенной нейросетью, отправь свой запрос', parse_mode='HTML')


# ОБРАБОТЧИК ЛЮБОГО СООБЩЕНИЯ
@dp.message()
async def filter_messages(message: Message):
    url = "https://api.intelligence.io.solutions/api/v1/chat/completions"  # Убрал пробел

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}",
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

        if '</think>\n\n' in text:
            bot_text = text.split('</think>\n\n')[1]
        else:
            bot_text = text

        await message.answer(bot_text, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await message.answer("Произошла ошибка, попробуйте позже")


# Обработчик вебхука
async def on_startup(bot: Bot):
    # Удаляем вебхук и устанавливаем новый
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to: {WEBHOOK_URL}")


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    logging.info("Webhook deleted")


def main():
    app = web.Application()

    # Настройка вебхука
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    # Добавляем обработчики запуска и остановки
    app.on_startup.append(lambda app: on_startup(bot))
    app.on_shutdown.append(lambda app: on_shutdown(bot))

    # Запуск веб-сервера
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()