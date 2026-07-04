import requests

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .config import (
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    DISCORD_API,
)

from .utils import discord_get


auth_bp = Blueprint(
    "auth",
    __name__,
)


@auth_bp.route("/login")
def login():

    if not CLIENT_ID or not REDIRECT_URI:

        return render_template(
            "error.html",
            title="OAuth not configured",
            message="Discord OAuth environment variables are missing.",
        ), 500

    return redirect(

        "https://discord.com/oauth2/authorize"

        f"?client_id={CLIENT_ID}"

        "&response_type=code"

        f"&redirect_uri={requests.utils.quote(REDIRECT_URI, safe='')}"

        "&scope=identify%20guilds"

    )


@auth_bp.route("/callback")
def callback():

    code = request.args.get("code")

    if not code:

        return render_template(
            "error.html",
            title="OAuth Failed",
            message="Discord did not return an authorization code.",
        ), 400

    try:

        token = requests.post(

            f"{DISCORD_API}/oauth2/token",

            data={

                "client_id": CLIENT_ID,

                "client_secret": CLIENT_SECRET,

                "grant_type": "authorization_code",

                "code": code,

                "redirect_uri": REDIRECT_URI,

            },

            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },

            timeout=15,

        )

        token.raise_for_status()

        token_json = token.json()

        access_token = token_json["access_token"]

        user = discord_get(
            "/users/@me",
            access_token,
        )

    except Exception:

        return render_template(

            "error.html",

            title="OAuth Failed",

            message="Unable to complete Discord login.",

        ), 400

    session.permanent = True

    session["token"] = access_token

    session["user"] = {

        "id": str(user["id"]),

        "username": user.get("username", "Discord User"),

        "avatar": user.get("avatar"),

        "access_token": access_token,

    }

    return redirect(
        url_for("dashboard")
    )


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )
