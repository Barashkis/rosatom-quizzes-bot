from enum import Enum
from typing import (
    List,
    Type,
)

from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
)
from aiogram.utils.exceptions import ChatNotFound

from rosatom_quizzes_bot.application.context import user_repository_context
from rosatom_quizzes_bot.application.enums import (
    AdminCommands,
    CommonUserCommands,
)


def _build_bot_commands(commands_enum: Type[Enum]) -> List[BotCommand]:
    return [BotCommand(cmd.name.lower(), cmd.value) for cmd in commands_enum]


async def setup_admin_commands(bot: Bot, user_id: int) -> None:
    repository = user_repository_context.get(bot)

    async for admin_id in repository.get_admins():
        if user_id == admin_id:
            await bot.set_my_commands(
                _build_bot_commands(AdminCommands),
                scope=BotCommandScopeChat(chat_id=user_id),
            )


async def setup_commands(dp: Dispatcher) -> None:
    repository = user_repository_context.get(dp.bot)

    await dp.bot.set_my_commands(_build_bot_commands(CommonUserCommands))
    admins_ids = [admin.user_id async for admin in repository.get_admins()]
    for admin_id in admins_ids:
        try:
            await dp.bot.set_my_commands(
                _build_bot_commands(AdminCommands),
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        except ChatNotFound:
            pass
