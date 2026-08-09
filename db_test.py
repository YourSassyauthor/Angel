import asyncio
import os

import asyncpg
from dotenv import load_dotenv

load_dotenv()


async def main():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ DATABASE_URL is missing from .env")
        return

    print("🔌 Connecting to PostgreSQL...")

    try:
        conn = await asyncpg.connect(database_url)

        version = await conn.fetchval("SELECT version()")
        print("✅ PostgreSQL connection successful!")
        print(f"📦 {version}")

        await conn.close()
        print("🔒 Connection closed.")

    except Exception as e:
        print(f"❌ PostgreSQL connection failed:")
        print(f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
