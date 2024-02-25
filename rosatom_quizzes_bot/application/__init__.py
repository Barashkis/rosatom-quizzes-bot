from aiogram import (
    Bot,
    Dispatcher,
)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import ParseMode

from rosatom_quizzes_bot.application.context import config_context
from rosatom_quizzes_bot.config import Config


def build_dispatcher(config: Config) -> Dispatcher:
    storage = RedisStorage2(
        host=redis_config.host,
        port=redis_config.port,
        password=redis_config.password,
    ) if (redis_config := config.redis) else MemoryStorage()
    bot = Bot(token=config.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(bot=bot, storage=storage)

    config_context.setup(bot, config)

    return dp
