import asyncio
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hbold

from rosatom_quizzes_bot.application.context import (
    quiz_repository_context,
    quiz_service_context,
    user_repository_context,
)
from rosatom_quizzes_bot.application.keyboards import start_kb


logger = logging.getLogger(__name__)


async def restore_quiz_handler(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    logger.debug(f"User {user_id} enters restore_quiz handler")

    bot = message.bot
    quiz_repository = quiz_repository_context.get(bot)
    user_repository = user_repository_context.get(bot)
    service = quiz_service_context.get(bot)

    await asyncio.sleep(.5)
    user = await user_repository.get_user(user_id)
    if user.attempts == 0:
        await message.answer(
            "К сожалению, ты потратил все свои три попытки... Но, если ты набрал в одном из тестов "
            "7 баллов или более, ты можешь показать этот результат на стенде Росатома и получить атомный мерч!",
        )
        return

    async with state.proxy() as data:
        if (exclude_ids := data.get("exclude_ids")) is None:
            await message.answer(
                f"Знаешь ли ты, в каком {hbold('направлении деятельности')} хочешь развиваться в будущем?",
                reply_markup=start_kb,
            )
            return
        last_quiz_id = exclude_ids[-1]

    quiz = await quiz_repository.fetch_full_quiz(last_quiz_id)
    correct_answer_sequence_id = service.correct_answer_sequence_id(quiz)
    question = quiz.question
    options = [a.text for a in quiz.answers]
    note = quiz.note

    logger.debug(
        f"Sending first poll to user {user_id} "
        f"(question={question!r}, options={options}, correct_answer_id={correct_answer_sequence_id}, note={note!r})"
    )
    obj = await message.answer_poll(
        question=question,
        options=options,
        is_anonymous=False,
        type="quiz",
        allows_multiple_answers=False,
        correct_option_id=correct_answer_sequence_id,
        explanation=note,
    )
    async with state.proxy() as data:
        data["quizzes_mapping_ids"][obj.poll.id] = quiz.id
