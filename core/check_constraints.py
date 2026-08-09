import asyncio

from core.database import db


async def main():
    try:
        await db.connect()

        rows = await db.fetch(
            """
            SELECT
                conname,
                pg_get_constraintdef(oid) AS definition
            FROM pg_constraint
            WHERE conrelid = 'blacklisted_words'::regclass;
            """
        )

        print("🔐 blacklisted_words constraints:\n")

        if not rows:
            print("  • No constraints found.")
        else:
            for row in rows:
                print(
                    f"  • {row['conname']}: "
                    f"{row['definition']}"
                )

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
