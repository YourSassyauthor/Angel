import asyncio

from core.database import db


async def main():
    try:
        await db.connect()

        rows = await db.fetch(
            """
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'members'
            ORDER BY ordinal_position;
            """
        )

        print("👤 members table columns:\n")

        for row in rows:
            print(
                f"  • {row['column_name']} "
                f"({row['data_type']}) "
                f"nullable={row['is_nullable']}"
            )

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
