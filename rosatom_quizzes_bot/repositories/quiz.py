from collections.abc import AsyncIterable
from textwrap import dedent

from asyncpg import Pool

from rosatom_quizzes_bot.application.interfaces import (
    Answer,
    AnswerIdT,
    LinkT,
    NoteT,
    PostgresRepositoryInterface,
    Quiz,
    QuizIdT,
)


DirectionNameT = str
QuestionT = str


class QuizRepository(PostgresRepositoryInterface):
    def __init__(self, pool: Pool):
        self._pool = pool

    async def _insert_answer(
            self,
            id_: AnswerIdT,
            quiz_id: QuizIdT,
            text: str,
    ) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                dedent(
                    """
                        INSERT INTO answer (id, quiz_id, text)
                        VALUES ($1, $2, $3);
                    """
                ),
                id_, quiz_id, text,
            )

    async def _insert_quiz(
            self,
            id_: QuizIdT,
            direction: DirectionNameT,
            question: QuestionT,
            link: LinkT,
            correct_answer_id: AnswerIdT,
            note: NoteT,
    ) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                dedent(
                    """
                        INSERT INTO quiz (id, direction, question, link, correct_answer_id, note)
                        VALUES ($1, $2, $3, $4, $5, $6);
                    """
                ),
                id_, direction, question, link, correct_answer_id, note,
            )

    async def insert_full_quiz(self, quiz: Quiz) -> None:
        await self._insert_quiz(
            id_=quiz.id,
            direction=quiz.direction,
            question=quiz.question,
            link=quiz.link,
            correct_answer_id=quiz.correct_answer_id,
            note=quiz.note,
        )
        for answer in quiz.answers:
            await self._insert_answer(
                id_=answer.id,
                quiz_id=answer.quiz_id,
                text=answer.text,
            )

    async def _fetch_quiz(self, id_: int) -> tuple[DirectionNameT, QuestionT, LinkT, NoteT, AnswerIdT]:
        async with self._pool.acquire() as conn:
            record = await conn.fetchrow(
                dedent(
                    """
                        SELECT direction, question, link, note, correct_answer_id
                        FROM quiz WHERE id = $1;
                    """,
                ),
                id_,
            )

        return record["direction"], record["question"], record["link"], record["note"], record["correct_answer_id"]

    async def _fetch_quiz_answers(self, id_: QuizIdT) -> AsyncIterable[Answer]:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                async for record in conn.cursor(
                        dedent(
                            """
                                SELECT a.id, a.quiz_id, a.text
                                FROM quiz q
                                JOIN answer a ON q.id = a.quiz_id
                                WHERE q.id = $1;
                            """
                        ),
                        id_,
                ):
                    yield Answer(
                        id=record["id"],
                        quiz_id=record["quiz_id"],
                        text=record["text"],
                    )

    async def fetch_full_quiz(self, id_: QuizIdT) -> Quiz:
        direction_name, question, link, note, correct_answer_id = await self._fetch_quiz(id_)
        answers: list[Answer] = []
        async for answer in self._fetch_quiz_answers(id_):
            answers.append(answer)

        return Quiz(
            id=id_,
            direction=direction_name,
            question=question,
            link=link,
            answers=answers,
            correct_answer_id=correct_answer_id,
            note=note,
        )

    async def fetch_quizzes_ids(self, direction: str) -> list[int]:
        async with self._pool.acquire() as conn:
            records = await conn.fetch("SELECT id FROM quiz WHERE direction = $1;", direction)

        return [record["id"] for record in records]

    async def truncate_quizzes(self) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute("TRUNCATE TABLE quiz CASCADE;")
