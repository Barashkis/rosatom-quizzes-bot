import logging
import os

from aiogram.types import (
    CallbackQuery,
    InputFile,
    InputMediaPhoto,
    MediaGroup,
)
from aiogram.utils.markdown import hlink

from rosatom_quizzes_bot.application.converters import (
    from_str_name_to_direction,
)
from rosatom_quizzes_bot.application.enums import Direction
from rosatom_quizzes_bot.application.keyboards import start_quiz_kb


logger = logging.getLogger(__name__)


async def prepare_user_to_quiz_handler(call: CallbackQuery, callback_data: dict):
    logger.debug(f"User {call.from_user.id} enters prepare_user_to_quiz handler")

    await call.message.edit_reply_markup()

    direction_name = callback_data["value"]
    if from_str_name_to_direction(direction_name) == Direction.BASIC:
        await call.message.answer(
            "Росатом - глобальный технологический лидер, обладающий ресурсами и компетенциями для выработки атомной"
            " энергии и не только. Ведь чтобы построить АЭС, нужно её сконструировать, протестировать модель "
            "(и смоделировать даже самые невероятные сценарии, чтобы точно быть уверенными в безопасности), затем "
            "построить, оснастить, загрузить топливо и только после этого дать старт. За каждым киловаттом энергии "
            "стоят тысячи людей, отвечающих за самые разные задачи. Росатом - больше, чем АЭС.\n\n"
            "Сегодня Росатом – одна из самых крупных и динамично развивающихся российских компаний, реализует "
            "10 направлений деятельности. А это значит, что работу здесь может найти каждый: и айтишник, и инженер, "
            "и химик, и бухгалтер, и переводчик. ⚛️💙",
        )
        await call.message.answer(
            "Открой для себя атомную отрасль с другой стороны! Читай информацию в карточках, "
            f"подписывайся на наши социальные сети ({hlink('Telegram', 'https://t.me/rosatom_career')}, "
            f"{hlink('ВКонтакте', 'https://vk.com/rosatomcareer')}) и изучай карьерный портал."
        )

        imgs_dir = os.path.join("media", "img")
        await call.message.answer_media_group(
            MediaGroup(
                [
                    InputMediaPhoto(InputFile(os.path.join(imgs_dir, img)))
                    for img in sorted(os.listdir(imgs_dir), key=lambda filename: int(filename.split(".")[0]))
                ],
            ),
        )

    await call.message.answer(
        "Пройди краткий тест об атомной отрасли, набери не менее 7 правильных ответов и получи атомный мерч!",
        reply_markup=start_quiz_kb(direction_name=direction_name),
    )
