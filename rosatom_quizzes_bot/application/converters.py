from typing import Optional

from rosatom_quizzes_bot.application.enums import Direction


def from_str_name_to_direction(value: str) -> Optional[Direction]:
    for d in Direction:
        if value == d.name:
            return d
    return None


def to_direction_name(value: str) -> str:
    return Direction(value).name


def to_not_empty_str(value: str) -> Optional[str]:
    if not value:
        return None
    return value.strip()
