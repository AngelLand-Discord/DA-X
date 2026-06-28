from functools import wraps

import requests
from flask import session, redirect, url_for
from werkzeug.exceptions import Forbidden, NotFound

from dashboard.config import DISCORD_API
from dashboard.database import fetch_one

OWNER_FEATURES = {
    "staff_access",
    "settings",
    "logs",
    "moderation",
    "suggestions",
    "appeals",
    "applications",
    "tickets",
    "automod",
    "announcements",
    "developer",
}

STAFF_FEATURES = {
    "logs",
    "moderation",
    "suggestions",
    "appeals",
    "applications",
    "tickets",
    "automod",
}

MEMBER_FEATURES = {
    "suggestions",
    "appeals",
    "applications",
    "tickets",
}


def current_user_id():
    return str(session["user"]["id"])


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user" not in session:
            return redirect(url_for("login"))

        if "token" not in session:
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


def discord_get(path, token):

    response = requests.get(
        f"{DISCORD_API}{path}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=15
    )

    response.raise_for_status()

    return response.json()


def get_user_guild(guild_id):

    try:

        guilds = discord_get(
            "/users/@me/guilds",
            session["token"]
        )

    except requests.RequestException:

        raise Forbidden(
            "Discord session expired. Please login again."
        )

    for guild in guilds:

        if str(guild["id"]) == str(guild_id):
            return guild

    raise NotFound("Guild not found.")


def is_staff(guild_id, user_id):

    row = fetch_one(
        """
        SELECT 1
        FROM guild_permissions
        WHERE guild_id=?
        AND user_id=?
        """,
        (
            str(guild_id),
            str(user_id),
        ),
    )

    return row is not None


def access_level(guild_id):

    guild = get_user_guild(guild_id)

    if guild.get("owner"):
        return "OWNER", guild

    if is_staff(
        guild_id,
        current_user_id()
    ):
        return "STAFF", guild

    return "MEMBER", guild


def require_feature(feature):

    def decorator(func):

        @wraps(func)
        def wrapper(guild_id, *args, **kwargs):

            level, guild = access_level(guild_id)

            allowed = {

                "OWNER": OWNER_FEATURES,

                "STAFF": STAFF_FEATURES,

                "MEMBER": MEMBER_FEATURES,

            }[level]

            if feature not in allowed:

                raise Forbidden(
                    "You do not have permission to access this page."
                )

            return func(
                guild_id,
                level,
                guild,
                *args,
                **kwargs
            )

        return login_required(wrapper)

    return decorator
