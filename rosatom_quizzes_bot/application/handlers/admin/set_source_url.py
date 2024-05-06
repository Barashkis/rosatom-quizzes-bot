import logging
import os

from aiogram import (
    Dispatcher,
    types,
)
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from rosatom_quizzes_bot.application.filters import AdminFilter


logger = logging.getLogger(__name__)


async def set_quizzes_source_handler(message: types.Message, state: FSMContext) -> None:
    logger.debug(f"Admin {message.from_user.id} enters set_quizzes_source handler")

    await message.answer("Отправьте ссылку на таблицу Google Sheets c вопросами викторины")
    await state.set_state("send_quizzes_source")


async def receive_quizzes_source_handler(message: types.Message, state: FSMContext) -> None:
    logger.debug(f"Admin {message.from_user.id} enters receive_quizzes_source handler")

    quizzes_source = message.text
    if "https://docs.google.com/spreadsheets/d/" not in quizzes_source:
        logger.info(f"Admin {message.from_user.id} enters invalid quizzes source url (url={quizzes_source!r})")
        await message.answer("Отправленное вами сообщение не является ссылкой. Повторите попытку еще раз")
        return

    os.environ["QUIZZES_SOURCE"] = quizzes_source
    await message.answer("Ссылка на таблицу была успешно обновлена")

    await state.finish()


def setup_source_url_routes(dp: Dispatcher) -> None:
    dp.register_message_handler(set_quizzes_source_handler, AdminFilter(), Command("set_quizzes_source"))
    dp.register_message_handler(receive_quizzes_source_handler, state="send_quizzes_source")
