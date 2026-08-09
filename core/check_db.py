import asyncio

from core.database import db


async def main():
    try:
        await db.connect()

        rows = await db.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        print("📋 Angel tables:")

        for row in rows:
            print(f"  • {row['table_name']}")

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
