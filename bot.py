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
API_TOKEN = os.getenv('API_TOKEN') or 'io-v2-...'  # Замените на ваш токен или установите переменную окружения

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
    # Отправляем сообщение "думаю" и сохраняем его как ответ на исходное сообщение
    thinking_message = await message.reply("🧠 Подождите, я думаю...")

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
        response = requests.post(url, headers=headers, json=data, timeout=60)  # Увеличен таймаут

        if response.status_code != 200:
            await thinking_message.edit_text(f"❌ Ошибка API: {response.status_code}")
            # Альтернатива, если edit_text не подходит: await message.answer(f"Ошибка API: {response.status_code}")
            return

        data_response = response.json()

        # Проверка наличия ключей
        if 'choices' not in data_response or not data_response['choices']:
            await thinking_message.edit_text("❓ Неправильный формат ответа от API")
            return

        text = data_response['choices'][0]['message']['content']

        # Исправлено экранирование для split
        if '</think>' in text and '\n\n' in text:
            # Предполагаем, что </think> и \n\n находятся вместе
            parts = text.split('</think>\n\n', 1)  # Разделяем только один раз
            if len(parts) > 1:
                bot_text = parts[1]
            else:
                # Если не нашли \n\n сразу после </think>, попробуем просто \n
                parts_alt = text.split('</think>\n', 1)
                if len(parts_alt) > 1:
                    bot_text = parts_alt[1]
                else:
                    # Если и это не помогло, отправляем весь текст
                    bot_text = text
        else:
            bot_text = text

        # Редактируем сообщение "думаю", заменяя его на ответ от нейросети
        # Используем message.answer, чтобы ответ был как ответ на сообщение пользователя
        await thinking_message.edit_text(bot_text, parse_mode="Markdown")

    except asyncio.TimeoutError:
        await thinking_message.edit_text("⏰ Время ожидания ответа от API истекло. Попробуйте ещё раз.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error: {e}")
        await thinking_message.edit_text("🌐 Ошибка соединения с API. Попробуйте ещё раз.")
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await thinking_message.edit_text("⚠️ Произошла ошибка при обработке запроса.")


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())