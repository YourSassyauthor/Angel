import asyncio

from core.database import db


async def main():
    try:
        await db.connect()

        guild_count = await db.fetchval(
            "SELECT COUNT(*) FROM guilds;"
        )

        member_count = await db.fetchval(
            "SELECT COUNT(*) FROM members;"
        )

        print(f"🏠 Guilds stored: {guild_count}")
        print(f"👤 Members stored: {member_count}")

        print("\n📊 Guild member counts:")

        rows = await db.fetch(
            """
            SELECT
                g.name,
                COUNT(m.user_id) AS members
            FROM guilds g
            LEFT JOIN members m
                ON g.guild_id = m.guild_id
            GROUP BY g.guild_id, g.name
            ORDER BY members DESC;
            """
        )

        for row in rows:
            print(f"  • {row['name']}: {row['members']}")

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
