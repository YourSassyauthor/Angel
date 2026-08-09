import discord

from core.repository import ensure_guild


async def handle_guild_available(guild: discord.Guild):
    try:
        await ensure_guild(guild)

        print(
            f"🏠 Guild available: "
            f"{guild.name} ({guild.id})"
        )

    except Exception as e:
        print(
            f"❌ Failed to process guild "
            f"{guild.name}: {type(e).__name__}: {e}"
        )

