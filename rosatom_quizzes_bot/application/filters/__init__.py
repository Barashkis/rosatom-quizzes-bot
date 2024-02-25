from aiogram import Dispatcher

from rosatom_quizzes_bot.application.filters.admin import (
    AdminFilter,
    AdminIdMessageFilter,
    BackMessageFilter,
)


def setup_filters(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(AdminIdMessageFilter)
    dp.filters_factory.bind(BackMessageFilter)
