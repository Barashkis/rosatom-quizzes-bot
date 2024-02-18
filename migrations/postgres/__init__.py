import logging
import os
from glob import glob
from pathlib import Path
from textwrap import dedent

import asyncpg

from rosatom_quizzes_bot.config import PostgresConfig


__all__ = (
    "migrate_postgres",
)


logger = logging.getLogger("rosatom_quizzes_bot.migrations")

migrations_dir = "versions"


class MigrationError(Exception):
    pass


def _read_migration(filepath: Path) -> str:
    statements = []
    with open(filepath, encoding="utf-8") as file:
        for line in file.readlines():
            statements.append(line)

    return "\n".join(statements)


async def migrate_postgres(source_dir: str, config: PostgresConfig) -> None:
    logger.info("Starting migrations")

    connection = await asyncpg.connect(config.dsn)
    await connection.execute(
        dedent(
            """
                CREATE TABLE IF NOT EXISTS _migration (
                    id SERIAL,
                    version INTEGER DEFAULT 0
                );
            """,
        )
    )
    current_version = await connection.fetchval("SELECT version FROM _migration;")
    if current_version is None:
        current_version = 0
        await connection.execute("INSERT INTO _migration (version) VALUES ($1);", 0)

    workdir = str(Path("migrations", source_dir))
    unused_migrations = []
    for migration in glob(str(Path(workdir, migrations_dir, f"{'[0-9]' * 3}.sql"))):
        if os.path.isfile(migration):
            if (version := int(Path(migration).stem)) > current_version:
                unused_migrations.append(version)

    if unused_migrations:
        unused_migrations.sort()
        expected_migrations = [i for i in range(current_version + 1, unused_migrations[-1] + 1)]
        if len(expected_migrations) != len(unused_migrations):
            raise MigrationError(
                "Found missing migration versions: "
                f"{', '.join(sorted(map(str, set(expected_migrations) - set(unused_migrations))))}."
            )

        for version in unused_migrations:
            filepath = Path(workdir, migrations_dir, f"{str(version).rjust(3, '0')}.sql")
            logger.info(f"Executing migration {filepath}")
            await connection.execute(_read_migration(filepath))
            current_version += 1
            await connection.execute("UPDATE _migration SET version = $1;", current_version)

    logger.info("All migrations are active")
