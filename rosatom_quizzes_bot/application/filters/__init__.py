from aiogram import Dispatcher

from rosatom_quizzes_bot.application.filters.admin import AdminFilter


def setup_filters(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)
