import logging

from aiogram import types
from aiogram.utils.markdown import hcode


logger = logging.getLogger(__name__)


async def show_user_id_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    logger.debug(f"User {user_id} enters show_user_id_handler")

    await message.answer(hcode(user_id))
