import os
import asyncio

import discord
from dotenv import load_dotenv

load_dotenv()


class GuildLister(discord.Client):
    def __init__(self):
        intents = discord.Intents.none()
        intents.guilds = True
        super().__init__(intents=intents)

    async def on_ready(self):
        print("\n😇 Angel is connected to:\n")

        for guild in self.guilds:
            print(f"📌 {guild.name}")
            print(f"   ID: {guild.id}")
            print(f"   Members: {guild.member_count}")
            print(f"   Invite: https://discord.gg/{guild.vanity_url_code}"
                  if guild.vanity_url_code else
                  "   Invite: No vanity URL")

        await self.close()


async def main():
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        raise RuntimeError("DISCORD_TOKEN is missing from .env")

    client = GuildLister()
    await client.start(token)


if __name__ == "__main__":
    asyncio.run(main())
