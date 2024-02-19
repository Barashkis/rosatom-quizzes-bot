from aiogram import Dispatcher
from aiogram.dispatcher.filters import Command

from rosatom_quizzes_bot.application.filters import AdminFilter

from .reset_user import reset_user_handler
from .set_source_url import (
    receive_quizzes_source_handler,
    set_quizzes_source_handler,
)


__all__ = (
    "setup_admin_routes",
)


def setup_admin_routes(dp: Dispatcher) -> None:
    dp.register_message_handler(reset_user_handler, AdminFilter(), Command("reset_user"))
    dp.register_message_handler(set_quizzes_source_handler, AdminFilter(), Command("set_quizzes_source"))
    dp.register_message_handler(receive_quizzes_source_handler, state="send_quizzes_source")
