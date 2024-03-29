import logging

from aiogram import types

from rosatom_quizzes_bot.application.context import user_repository_context


logger = logging.getLogger(__name__)


async def reset_user_handler(message: types.Message):
    user_id = message.from_user.id
    logger.debug(f"User {user_id} enters reset_user handler")

    repository = user_repository_context.get(message.bot)
    await repository.delete_user(user_id)

    await message.answer(
        "Вы можете снова выбрать роль и проходить тестирование. Для начала процесса воспользуйтесь командой /start",
    )
