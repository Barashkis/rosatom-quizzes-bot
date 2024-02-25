from dataclasses import dataclass
from datetime import tzinfo
from pathlib import Path
from urllib.parse import ParseResult

from environs import Env
from pytz import timezone


@dataclass
class PostgresConfig:
    host: str
    port: int
    password: str
    user: str
    database: str

    @property
    def dsn(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class RedisConfig:
    host: str
    port: int
    password: str


@dataclass
class LoggerConfig:
    logs_dir: Path
    timezone: tzinfo


@dataclass
class QuizzesServiceConfig:
    source: ParseResult
    access_file_path: str
    polling_interval_minutes: int


@dataclass
class Config:
    token: str
    postgres: PostgresConfig
    redis: RedisConfig
    logger: LoggerConfig
    quizzes_service: QuizzesServiceConfig


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        token=env.str("TOKEN"),
        postgres=PostgresConfig(
            host=env.str("POSTGRES_HOST"),
            port=env.int("POSTGRES_PORT"),
            password=env.str("POSTGRES_PASSWORD"),
            user=env.str("POSTGRES_USER"),
            database=env.str("POSTGRES_DATABASE"),
        ),
        redis=RedisConfig(
            host=env.str("REDIS_HOST"),
            port=env.int("REDIS_PORT"),
            password=env.str("REDIS_PASSWORD"),
        ),
        logger=LoggerConfig(
            logs_dir=Path(env.str("LOGS_DIR")),
            timezone=timezone(env.str("LOGS_TZ")),
        ),
        quizzes_service=QuizzesServiceConfig(
            source=env.url("QUIZZES_SOURCE_URL"),
            access_file_path=env.path("ACCESS_FILE_PATH"),
            polling_interval_minutes=env.int("POLLING_INTERVAL_MINUTES")
        ),
    )
