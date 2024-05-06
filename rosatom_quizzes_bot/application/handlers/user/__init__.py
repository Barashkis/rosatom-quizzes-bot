from aiogram import Dispatcher
from aiogram.dispatcher.filters import Command

from .restore_quiz import restore_quiz_handler
from .show_user_id import show_user_id_handler
from .start import setup_start_routes


__all__ = (
    "setup_user_routes",
)


def setup_user_routes(dp: Dispatcher) -> None:
    setup_start_routes(dp)

    dp.register_message_handler(show_user_id_handler, Command("id"), state="*")
    dp.register_message_handler(restore_quiz_handler, Command("restore_quiz"))
