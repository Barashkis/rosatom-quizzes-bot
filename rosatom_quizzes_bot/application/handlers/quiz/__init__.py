from logging import getLogger

from aiogram import (
    Dispatcher,
    types,
)
from aiogram.dispatcher import FSMContext

from rosatom_quizzes_bot.application.context import (
    dispatcher_context,
    quiz_service_context,
    user_repository_context,
)
from rosatom_quizzes_bot.application.converters import (
    from_str_name_to_direction,
)
from rosatom_quizzes_bot.application.enums import Direction
from rosatom_quizzes_bot.application.handlers.quiz.prepare_user import (
    prepare_user_to_quiz_handler,
)
from rosatom_quizzes_bot.application.keyboards import (
    choose_quiz_type_cd,
    repeat_quiz_kb,
    start_quiz_cd,
)


__all__ = (
    "setup_quiz_routes",
)

from rosatom_quizzes_bot.data import basic_quiz_messages


logger = getLogger(__name__)


async def first_question_handler(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    logger.debug(f"User {call.from_user.id} enters first_question handler")

    await call.message.edit_reply_markup()
    service = quiz_service_context.get(call.bot)

    direction_name = callback_data["direction_name"]
    quiz = await service.get_random_direction_quiz(direction_name)
    correct_answer_sequence_id = service.correct_answer_sequence_id(quiz)
    await call.message.answer_poll(
        question=quiz.question,
        options=[a.text for a in quiz.answers],
        is_anonymous=False,
        type="quiz",
        allows_multiple_answers=False,
        correct_option_id=correct_answer_sequence_id,
        explanation=quiz.note,
    )
    if (link := quiz.link) is not None:
        await call.message.answer(link)

    async with state.proxy() as data:
        data.update(
            {
                "direction_name": direction_name,
                "correct_answer_id": correct_answer_sequence_id,
                "exclude_ids": [quiz.id],
                "score": 0,
            },
        )


async def pass_quiz_handler(poll_answer: types.PollAnswer):
    user_id = poll_answer.user.id

    bot = poll_answer.bot
    dp = dispatcher_context.get(bot)
    state = dp.current_state()
    async with state.proxy() as data:
        direction_name = data["direction_name"]
        exclude_ids = data["exclude_ids"]

        if data["correct_answer_id"] in poll_answer.option_ids:
            data["score"] += 1
        score = data["score"]

    passed_quizzes_count = len(exclude_ids)
    quiz_number = passed_quizzes_count + 1
    logger.debug(f"User {user_id} enters pass_quiz handler (quiz_number={quiz_number})")

    repository = user_repository_context.get(bot)
    user = await repository.get_user(user_id)
    if from_str_name_to_direction(direction_name) == Direction.BASIC:
        if user.attempts == 3:
            if passed_quizzes_count in basic_quiz_messages:
                await bot.send_message(user_id, text=basic_quiz_messages[passed_quizzes_count])

    if passed_quizzes_count == 10:
        await repository.decrease_attempts(user_id)
        if (attempts := (user.attempts - 1)) > 0:
            if score < 7:
                await bot.send_message(
                    user_id,
                    text=f"Твой результат: {score} баллов. К сожалению, этого недостаточно, чтобы получить мерч. "
                         f"Попробуй пройти тест еще раз. У тебя осталось {attempts} из 3 попыток",
                    reply_markup=repeat_quiz_kb(direction_name=direction_name),
                )
            else:
                await bot.send_message(
                    user_id,
                    text=f"Твой результат: {score} баллов. "
                         "Подойди к стенду Росатома и покажи это сообщение, чтобы получить мерч",
                )
        else:
            if score < 7:
                await bot.send_message(
                    user_id,
                    text=f"Твой результат: {score} баллов. "
                         "К сожалению, этого недостаточно, чтобы получить мерч и у тебя больше не осталось попыток",
                )
            else:
                await bot.send_message(
                    user_id,
                    text=f"Твой результат: {score} баллов. "
                         "Подойди к стенду Росатома и покажи это сообщение, чтобы получить мерч",
                )

        await state.reset_data()
        return

    service = quiz_service_context.get(poll_answer.bot)
    quiz = await service.get_random_direction_quiz(direction=direction_name, exclude_ids=exclude_ids)
    correct_answer_sequence_id = service.correct_answer_sequence_id(quiz)
    await bot.send_poll(
        user_id,
        question=quiz.question,
        options=[a.text for a in quiz.answers],
        is_anonymous=False,
        type="quiz",
        allows_multiple_answers=False,
        correct_option_id=correct_answer_sequence_id,
        explanation=quiz.note,
    )
    if (link := quiz.link) is not None:
        await bot.send_message(user_id, text=link)

    async with state.proxy() as data:
        data["correct_answer_id"] = correct_answer_sequence_id
        data["exclude_ids"].append(quiz.id)


def setup_quiz_routes(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(prepare_user_to_quiz_handler, choose_quiz_type_cd.filter())
    dp.register_callback_query_handler(first_question_handler, start_quiz_cd.filter())
    dp.register_poll_answer_handler(pass_quiz_handler)
