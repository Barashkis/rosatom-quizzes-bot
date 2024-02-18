from aiogram import Dispatcher

from rosatom_quizzes_bot.application.handlers import (
    setup_admin_routes,
    setup_quiz_routes,
    setup_start_routes,
)


def setup_routes(dp: Dispatcher) -> None:
    setup_admin_routes(dp)
    setup_start_routes(dp)
    setup_quiz_routes(dp)
