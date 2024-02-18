from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Optional


AnswerIdT = int
QuizIdT = int
NoteT = Optional[str]
QuestionT = str
LinkT = Optional[str]


@dataclass
class Admin:
    user_id: int


@dataclass
class User:
    user_id: int
    username: str
    attempts: int


@dataclass
class Answer:
    id: AnswerIdT
    quiz_id: QuizIdT
    text: str


@dataclass
class Quiz:
    id: int
    direction: str
    question: QuestionT
    link: LinkT
    answers: Sequence[Answer]
    correct_answer_id: AnswerIdT
    note: NoteT


class PostgresRepositoryInterface(ABC):
    ...


class ServiceInterface(ABC):
    ...
