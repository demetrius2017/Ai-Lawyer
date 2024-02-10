from telegram import Update, ForceReply
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

import logging
from tellogging import setup_logger
from main import set_logger  # Импортируйте функцию set_logger
import os
from main import process_document
import main

TOKEN = os.getenv("TELEGRAM_TOKEN")
assert TOKEN, "Токен бота не задан"
# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR)
logger = logging.getLogger(__name__)

import aiohttp


async def download_file(file_path: str, file_url: str):
    # Создаем папку, если она не существует
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            if resp.status == 200:
                with open(file_path, "wb") as f:
                    f.write(await resp.read())


# Команда start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {user.mention_markdown_v2()}! Отправь мне документ в формате docx для анализа.",
        reply_markup=ForceReply(selective=True),
        parse_mode="MarkdownV2",
    )
    chat_id = update.message.chat_id
    # Настройка логгера для отправки сообщений в чат пользователя
    logger = setup_logger(TOKEN, chat_id)
    # Передача логгера в main для дальнейшего использования
    set_logger(logger)  # Установка глобального logger в main.py

    logger.info("Бот запущен. Ожидаю документы для анализа.")


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    # Настройка логгера для отправки сообщений в чат пользователя
    logger = setup_logger(TOKEN, [chat_id])
    # Передача логгера в main для дальнейшего использования
    set_logger(logger)  # Установка глобального logger в main.py
    logger.telega("Бот запущен. Ожидаю документы для анализа.")

    document = update.message.document
    if document.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file = await context.bot.get_file(document.file_id)
        file_url = file.file_path  # Получение URL для скачивания файла
        file_path = f"./recieved/{document.file_name}"
        file_send = f"./sent/processed_{document.file_name}"

        # Загрузка файла
        await download_file(file_path, file_url)

        await update.message.reply_text("Документ получен, начинаю анализ...")

        # Здесь ваш код для анализа документа
        process_document(file_path)

        # После анализа отправьте результат пользователю
        await update.message.reply_document(document=open(file_send, "rb"))
    else:
        await update.message.reply_text("Пожалуйста, отправьте документ в формате docx.")


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, document_handler))

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
