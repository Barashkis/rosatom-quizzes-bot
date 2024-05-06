import logging

from aiogram import (
    Dispatcher,
    types,
)
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils.markdown import hbold

from rosatom_quizzes_bot.application.context import user_repository_context
from rosatom_quizzes_bot.application.keyboards import (
    choose_direction_cd,
    directions_kb,
    start_kb,
)
from rosatom_quizzes_bot.application.utils import setup_admin_commands


logger = logging.getLogger(__name__)


async def start_handler(message: types.Message):
    user_id = message.from_user.id
    logger.debug(f"User {user_id} enters start handler")

    bot = message.bot
    await setup_admin_commands(bot, user_id)

    repository = user_repository_context.get(bot)
    user = await repository.get_user(id_=user_id)
    if user is not None:
        await message.answer(
            "Похоже, ты уже запускал бота ранее, так что ты уже можешь приступать к прохождению теста.\n\n"
            "Важно: у тебя всего три попытки на прохождение!\n\n"
            "Если ты не можешь приступить к прохождению теста или его продолжению из-за того, что переписка с ботом "
            "удалена либо бот перестал тебе отвечать, воспользуйся командой /restore_quiz",
        )
        return

    await repository.add_user(user_id=user_id, username=message.from_user.username)

    await message.answer(
        f"Знаешь ли ты, в каком {hbold('направлении деятельности')} хочешь развиваться в будущем?",
        reply_markup=start_kb,
    )


async def choose_direction_handler(call: types.CallbackQuery):
    logger.debug(f"User {call.from_user.id} enters choose_direction handler")

    await call.message.edit_text("Отлично! Выбери свое направление", reply_markup=directions_kb)


def setup_start_routes(dp: Dispatcher) -> None:
    dp.register_message_handler(start_handler, CommandStart())
    dp.register_callback_query_handler(choose_direction_handler, choose_direction_cd.filter())
