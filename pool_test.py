import asyncio

from core.database import db


async def main():
    try:
        await db.connect()

        result = await db.fetchval("SELECT 1")

        if result == 1:
            print("✅ Database pool test successful!")

    except Exception as e:
        print(f"❌ Database pool test failed:")
        print(f"{type(e).__name__}: {e}")

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())

