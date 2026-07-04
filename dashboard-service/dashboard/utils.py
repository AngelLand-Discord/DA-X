import re
import requests

from datetime import datetime, timezone
from flask import session, redirect, url_for

from config import (
    DISCORD_API,
    VALID_ID,
)


def utc_now():

    return datetime.now(
        timezone.utc
    ).isoformat()


def clean_text(
    value,
    max_length=4000,
):

    value = (value or "").strip()

    return value[:max_length]


def valid_discord_id(value):

    return bool(
        value
        and VALID_ID.match(
            str(value)
        )
    )


def current_user_id():

    return str(
        session["user"]["id"]
    )


def discord_get(
    path,
    token,
):

    response = requests.get(

        f"{DISCORD_API}{path}",

        headers={
            "Authorization": f"Bearer {token}"
        },

        timeout=15,

    )

    response.raise_for_status()

    return response.json()


def require_login():

    if (
        "user" not in session
        or
        "token" not in session
    ):

        return redirect(
            url_for("login")
        )

    return None
