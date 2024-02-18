from aiogram.dispatcher.filters import BoundFilter

from rosatom_quizzes_bot.application.context import user_repository_context


class AdminFilter(BoundFilter):
    async def check(self, obj):
        repository = user_repository_context.get(obj.bot)

        admin = await repository.get_admin(id_=obj.from_user.id)
        return bool(admin)
