from typing import Optional

import asyncpg
import discord

from core.database import db


async def ensure_guild(guild: discord.Guild):
    await db.execute(
        """
        INSERT INTO guilds (guild_id, name)
        VALUES ($1, $2)
        ON CONFLICT (guild_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            updated_at = NOW();
        """,
        guild.id,
        guild.name,
    )

    await db.execute(
        """
        INSERT INTO guild_settings (guild_id)
        VALUES ($1)
        ON CONFLICT (guild_id) DO NOTHING;
        """,
        guild.id,
    )


async def ensure_member(
    guild_id: int,
    member: discord.Member,
):
    await db.execute(
        """
        INSERT INTO members (
            guild_id,
            user_id,
            username,
            display_name
        )
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (guild_id, user_id)
        DO UPDATE SET
            username = EXCLUDED.username,
            display_name = EXCLUDED.display_name,
            last_seen_at = NOW();
        """,
        guild_id,
        member.id,
        str(member),
        member.display_name,
    )


async def ensure_members(
    guild_id: int,
    members: list[discord.Member],
):
    if not members:
        return

    user_ids = []
    usernames = []
    display_names = []

    for member in members:
        if member.bot:
            continue

        user_ids.append(member.id)
        usernames.append(str(member))
        display_names.append(member.display_name)

    if not user_ids:
        return

    await db.execute(
        """
        INSERT INTO members (
            guild_id,
            user_id,
            username,
            display_name
        )
        SELECT
            $1,
            data.user_id,
            data.username,
            data.display_name
        FROM UNNEST(
            $2::BIGINT[],
            $3::TEXT[],
            $4::TEXT[]
        ) AS data(
            user_id,
            username,
            display_name
        )
        ON CONFLICT (guild_id, user_id)
        DO UPDATE SET
            username = EXCLUDED.username,
            display_name = EXCLUDED.display_name,
            last_seen_at = NOW();
        """,
        guild_id,
        user_ids,
        usernames,
        display_names,
    )


async def get_member(
    guild_id: int,
    user_id: int,
) -> Optional[asyncpg.Record]:
    return await db.fetchrow(
        """
        SELECT *
        FROM members
        WHERE guild_id = $1
          AND user_id = $2;
        """,
        guild_id,
        user_id,
    )


async def update_reputation(
    guild_id: int,
    user_id: int,
    trust_change: int = 0,
    goodwill_change: int = 0,
):
    return await db.fetchrow(
        """
        UPDATE members
        SET
            trust_score = GREATEST(
                0,
                LEAST(100, trust_score + $3)
            ),
            goodwill_score = GREATEST(
                0,
                LEAST(100, goodwill_score + $4)
            ),
            last_seen_at = NOW()
        WHERE guild_id = $1
          AND user_id = $2
        RETURNING
            trust_score,
            goodwill_score;
        """,
        guild_id,
        user_id,
        trust_change,
        goodwill_change,
    )


async def add_warning(
    guild_id: int,
    user_id: int,
):
    return await db.fetchrow(
        """
        UPDATE members
        SET
            warnings = warnings + 1,
            trust_score = GREATEST(0, trust_score - 5),
            goodwill_score = GREATEST(0, goodwill_score - 3),
            last_seen_at = NOW()
        WHERE guild_id = $1
          AND user_id = $2
        RETURNING
            warnings,
            trust_score,
            goodwill_score;
        """,
        guild_id,
        user_id,
    )
async def get_blacklisted_words(
    guild_id: int,
) -> list[asyncpg.Record]:
    return await db.fetch(
        """
        SELECT
            word,
            severity
        FROM blacklisted_words
        WHERE guild_id = $1
        ORDER BY severity DESC;
        """,
        guild_id,
    )


async def add_blacklisted_word(
    guild_id: int,
    word: str,
    severity: int = 1,
):
    word = word.strip().lower()

    if not word:
        raise ValueError("Blacklist word cannot be empty.")

    severity = max(1, min(5, severity))

    return await db.fetchrow(
        """
        INSERT INTO blacklisted_words (
            guild_id,
            word,
            severity
        )
        VALUES ($1, $2, $3)
        ON CONFLICT (guild_id, word)
        DO UPDATE SET
            severity = EXCLUDED.severity
        RETURNING
            guild_id,
            word,
            severity;
        """,
        guild_id,
        word,
        severity,
    )


async def remove_blacklisted_word(
    guild_id: int,
    word: str,
):
    return await db.fetchrow(
        """
        DELETE FROM blacklisted_words
        WHERE guild_id = $1
          AND word = $2
        RETURNING
            guild_id,
            word,
            severity;
        """,
        guild_id,
        word.strip().lower(),
    )
