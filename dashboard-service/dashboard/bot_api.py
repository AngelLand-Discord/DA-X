from .database import fetchall
from .utils import discord_get

from flask import session


def get_bot_guilds():
    """
    Returns every guild the bot is currently in,
    read directly from SQLite.
    """

    rows = fetchall(
        """
        SELECT
            guild_id,
            guild_name,
            icon,
            owner_id,
            member_count
        FROM bot_guilds
        """
    )

    return {
        row["guild_id"]: row
        for row in rows
    }


def get_dashboard_guilds():
    """
    Returns only guilds that BOTH
    the logged-in user and the bot share.
    """

    user_guilds = discord_get(
        "/users/@me/guilds",
        session["token"],
    )

    bot_guilds = get_bot_guilds()

    visible = []

    for guild in user_guilds:

        guild_id = str(guild["id"])

        if guild_id not in bot_guilds:
            continue

        bot = bot_guilds[guild_id]

        guild["member_count"] = bot["member_count"]

        guild["owner_id"] = bot["owner_id"]

        guild["icon"] = bot["icon"]

        visible.append(guild)

    visible.sort(
        key=lambda g: g["name"].lower()
    )

    return visible