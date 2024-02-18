import logging
import os
from datetime import datetime
from logging import (
    LogRecord,
    StreamHandler,
)
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Callable

from rosatom_quizzes_bot.config import LoggerConfig


__all__ = (
    "setup_logger",
)


class _LocalTimeFormatter(logging.Formatter):
    @staticmethod
    def _convert_to_datetime(timestamp: float) -> datetime:
        return datetime.fromtimestamp(timestamp).astimezone()

    def formatTime(self, record: LogRecord, date_format: str = None):
        if not date_format:
            date_format = "%d-%m-%Y %H:%M:%S"
        date_string = self._convert_to_datetime(record.created).strftime(date_format)

        return date_string


def _namer(config: LoggerConfig) -> Callable[[str], str]:
    def wrapper(_) -> str:
        return str(Path(config.logs_dir, f"logfile.{datetime.now(tz=config.timezone).strftime('%d-%m-%Y')}.log"))
    return wrapper


def setup_logger(config: LoggerConfig) -> None:
    if not os.path.exists(config.logs_dir):
        os.mkdir(config.logs_dir)

    logger = logging.getLogger("rosatom_quizzes_bot")
    logger.setLevel(logging.DEBUG)

    time_handler = TimedRotatingFileHandler(
        filename=Path(config.logs_dir, "logfile.log"),
        when="d",
        backupCount=31,
    )
    time_handler.namer = _namer(config)

    stream_handler = StreamHandler()

    formatter = _LocalTimeFormatter("{asctime}: {filename}: {levelname} - {message}", style="{")
    time_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(time_handler)
    logger.addHandler(stream_handler)
