import requests

from flask import session

from .config import DISCORD_API
from .utils import discord_get


def get_bot_guilds():

    """
    Returns a set containing every guild
    the bot is currently in.
    """

    bot_token = session.get("bot_token")

    if not bot_token:
        return set()

    try:

        response = requests.get(

            f"{DISCORD_API}/users/@me/guilds",

            headers={
                "Authorization": f"Bot {bot_token}"
            },

            timeout=15,

        )

        response.raise_for_status()

        guilds = response.json()

        return {
            str(guild["id"])
            for guild in guilds
        }

    except Exception:

        return set()


def get_dashboard_guilds():

    """
    Returns only guilds where BOTH
    the user and the bot are present.
    """

    user_guilds = discord_get(

        "/users/@me/guilds",

        session["token"]

    )

    bot_guilds = get_bot_guilds()

    visible = []

    for guild in user_guilds:

        if guild["id"] in bot_guilds:

            visible.append(guild)

    return visible
