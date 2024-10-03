import asyncio
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


async def first_question_handler(call: types.CallbackQuery, state: FSMContext, callback_data: dict) -> None:
    user_id = call.from_user.id

    bot = call.bot
    repository = user_repository_context.get(bot)
    service = quiz_service_context.get(bot)

    await asyncio.sleep(.5)
    await call.message.edit_reply_markup()

    direction_name = callback_data["direction_name"]

    user = await repository.get_user(user_id)
    if user.attempts == 0:
        logger.debug(f"User {user_id} enters first_question handler with no attempts (direction={direction_name!r})")
        await call.message.answer(
            "К сожалению, ты потратил все свои три попытки... Но, если ты набрал в одном из тестов "
            "7 баллов или более, ты можешь показать этот результат на стенде Росатома и получить атомный мерч!",
        )
        return

    logger.debug(f"User {user_id} enters first_question handler (direction={direction_name!r})")

    quiz = await service.get_random_direction_quiz(direction_name)
    correct_answer_sequence_id = service.correct_answer_sequence_id(quiz)

    question = quiz.question
    options = [a.text for a in quiz.answers]
    note = quiz.note
    logger.debug(
        f"Sending first poll to user {user_id} "
        f"(question={question!r}, options={options}, correct_answer_id={correct_answer_sequence_id}, note={note!r})"
    )

    await asyncio.sleep(.5)
    async with state.proxy() as data:
        data.update(
            {
                "direction_name": direction_name,
                "correct_answer_id": correct_answer_sequence_id,
                "exclude_ids": [quiz.id],
                "answered_quizzes_ids": [],
                "quizzes_mapping_ids": {},
                "question_number": 1,
                "score": 0,
            },
        )

    obj = await call.message.answer_poll(
        question=question,
        options=options,
        is_anonymous=False,
        type="quiz",
        allows_multiple_answers=False,
        correct_option_id=correct_answer_sequence_id,
        explanation=note,
    )
    if (link := quiz.link) is not None:
        await call.message.answer(link)

    async with state.proxy() as data:
        data["quizzes_mapping_ids"] = {obj.poll.id: quiz.id}


async def pass_quiz_handler(poll_answer: types.PollAnswer) -> None:
    user_id = poll_answer.user.id
    poll_id = poll_answer.poll_id

    bot = poll_answer.bot
    service = quiz_service_context.get(bot)
    repository = user_repository_context.get(bot)
    dp = dispatcher_context.get(bot)

    state = dp.current_state()

    async with (state.proxy() as data):
        direction_name = data["direction_name"]

    user = await repository.get_user(user_id)
    if user.attempts == 0:
        logger.debug(f"User {user_id} enters pass_quiz handler with no attempts (direction={direction_name!r})")
        await bot.send_message(
            user_id,
            text="К сожалению, ты потратил все свои три попытки... Но, если ты набрал в одном из тестов "
                 "7 баллов или более, ты можешь показать этот результат на стенде Росатома и получить атомный мерч!",
        )
        return

    await asyncio.sleep(.5)
    async with (state.proxy() as data):
        if (exclude_ids := data.get("exclude_ids")) is None:
            logger.debug(
                f"User {user_id} enters pass_quiz handler trying to "
                f"answer duplicate already passed quiz (direction={direction_name!r})",
            )
            await bot.send_message(
                user_id,
                text="Ты уже закончил прохождение теста. Если у тебя остались попытки и ты не набрал необходимое "
                     "количество баллов для получения мерча, ты можешь пройти тест заново",
            )
            return

        answered_quizzes_ids = data["answered_quizzes_ids"]
        quizzes_mapping_ids = data["quizzes_mapping_ids"]
        answered_quiz_id = quizzes_mapping_ids[poll_id]
        if answered_quiz_id in answered_quizzes_ids:
            logger.debug(
                f"User {user_id} enters pass_quiz handler trying to "
                f"answer duplicate quiz (direction={direction_name!r}, quiz_id={answered_quiz_id})",
            )
            await bot.send_message(
                user_id,
                text="Ты уже ответил на этот вопрос. Продолжай проходить тест, "
                     "чтобы получить баллы за правильные ответы и получить итоговый результат!",
            )
            return
        answered_quizzes_ids.append(answered_quiz_id)

    async with state.proxy() as data:
        question_number = data["question_number"]
        if data["correct_answer_id"] in poll_answer.option_ids:
            data["score"] += 1
        score = data["score"]
    logger.debug(f"User {user_id} enters pass_quiz handler (quiz_number={question_number})")

    passed_quizzes_count = len(exclude_ids)
    user = await repository.get_user(user_id)
    if from_str_name_to_direction(direction_name) == Direction.BASIC:
        if user.attempts == 3:
            if passed_quizzes_count in basic_quiz_messages:
                await bot.send_message(user_id, text=basic_quiz_messages[passed_quizzes_count])

    if question_number == 8:
        attempts = user.attempts - 1
        logger.debug(f"User {user_id} ends quiz (score={score}, remaining_attempts={attempts})")

        await repository.decrease_attempts(user_id)
        if score >= 6:
            await bot.send_message(
                user_id,
                text=f"Твой результат: {score} баллов. "
                     "Подойди к стенду Росатома и покажи это сообщение, чтобы получить мерч",
            )
            return

        additional_args = {}
        if attempts > 0:
            additional_args.update({"reply_markup": repeat_quiz_kb(direction_name=direction_name)})

        await bot.send_message(
            user_id,
            text=f"Твой результат: {score} баллов. К сожалению, этого недостаточно, чтобы получить мерч. "
                 f"Попробуй пройти тест еще раз. У тебя осталось {attempts} из 3 попыток",
            **additional_args,
        )

        await state.reset_data()
        async with state.proxy() as data:
            data["direction_name"] = direction_name

        return

    quiz = await service.get_random_direction_quiz(direction=direction_name, exclude_ids=exclude_ids)
    correct_answer_sequence_id = service.correct_answer_sequence_id(quiz)
    async with state.proxy() as data:
        data["correct_answer_id"] = correct_answer_sequence_id
        data["question_number"] += 1
        if quiz.id != exclude_ids[-1]:
            data["exclude_ids"].append(quiz.id)

    question = quiz.question
    options = [a.text for a in quiz.answers]
    note = quiz.note

    logger.debug(
        f"Sending poll to user {user_id} "
        f"(question={question!r}, options={options}, correct_answer_id={correct_answer_sequence_id}, note={note!r})"
    )
    obj = await bot.send_poll(
        user_id,
        question=question,
        options=options,
        is_anonymous=False,
        type="quiz",
        allows_multiple_answers=False,
        correct_option_id=correct_answer_sequence_id,
        explanation=note,
    )
    if (link := quiz.link) is not None:
        await bot.send_message(user_id, text=link)

    async with state.proxy() as data:
        data["quizzes_mapping_ids"][obj.poll.id] = quiz.id


def setup_quiz_routes(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(prepare_user_to_quiz_handler, choose_quiz_type_cd.filter())
    dp.register_callback_query_handler(first_question_handler, start_quiz_cd.filter())
    dp.register_poll_answer_handler(pass_quiz_handler)
