import logging

from aiogram import (
    Dispatcher,
    types,
)
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from rosatom_quizzes_bot.application.context import user_repository_context
from rosatom_quizzes_bot.application.filters import AdminFilter


logger = logging.getLogger(__name__)


async def request_user_to_reset_handler(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    logger.debug(f"Admin {user_id} enters request_user_to_reset handler")

    await state.set_state("send_user_id_to_reset")
    await message.answer(
        "Введите идентификатор в Telegram пользователя, состояние которого вы хотите сбросить. "
        "Для этого попросите его воспользоваться командой /id и сообщить его вам"
    )


async def reset_user_handler(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_to_reset_id = int(message.text)
    bot = message.bot
    logger.debug(f"Admin {user_id} enters reset_user handler (user_to_reset_id={user_to_reset_id})")

    repository = user_repository_context.get(message.bot)
    user_to_reset = await repository.get_user(user_to_reset_id)
    if user_to_reset is None:
        await message.answer("Вы ввели неправильный идентификатор пользователя. Повторите попытку еще раз")
        return

    await repository.delete_user(user_to_reset_id)

    await message.answer(f"Состояние пользователя @{user_to_reset.username} успешно сброшено")
    await bot.send_message(
        user_to_reset_id,
        text="Ты можешь снова выбрать роль и проходить тестирование. Для начала процесса воспользуйся командой /start",
    )

    await state.finish()


async def reset_admin_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    logger.debug(f"Admin {user_id} enters reset_admin handler")

    repository = user_repository_context.get(message.bot)
    await repository.delete_user(user_id)

    await message.answer(
        "Вы можете снова выбрать роль и проходить тестирование. Для начала процесса воспользуйтесь командой /start",
    )


def setup_reset_user_routes(dp: Dispatcher) -> None:
    dp.register_message_handler(reset_admin_handler, AdminFilter(), Command("reset_myself"))

    dp.register_message_handler(request_user_to_reset_handler, AdminFilter(), Command("reset_user"))
    dp.register_message_handler(reset_user_handler, state="send_user_id_to_reset")
