import asyncio
from pathlib import Path

from core.database import db


async def main():
    schema_path = Path(__file__).with_name("schema.sql")
    schema = schema_path.read_text()

    try:
        await db.connect()

        async with db.pool.acquire() as connection:
            await connection.execute(schema)

        print("✅ Angel database schema installed successfully.")

    except Exception as e:
        print(f"❌ Database schema installation failed:")
        print(f"{type(e).__name__}: {e}")

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
