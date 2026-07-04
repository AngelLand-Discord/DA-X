from functools import wraps

import requests
from flask import session, redirect, url_for
from werkzeug.exceptions import Forbidden, NotFound

from .config import (
    OWNER_FEATURES,
    STAFF_FEATURES,
    MEMBER_FEATURES,
)

from .database import (
    get_db,
)

from .utils import (
    current_user_id,
    discord_get,
)


def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if (
            "user" not in session
            or
            "token" not in session
        ):
            return redirect(
                url_for("login")
            )

        return func(*args, **kwargs)

    return wrapper


def is_staff(
    guild_id,
    user_id,
):

    db = get_db()

    row = db.execute(
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
    ).fetchone()

    db.close()

    return row is not None


def get_user_guild(guild_id):

    try:

        guilds = discord_get(
            "/users/@me/guilds",
            session["token"],
        )

    except requests.RequestException:

        session.clear()

        raise Forbidden(
            "Session expired."
        )

    for guild in guilds:

        if str(guild["id"]) == str(guild_id):

            return guild

    raise NotFound(
        "Guild not found."
    )


def access_level(guild_id):

    guild = get_user_guild(
        guild_id
    )

    if guild.get("owner"):

        return "OWNER", guild

    if is_staff(
        guild_id,
        current_user_id(),
    ):

        return "STAFF", guild

    return "MEMBER", guild


def require_feature(feature):

    def decorator(func):

        @wraps(func)
        def wrapper(
            guild_id,
            *args,
            **kwargs,
        ):

            level, guild = access_level(
                guild_id
            )

            allowed = {

                "OWNER": OWNER_FEATURES,

                "STAFF": STAFF_FEATURES,

                "MEMBER": MEMBER_FEATURES,

            }[level]

            if feature not in allowed:

                raise Forbidden(
                    "Access denied."
                )

            return func(
                guild_id,
                level,
                guild,
                *args,
                **kwargs,
            )

        return login_required(
            wrapper
        )

    return decorator
