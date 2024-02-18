from contextvars import ContextVar
from typing import (
    Generic,
    Optional,
    TypeVar,
)

import asyncpg
from aiogram import (
    Bot,
    Dispatcher,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from rosatom_quizzes_bot.config import Config
from rosatom_quizzes_bot.repositories import (
    QuizRepository,
    UserRepository,
)
from rosatom_quizzes_bot.services import QuizService


__all__ = (
    "config_context",
    "dispatcher_context",
    "scheduler_context",

    "user_repository_context",
    "quiz_repository_context",

    "quiz_service_context",

    "setup_context",
)


T = TypeVar("T")


POSTGRES_POOL = ContextVar("postgres_pool")


class BotContext(Generic[T]):
    __slots__ = ("_key",)

    def __init__(self, key: str) -> None:
        self._key = key

    def setup(self, bot: Bot, value: T) -> None:
        bot[self._key] = value

    def get(self, bot: Bot) -> Optional[T]:
        return bot.get(self._key)


config_context: BotContext[Config] = BotContext("config")

quiz_repository_context: BotContext[QuizRepository] = BotContext("quiz_repository")
user_repository_context: BotContext[UserRepository] = BotContext("user_repository")

scheduler_context: BotContext[AsyncIOScheduler] = BotContext("scheduler")
dispatcher_context: BotContext[Dispatcher] = BotContext("dispatcher")

quiz_service_context: BotContext[QuizService] = BotContext("quiz_service")


async def setup_postgres_pool(bot: Bot):
    config = config_context.get(bot)
    pool = await asyncpg.create_pool(config.postgres.dsn)
    POSTGRES_POOL.set(pool)


def setup_quiz_repository_context(bot: Bot):
    pool = POSTGRES_POOL.get()
    repository = QuizRepository(pool)

    quiz_repository_context.setup(bot, repository)


def setup_user_repository_context(bot: Bot):
    pool = POSTGRES_POOL.get()
    repository = UserRepository(pool)

    user_repository_context.setup(bot, repository)


async def setup_repositories(bot: Bot) -> None:
    await setup_postgres_pool(bot)

    setup_quiz_repository_context(bot)
    setup_user_repository_context(bot)


def setup_scheduler_context(bot: Bot) -> None:
    scheduler = AsyncIOScheduler()
    scheduler.start()
    scheduler_context.setup(bot, scheduler)


def setup_quiz_service_context(bot: Bot) -> None:
    config = config_context.get(bot).quizzes_service
    repository = quiz_repository_context.get(bot)
    scheduler = scheduler_context.get(bot)
    quiz_service_context.setup(
        bot,
        QuizService(
            repository,
            scheduler,
            source=config.source,
            access_file_path=config.access_file_path,
            polling_interval_minutes=config.polling_interval_minutes,
        )
    )


def setup_services(bot: Bot) -> None:
    setup_scheduler_context(bot)
    setup_quiz_service_context(bot)


async def setup_context(dp: Dispatcher) -> None:
    bot = dp.bot
    dispatcher_context.setup(bot, dp)

    await setup_repositories(bot)
    setup_services(bot)
