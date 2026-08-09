import discord

from core.repository import ensure_guild, ensure_member


async def handle_member_join(member: discord.Member):
    try:
        await ensure_guild(member.guild)
        await ensure_member(member.guild.id, member)

        print(
            f"👤 Member joined: "
            f"{member} → {member.guild.name}"
        )

    except Exception as e:
        print(
            f"❌ Failed to process member join "
            f"{member}: {type(e).__name__}: {e}"
        )
