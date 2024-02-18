from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from rosatom_quizzes_bot.application.enums import Direction
from rosatom_quizzes_bot.application.keyboards import (
    choose_direction_cd,
    choose_quiz_type_cd,
)


start_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=choose_direction_cd.new()),
            InlineKeyboardButton(text="Нет", callback_data=choose_quiz_type_cd.new(value=Direction.BASIC.name)),
        ],
    ],
)

directions_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=direction.value,
                callback_data=choose_quiz_type_cd.new(value=direction.name),
            )
        ]
        for direction in Direction if direction is not Direction.BASIC
    ],
)
