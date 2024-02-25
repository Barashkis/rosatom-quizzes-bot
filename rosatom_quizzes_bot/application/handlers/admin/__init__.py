from aiogram import Dispatcher
from aiogram.dispatcher.filters import Command

from rosatom_quizzes_bot.application.filters import (
    AdminFilter,
    AdminIdMessageFilter,
    BackMessageFilter,
)

from .add_admin import (
    add_admin_handler,
    cancel_adding_admin_handler,
    request_admin_id_handler,
    show_user_id_handler,
    wrong_admin_id_handler,
)
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
    dp.register_message_handler(request_admin_id_handler, AdminFilter(), Command("add_admin"))
    dp.register_message_handler(show_user_id_handler, Command("id"))

    dp.register_message_handler(set_quizzes_source_handler, AdminFilter(), Command("set_quizzes_source"))
    dp.register_message_handler(receive_quizzes_source_handler, state="send_quizzes_source")
    dp.register_message_handler(add_admin_handler, AdminIdMessageFilter(), state="send_new_admin_id")
    dp.register_message_handler(cancel_adding_admin_handler, BackMessageFilter(), state="send_new_admin_id")
    dp.register_message_handler(wrong_admin_id_handler, state="send_new_admin_id")
