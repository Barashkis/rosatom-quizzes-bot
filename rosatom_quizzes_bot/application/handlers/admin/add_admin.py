import logging

from aiogram import (
    Dispatcher,
    types,
)
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from rosatom_quizzes_bot.application.context import user_repository_context
from rosatom_quizzes_bot.application.filters import (
    AdminFilter,
    AdminIdMessageFilter,
    BackMessageFilter,
)
from rosatom_quizzes_bot.application.utils import setup_admin_commands


logger = logging.getLogger(__name__)


async def request_admin_id_handler(message: types.Message, state: FSMContext) -> None:
    logger.debug(f"Admin {message.from_user.id} enters request_admin_id_handler")

    await message.answer(
        "Перешлите в бота любое сообщение пользователя, которого хотите сделать модератором. "
        "Если его профиль закрыт, пришлите сообщение с его ID. Для этого попросите его воспользоваться командой "
        "/id и передать идентификатор Вам (сообщение с ID можно как прислать самому, "
        "так и переслать напрямую)"
    )

    await state.set_state("send_new_admin_id")


async def add_admin_handler(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    new_admin_id = message.forward_from.id if message.is_forward() else int(message.text)
    logger.debug(f"Admin {user_id} enters add_admin_handler (new_admin_id={new_admin_id!r})")

    bot = message.bot
    repository = user_repository_context.get(bot)

    admin = await repository.get_admin(new_admin_id)
    if admin is not None:
        logger.info(f"Admin {message.from_user.id} tries to add existing admin (admin_id={admin.user_id})")
        await message.answer(
            "Вы пытаетесь добавить администратора, который уже им является. "
            "Повторите попытку или напишите 'Назад', чтобы отменить процесс добавления администратора",
        )
        return
    await repository.add_admin(new_admin_id)

    await setup_admin_commands(bot, user_id)
    await message.answer("Пользователь был добавлен в список модераторов бота")
    await state.finish()


async def wrong_admin_id_handler(message: types.Message) -> None:
    logger.debug(f"Admin {message.from_user.id} enters wrong_admin_id_handler")

    await message.answer(
        "Вы неверно отправили сообщение для добавления администратора. "
        "Повторите попытку или напишите 'Назад', чтобы отменить процесс добавления администратора",
    )


async def cancel_adding_admin_handler(message: types.Message, state: FSMContext) -> None:
    logger.debug(f"Admin {message.from_user.id} enters add_admin_by_common_message_handler")

    await state.finish()
    await message.answer("Вы вернулись в главное меню и можете использоваться все команды")


def setup_add_admin_routes(dp: Dispatcher) -> None:
    dp.register_message_handler(request_admin_id_handler, AdminFilter(), Command("add_admin"))
    dp.register_message_handler(add_admin_handler, AdminIdMessageFilter(), state="send_new_admin_id")
    dp.register_message_handler(cancel_adding_admin_handler, BackMessageFilter(), state="send_new_admin_id")
    dp.register_message_handler(wrong_admin_id_handler, state="send_new_admin_id")
