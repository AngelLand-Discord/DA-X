import os
import sqlite3

from functools import wraps
from pathlib import Path
from datetime import datetime

import requests

from flask import (
    Flask,
    redirect,
    request,
    session,
    url_for,
    render_template
)

# =========================
# PATHS
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    BASE_DIR.parent /
    "bot-service" /
    "bot.db"
)

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

initialize_dashboard_tables()

# =========================
# DATABASE
# =========================

def get_db():

    db = sqlite3.connect(
        DATABASE_PATH
    )

    db.row_factory = sqlite3.Row

    return db

def initialize_dashboard_tables():

    db = get_db()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        suggestion TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_at TEXT NOT NULL
    )
    """)

    db.commit()
    db.close()
    
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

    return redirect("/")

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
# SUGGESTIONS
# =========================

@app.route(
    "/guild/<guild_id>/suggestions",
    methods=["GET", "POST"]
)
@login_required
def suggestions(guild_id):

    db = get_db()
    cur = db.cursor()

    if request.method == "POST":

        suggestion = request.form.get(
            "suggestion"
        )

        if suggestion:

            cur.execute(
                """
                INSERT INTO suggestions
                (
                    guild_id,
                    user_id,
                    username,
                    suggestion,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    guild_id,
                    session["user"]["id"],
                    session["user"]["username"],
                    suggestion,
                    datetime.utcnow().isoformat()
                )
            )

            db.commit()

    cur.execute(
        """
        SELECT *
        FROM suggestions
        WHERE guild_id=?
        ORDER BY id DESC
        """,
        (guild_id,)
    )

    suggestions = cur.fetchall()

    db.close()

    return render_template(
        "suggestions.html",
        guild_id=guild_id,
        suggestions=suggestions
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
