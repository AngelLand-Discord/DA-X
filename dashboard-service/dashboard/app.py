import os
from functools import wraps

import requests

from flask import (
    Flask,
    redirect,
    request,
    session,
    url_for,
    render_template
)
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# =========================
# CONFIG
# =========================

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")

REDIRECT_URI = os.getenv(
    "DISCORD_REDIRECT_URI"
)

SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY",
    "change-me"
)

DISCORD_API = "https://discord.com/api"

# =========================
# APP
# =========================

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates")
)

app.secret_key = SECRET_KEY

# =========================
# HELPERS
# =========================

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user" not in session:

            return redirect(
                url_for("login")
            )

        return func(*args, **kwargs)

    return wrapper


def get_discord_user(token):

    r = requests.get(
        f"{DISCORD_API}/users/@me",
        headers={
            "Authorization":
            f"Bearer {token}"
        }
    )

    return r.json()


def get_user_guilds(token):

    r = requests.get(
        f"{DISCORD_API}/users/@me/guilds",
        headers={
            "Authorization":
            f"Bearer {token}"
        }
    )

    return r.json()


# =========================
# ROUTES
# =========================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


@app.route("/login")
def login():

    scope = (
        "identify guilds"
    )

    return redirect(
        "https://discord.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scope}"
    )


@app.route("/callback")
def callback():

    code = request.args.get(
        "code"
    )

    data = {

        "client_id":
        CLIENT_ID,

        "client_secret":
        CLIENT_SECRET,

        "grant_type":
        "authorization_code",

        "code":
        code,

        "redirect_uri":
        REDIRECT_URI

    }

    headers = {
        "Content-Type":
        "application/x-www-form-urlencoded"
    }

    token_response = requests.post(
        f"{DISCORD_API}/oauth2/token",
        data=data,
        headers=headers
    )

    token_json = token_response.json()

    access_token = token_json.get(
        "access_token"
    )

    if not access_token:

        return (
            "OAuth failed.",
            400
        )

    user = get_discord_user(
        access_token
    )

    session["token"] = access_token

    session["user"] = {

        "id":
        user["id"],

        "username":
        user["username"],

        "avatar":
        user.get("avatar")

    }

    return redirect(
        url_for(
            "dashboard"
        )
    )


@app.route("/dashboard")
@login_required
def dashboard():

    guilds = get_user_guilds(
        session["token"]
    )

    return render_template(
        "dashboard.html",
        user=session["user"],
        guilds=guilds
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        "/"
    )
@app.route("/guild/<guild_id>")
@login_required
def guild_dashboard(guild_id):

    guilds = get_user_guilds(
        session["token"]
    )

    selected = None

    for guild in guilds:

        if guild["id"] == guild_id:

            selected = guild

            break

    if not selected:

        return (
            "Guild not found",
            404
        )

    return render_template(
        "guild.html",
        guild_name=selected["name"],
        guild_id=guild_id
    )

# =========================
# START
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
