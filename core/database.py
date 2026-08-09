import os

import asyncpg
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise RuntimeError("DATABASE_URL is missing from .env")

        self.pool = await asyncpg.create_pool(
            dsn=database_url,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )

        print("🗄️  PostgreSQL connection pool created.")

    async def close(self):
        if self.pool:
            await self.pool.close()
            self.pool = None
            print("🗄️  PostgreSQL connection pool closed.")

    async def execute(self, query: str, *args):
        if not self.pool:
            raise RuntimeError("Database pool is not connected.")

        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args):
        if not self.pool:
            raise RuntimeError("Database pool is not connected.")

        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        if not self.pool:
            raise RuntimeError("Database pool is not connected.")

        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        if not self.pool:
            raise RuntimeError("Database pool is not connected.")

        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)


db = Database()
