import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from core.database import db
from core.repository import ensure_guild, ensure_members
from core.events.guilds import handle_guild_available
from core.events.members import handle_member_join
from core.events.messages import handle_message


load_dotenv()


class Angel(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        print("⚙️  Starting Angel...")

        await db.connect()

        print("🗄️  Database ready.")

        try:
            synced = await self.tree.sync()
            print(f"🔄 Synced {len(synced)} slash command(s).")
        except Exception as e:
            print(f"⚠️  Slash command sync failed: {e}")

    async def on_ready(self):
        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"😇 Angel online as {self.user}")
        print(f"🆔 User ID: {self.user.id}")
        print(f"🌐 Connected to {len(self.guilds)} server(s)")
        print("🗄️  PostgreSQL: ONLINE")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        for guild in self.guilds:
            try:
                await ensure_guild(guild)
                await ensure_members(guild.id, list(guild.members))

                print(f"✅ Database synced: {guild.name}")

            except Exception as e:
                print(
                    f"❌ Failed to sync {guild.name}: "
                    f"{type(e).__name__}: {e}"
                )

        print()

    async def on_guild_available(self, guild: discord.Guild):
        await handle_guild_available(guild)

    async def on_member_join(self, member: discord.Member):
        await handle_member_join(member)

    async def on_message(self, message: discord.Message):
        await handle_message(message)

        await self.process_commands(message)

    async def close(self):
        print("🛑 Shutting down Angel...")

        await db.close()

        await super().close()

        print("👋 Angel shut down cleanly.")


async def main():
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        raise RuntimeError("DISCORD_TOKEN is missing from .env")

    bot = Angel()

    try:
        await bot.start(token)
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
