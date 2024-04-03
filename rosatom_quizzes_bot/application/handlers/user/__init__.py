from aiogram import Dispatcher
from aiogram.dispatcher.filters import (
    Command,
    CommandStart,
)

from rosatom_quizzes_bot.application.keyboards import choose_direction_cd
from .reset_user import reset_user_handler

from .restore_quiz import restore_quiz_handler
from .start import (
    choose_direction_handler,
    start_handler,
)


__all__ = (
    "setup_user_routes",
)


def setup_user_routes(dp: Dispatcher) -> None:
    dp.register_message_handler(start_handler, CommandStart())
    dp.register_message_handler(reset_user_handler, Command("reset_user"))
    dp.register_message_handler(restore_quiz_handler, Command("restore_quiz"))
    dp.register_callback_query_handler(choose_direction_handler, choose_direction_cd.filter())
