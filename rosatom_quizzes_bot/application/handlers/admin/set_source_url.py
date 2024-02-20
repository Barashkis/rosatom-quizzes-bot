import logging
import os

from aiogram import types
from aiogram.dispatcher import FSMContext


logger = logging.getLogger(__name__)


async def set_quizzes_source_handler(message: types.Message, state: FSMContext):
    logger.debug(f"Admin {message.from_user.id} enters set_quizzes_source handler")

    await message.answer("Отправьте ссылку на таблицу Google Sheets c вопросами викторины")
    await state.set_state("send_quizzes_source")


async def receive_quizzes_source_handler(message: types.Message, state: FSMContext):
    logger.debug(f"Admin {message.from_user.id} enters receive_quizzes_source handler")

    quizzes_source = message.text
    if "https://docs.google.com/spreadsheets/d/" not in quizzes_source:
        await message.answer("Отправленное вами сообщение не является ссылкой. Повторите попытку еще раз")

        logger.info(f"Admin {message.from_user.id} enters invalid quizzes source url (url={quizzes_source!r})")
        return

    os.environ["QUIZZES_SOURCE"] = quizzes_source
    await message.answer("Ссылка на таблицу была успешно обновлена")

    await state.finish()
