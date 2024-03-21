from enum import Enum


class CommonUserCommands(Enum):
    START = "Перезапустить бота"
    RESET_USER = "Сбросить состояние (применять в случае, если бот завис)"


class AdminCommands(Enum):
    START = "Перезапустить бота"
    ADD_ADMIN = "Добавить администратора"
    SET_QUIZZES_SOURCE = "Изменить ссылку на таблицу с вопросами викторины"
    RESET_USER = "Сбросить состояние (удалить себя из базы данных)"


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
