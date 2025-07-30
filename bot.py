import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
# Импортируем утилиту для экранирования Markdown
from aiogram.utils.text_decorations import markdown_decoration
import requests
from requests.exceptions import Timeout, RequestException

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


# Вспомогательная функция для безопасной отправки текста с Markdown
async def safe_edit_text(message_obj, text, parse_mode=None):
    """Пытается отредактировать сообщение с указанным parse_mode.
       Если возникает ошибка парсинга, отправляет без разметки."""
    try:
        await message_obj.edit_text(text, parse_mode=parse_mode)
    except Exception as e:  # Ловим любую ошибку редактирования
        if "can't parse entities" in str(e):  # Проверяем, связана ли она с Markdown
            logging.warning(f"Failed to parse Markdown for message ID {message_obj.message_id}. Sending plain text.")
            # Если ошибка парсинга, отправляем без разметки
            await message_obj.edit_text(text, parse_mode=None)
        else:
            # Если ошибка другая, пробрасываем её
            raise


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
        # Увеличен таймаут для запроса до 120 секунд
        response = requests.post(url, headers=headers, json=data, timeout=120)

        if response.status_code != 200:
            await safe_edit_text(thinking_message, f"❌ Ошибка API: {response.status_code}")
            return

        data_response = response.json()

        # Проверка наличия ключей
        if 'choices' not in data_response or not data_response['choices']:
            await safe_edit_text(thinking_message, "❓ Неправильный формат ответа от API")
            return

        text = data_response['choices'][0]['message']['content']

        # Исправлено экранирование для split
        if '  </think>' in text and '\n\n' in text:
            # Предполагаем, что   </think> и \n\n находятся вместе
            parts = text.split('  </think>\n\n', 1)  # Разделяем только один раз
            if len(parts) > 1:
                bot_text = parts[1]
            else:
                # Если не нашли \n\n сразу после   </think> , попробуем просто \n
                parts_alt = text.split('  </think>\n', 1)
                if len(parts_alt) > 1:
                    bot_text = parts_alt[1]
                else:
                    # Если и это не помогло, отправляем весь текст
                    bot_text = text
        else:
            bot_text = text

        # Редактируем сообщение "думаю", заменяя его на ответ от нейросети
        # Проверим длину сообщения, так как Telegram имеет ограничения
        if len(bot_text) > 4096:
            # Если сообщение слишком длинное, отправим его частями
            # или как документ/файл. Для простоты отправим первые 4000 символов
            # и уведомим пользователя.
            part_text = bot_text[:4000] + "\n\n(Ответ слишком длинный, обрезан для отображения)"
            # Пробуем отправить с Markdown, если не получится - без него
            await safe_edit_text(thinking_message, part_text, parse_mode="Markdown")
        else:
            # Пробуем отправить с Markdown, если не получится - без него
            await safe_edit_text(thinking_message, bot_text, parse_mode="Markdown")

    except Timeout:
        # Обработка таймаута
        await safe_edit_text(thinking_message,
                             "⏰ Время ожидания ответа от нейросети истекло. Запрос был слишком сложным или сервер перегружен. Попробуйте ещё раз.")
        logging.warning(f"Request to {url} timed out for user message: {message.text}")
    except RequestException as e:
        # Обработка других сетевых ошибок
        logging.error(f"Network error during request: {e}")
        await safe_edit_text(thinking_message,
                             "🌐 Ошибка соединения с API нейросети. Проверьте подключение или попробуйте позже.")
    except Exception as e:
        # Обработка всех остальных ошибок
        logging.error(f"Unexpected error processing message: {e}", exc_info=True)
        await safe_edit_text(thinking_message, "⚠️ Произошла непредвиденная ошибка при обработке вашего запроса.")


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())