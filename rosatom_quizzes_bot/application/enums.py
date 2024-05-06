from enum import Enum


class CommonUserCommands(Enum):
    RESTORE_QUIZ = "Восстановить викторину (если бот завис или удалена переписка, применять в первую очередь)"


class AdminCommands(Enum):
    ADD_ADMIN = "Добавить администратора"
    SET_QUIZZES_SOURCE = "Изменить ссылку на таблицу с вопросами викторины"
    RESTORE_QUIZ = "Восстановить викторину (если бот завис или удалена переписка)"
    RESET_USER = (
        "Сбросить состояние пользователя по идентификатору пользователя "
        "(в случае, если восстановление викторины у пользователя не работает)"
    )
    RESET_MYSELF = "Сбросить собственное состояние"


class Direction(Enum):
    BASIC = "Вопросы для всех"

    DIGITALIZATION = "Цифровизация"
    SCIENCE = "Наука"
    ENERGETICS = "Атомная и альтернативная энергетика"
    ENGINEERING = "Проектирование и строительство"
    NEW_MATERIALS = "Новые материалы"
    NORTHERN_SEA_ROUTE = "Северный морской путь"
    ECOLOGY = "Экология"
    PRODUCTION = "Производство"
    INTERNATIONAL_ACTIVITIES = "Международная деятельность"
    NUCLEAR_MEDICINE = "Ядерная медицина"
