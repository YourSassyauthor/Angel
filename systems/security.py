import re
import time
from collections import defaultdict, deque

import discord

from core.repository import (
    get_blacklisted_words,
    update_reputation,
)


_message_history: dict[int, deque[float]] = defaultdict(
    lambda: deque(maxlen=20)
)


def normalize_text(text: str) -> str:
    """
    Normalize message text for blacklist detection.
    """
    text = text.lower()

    # Replace punctuation with spaces.
    text = re.sub(r"[^\w\s]", " ", text)

    # Collapse repeated whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text


def contains_blacklisted_word(
    text: str,
    word: str,
) -> bool:
    """
    Match a blacklist entry as a whole word/phrase.
    """

    normalized_text = normalize_text(text)
    normalized_word = normalize_text(word)

    if not normalized_word:
        return False

    pattern = rf"(?<!\w){re.escape(normalized_word)}(?!\w)"

    return re.search(
        pattern,
        normalized_text,
        flags=re.IGNORECASE,
    ) is not None


async def check_blacklist(
    message: discord.Message,
) -> list[dict]:
    """
    Return all blacklist matches found in a message.
    """

    words = await get_blacklisted_words(
        message.guild.id
    )

    matches = []

    for row in words:
        if contains_blacklisted_word(
            message.content,
            row["word"],
        ):
            matches.append(
                {
                    "word": row["word"],
                    "severity": row["severity"],
                }
            )

    return matches


async def analyze_message(
    message: discord.Message,
) -> dict:

    if message.author.bot or not message.guild:
        return {
            "ignored": True,
            "spam": False,
            "blacklist_matches": [],
        }

    now = time.monotonic()

    history = _message_history[message.author.id]

    history.append(now)

    recent = [
        timestamp
        for timestamp in history
        if now - timestamp <= 5
    ]

    spam = len(recent) >= 6

    blacklist_matches = await check_blacklist(message)

    if spam:
        await update_reputation(
            message.guild.id,
            message.author.id,
            trust_change=-2,
            goodwill_change=-2,
        )

    elif len(recent) == 1:
        await update_reputation(
            message.guild.id,
            message.author.id,
            trust_change=0,
            goodwill_change=1,
        )

    if blacklist_matches:
        highest_severity = max(
            match["severity"]
            for match in blacklist_matches
        )

        trust_penalty = highest_severity * 2
        goodwill_penalty = highest_severity * 3

        await update_reputation(
            message.guild.id,
            message.author.id,
            trust_change=-trust_penalty,
            goodwill_change=-goodwill_penalty,
        )

    return {
        "ignored": False,
        "spam": spam,
        "messages_last_5_seconds": len(recent),
        "blacklist_matches": blacklist_matches,
    }
