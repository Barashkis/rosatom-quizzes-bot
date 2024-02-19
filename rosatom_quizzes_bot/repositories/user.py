from textwrap import dedent
from typing import (
    AsyncIterator,
    Optional,
)

from asyncpg import Pool

from rosatom_quizzes_bot.application.interfaces import (
    Admin,
    PostgresRepositoryInterface,
    User,
)


class UserRepository(PostgresRepositoryInterface):
    def __init__(self, pool: Pool):
        self._pool = pool

    async def get_admin(self, id_: int) -> Optional[Admin]:
        async with self._pool.acquire() as conn:
            record = await conn.fetchrow("SELECT * FROM admin WHERE user_id = $1;", id_)

        if record is None:
            return None

        return Admin(user_id=record["user_id"])

    async def get_admins(self) -> AsyncIterator[Admin]:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                async for admin in conn.cursor("SELECT user_id FROM admin;"):
                    yield Admin(user_id=admin["user_id"])

    async def get_user(self, id_: int) -> Optional[User]:
        async with self._pool.acquire() as conn:
            record = await conn.fetchrow("SELECT username, attempts FROM user_ WHERE user_id = $1;", id_)

        if record is None:
            return None

        return User(
            user_id=id_,
            username=record["username"],
            attempts=record["attempts"],
        )

    async def add_user(self, user_id: int, username: str) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute("INSERT INTO user_ (user_id, username) VALUES ($1, $2);", user_id, username)

    async def delete_user(self, user_id: int) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute("DELETE FROM user_ WHERE user_id = $1;", user_id)

    async def decrease_attempts(self, user_id: int) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                dedent(
                    """
                        UPDATE user_ SET attempts = attempts - 1
                        WHERE user_id = $1
                        RETURNING attempts
                    """,
                ),
                user_id,
            )
