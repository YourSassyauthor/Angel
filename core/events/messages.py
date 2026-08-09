import discord

from systems.security import analyze_message


async def handle_message(message: discord.Message):
    if message.author.bot:
        return

    if not message.guild:
        return

    result = await analyze_message(message)

    if result["spam"]:
        print(
            f"🚨 Spam signal: "
            f"{message.author} in {message.guild.name} "
            f"({result['messages_last_5_seconds']} messages/5s)"
        )

    if result["blacklist_matches"]:
        matches = ", ".join(
            match["word"]
            for match in result["blacklist_matches"]
        )

        print(
            f"🚫 Blacklist signal: "
            f"{message.author} in {message.guild.name} "
            f"→ {matches}"
        )
