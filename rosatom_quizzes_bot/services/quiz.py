import random
import re
from collections.abc import (
    Iterator,
    Sequence,
)
from logging import getLogger
from typing import Optional
from urllib.parse import ParseResult

import gspread
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from gspread import Worksheet

from rosatom_quizzes_bot.application.converters import (
    to_direction_name,
    to_not_empty_str,
)
from rosatom_quizzes_bot.application.interfaces import (
    Answer,
    AnswerIdT,
    LinkT,
    NoteT,
    QuestionT,
    Quiz,
    ServiceInterface,
)
from rosatom_quizzes_bot.repositories import QuizRepository


logger = getLogger(__name__)


QuizDataT = list[str]


class QuizService(ServiceInterface):
    def __init__(
            self,
            repository: QuizRepository,
            scheduler: AsyncIOScheduler,
            source: ParseResult,
            access_file_path: str,
            polling_interval_minutes: int,
    ):
        self._source_url = source.geturl()
        self._polling_interval_minutes = polling_interval_minutes

        self.repository = repository
        self.gc = gspread.service_account(filename=access_file_path)

        self.__current_quiz_id = 1
        self.__current_answer_id = 1

        scheduler.add_job(self.scan_quizzes_google_sheets, "interval", minutes=polling_interval_minutes)

    def __reset_private_ids(self):
        self.__current_quiz_id = 1
        self.__current_answer_id = 1

    @staticmethod
    def correct_answer_sequence_id(quiz: Quiz) -> AnswerIdT:
        answers = quiz.answers
        for sequence_answer_id in range(len(answers)):
            if answers[sequence_answer_id].id == quiz.correct_answer_id:
                return sequence_answer_id

    @staticmethod
    def _extract_question_data(full_question_text: str) -> tuple[QuestionT, LinkT]:
        if (question_info := re.match(r"(.+)\s\((.*)\)", full_question_text)) is not None:
            groups = question_info.groups()
            question = groups[0]
            link = to_not_empty_str(groups[1])
        else:
            question, link = full_question_text, None

        return question, link

    def _extract_answers(self, quiz_data: QuizDataT) -> tuple[list[Answer], AnswerIdT, NoteT]:
        note = None
        answers: list[Answer] = []

        raw_answers = quiz_data[1:]
        for answer_text in raw_answers:
            if answer_text:
                if right_answer_data := re.match(r"(.+)\s\((\+)[;\s]?(.*)\)", answer_text):
                    answer_text, _, note = right_answer_data.groups()
                    correct_answer_id = self.__current_answer_id

                answers.append(
                    Answer(
                        id=self.__current_answer_id,
                        quiz_id=self.__current_quiz_id,
                        text=answer_text,
                    )
                )
                self.__current_answer_id += 1

        return answers, correct_answer_id, to_not_empty_str(note)  # noqa

    def _iterate_sheet_quizzes(self, sheet: Worksheet) -> Iterator[Quiz]:
        direction_name = to_direction_name(sheet.title)
        rows: list[QuizDataT] = sheet.get_all_values()

        for quiz_row in zip(*rows):
            if full_question := quiz_row[0]:
                question, link = self._extract_question_data(full_question)
                answers, correct_answer_id, note = self._extract_answers(quiz_row)
                yield Quiz(
                    id=self.__current_quiz_id,
                    direction=direction_name,
                    question=question,
                    link=link,
                    answers=answers,
                    correct_answer_id=correct_answer_id,
                    note=note,
                )

                self.__current_quiz_id += 1

    async def _upsert_quizzes(self, sheet: Worksheet):
        logger.debug(f"Scanning sheet (title={sheet.title!r})")

        for quiz in self._iterate_sheet_quizzes(sheet):
            await self.repository.upsert_full_quiz(quiz)

    async def scan_quizzes_google_sheets(self) -> None:
        logger.debug(
            "Start google sheets scanning "
            f"(url={self._source_url!r}, interval_minutes={self._polling_interval_minutes})"
        )

        for sheet in self.gc.open_by_url(self._source_url):
            await self._upsert_quizzes(sheet)
        self.__reset_private_ids()

    async def get_random_direction_quiz(
            self,
            direction: str,
            exclude_ids: Optional[Sequence[int]] = None,
    ) -> Quiz:
        quizzes_ids = await self.repository.fetch_quizzes_ids(direction)
        if exclude_ids is not None:
            quizzes_ids = list(set(quizzes_ids).difference(set(exclude_ids)))

        return await self.repository.fetch_full_quiz(random.choice(quizzes_ids))
