import logging

from aiogram import Dispatcher
from aiogram.utils import executor

from migrations import migrate_postgres
from rosatom_quizzes_bot.application import build_dispatcher
from rosatom_quizzes_bot.application.context import setup_context
from rosatom_quizzes_bot.application.filters import setup_filters
from rosatom_quizzes_bot.application.routes import setup_routes
from rosatom_quizzes_bot.application.utils import setup_commands
from rosatom_quizzes_bot.config import load_config
from rosatom_quizzes_bot.logger import setup_logger


logger = logging.getLogger("rosatom_quizzes_bot")


async def on_startup(dp: Dispatcher) -> None:
    bot = dp.bot
    config = bot["config"]
    setup_logger(config.logger)

    await migrate_postgres("postgres", config.postgres)

    setup_routes(dp)
    setup_filters(dp)

    await setup_context(dp)
    await setup_commands(dp)

    logger.info("Bot started")


async def on_shutdown(dp: Dispatcher) -> None:
    await dp.bot.close()
    await dp.storage.close()

    logger.info("Bot stopped")


def main():
    dp = build_dispatcher(load_config())
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == "__main__":
    main()
