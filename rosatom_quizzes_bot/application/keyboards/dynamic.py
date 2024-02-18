from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from rosatom_quizzes_bot.application.converters import (
    from_str_name_to_direction,
)
from rosatom_quizzes_bot.application.enums import Direction
from rosatom_quizzes_bot.application.keyboards.callback_data import (
    choose_direction_cd,
    start_quiz_cd,
)


def start_quiz_kb(direction_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Начать тест",
                    callback_data=start_quiz_cd.new(direction_name=direction_name),
                ),
            ],
        ],
    )


def repeat_quiz_kb(direction_name: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Пройти тест еще раз",
                    callback_data=start_quiz_cd.new(direction_name=direction_name),
                ),
            ],
        ],
    )
    if from_str_name_to_direction(direction_name) != Direction.BASIC:
        kb.add(
            InlineKeyboardButton(
                text="Сменить направление",
                callback_data=choose_direction_cd.new(),
            ),
        )

    return kb
