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

CLIENT_ID = os.getenv(
    "DISCORD_CLIENT_ID"
)

CLIENT_SECRET = os.getenv(
    "DISCORD_CLIENT_SECRET"
)

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
    template_folder=str(
        BASE_DIR / "templates"
    )
)

app.secret_key = SECRET_KEY

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
    CREATE TABLE IF NOT EXISTS guild_permissions (
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL,
        added_by TEXT NOT NULL,
        PRIMARY KEY (
            guild_id,
            user_id
        )
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        suggestion TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS appeals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        appeal TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        name TEXT NOT NULL,
        age TEXT NOT NULL,
        timezone TEXT NOT NULL,
        experience TEXT NOT NULL,
        reason TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_at TEXT NOT NULL
    )
    """)

    db.commit()
    db.close()


initialize_dashboard_tables()

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

        return func(
            *args,
            **kwargs
        )

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


def is_owner(guild):

    return guild.get(
        "owner",
        False
    )


def is_staff(
    guild_id,
    user_id
):

    db = get_db()
    cur = db.cursor()

    cur.execute(
        """
        SELECT *
        FROM guild_permissions
        WHERE guild_id=?
        AND user_id=?
        """,
        (
            str(guild_id),
            str(user_id)
        )
    )

    result = cur.fetchone()

    db.close()

    return result is not None
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

    if is_owner(selected):

        return render_template(
            "owner_dashboard.html",
            guild_id=guild_id,
            guild_name=selected["name"]
        )

    if is_staff(
        guild_id,
        session["user"]["id"]
    ):

        return render_template(
            "staff_dashboard.html",
            guild_id=guild_id,
            guild_name=selected["name"]
        )

    return render_template(
        "member_dashboard.html",
        guild_id=guild_id,
        guild_name=selected["name"]
    )


# =========================
# STAFF ACCESS
# =========================

@app.route(
    "/guild/<guild_id>/staff-access",
    methods=["GET", "POST"]
)
@login_required
def staff_access(guild_id):

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

    if not is_owner(selected):

        return (
            "Access denied",
            403
        )

    db = get_db()
    cur = db.cursor()

    if request.method == "POST":

        user_id = request.form.get(
            "user_id"
        )

        if user_id:

            cur.execute(
                """
                INSERT OR REPLACE INTO
                guild_permissions
                (
                    guild_id,
                    user_id,
                    role,
                    added_by
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    guild_id,
                    user_id,
                    "staff",
                    session["user"]["id"]
                )
            )

            db.commit()

            db.close()

            return redirect(
                url_for(
                    "staff_access",
                    guild_id=guild_id
                )
            )

    cur.execute(
        """
        SELECT *
        FROM guild_permissions
        WHERE guild_id=?
        """,
        (guild_id,)
    )

    staff_users = cur.fetchall()

    db.close()

    return render_template(
        "staff_access.html",
        guild_id=guild_id,
        staff_users=staff_users
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

            db.close()

            return redirect(
                url_for(
                    "suggestions",
                    guild_id=guild_id
                )
            )

    cur.execute(
        """
        SELECT *
        FROM suggestions
        WHERE guild_id=?
        ORDER BY id DESC
        """,
        (guild_id,)
    )

    suggestions_list = cur.fetchall()

    db.close()

    return render_template(
        "suggestions.html",
        guild_id=guild_id,
        suggestions=suggestions_list
    )


# =========================
# APPEALS
# =========================

@app.route(
    "/guild/<guild_id>/appeals",
    methods=["GET", "POST"]
)
@login_required
def appeals(guild_id):

    db = get_db()
    cur = db.cursor()

    if request.method == "POST":

        appeal = request.form.get(
            "appeal"
        )

        if appeal:

            cur.execute(
                """
                INSERT INTO appeals
                (
                    guild_id,
                    user_id,
                    username,
                    appeal,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    guild_id,
                    session["user"]["id"],
                    session["user"]["username"],
                    appeal,
                    datetime.utcnow().isoformat()
                )
            )

            db.commit()

            db.close()

            return redirect(
                url_for(
                    "appeals",
                    guild_id=guild_id
                )
            )

    cur.execute(
        """
        SELECT *
        FROM appeals
        WHERE guild_id=?
        ORDER BY id DESC
        """,
        (guild_id,)
    )

    appeals_list = cur.fetchall()

    db.close()

    return render_template(
        "appeals.html",
        guild_id=guild_id,
        appeals=appeals_list
    )


# =========================
# APPLICATIONS
# =========================

@app.route(
    "/guild/<guild_id>/applications",
    methods=["GET", "POST"]
)
@login_required
def applications(guild_id):

    db = get_db()
    cur = db.cursor()

    if request.method == "POST":

        name = request.form.get("name")
        age = request.form.get("age")
        timezone_name = request.form.get("timezone")
        experience = request.form.get("experience")
        reason = request.form.get("reason")

        if all([
            name,
            age,
            timezone_name,
            experience,
            reason
        ]):

            cur.execute(
                """
                INSERT INTO applications
                (
                    guild_id,
                    user_id,
                    username,
                    name,
                    age,
                    timezone,
                    experience,
                    reason,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    guild_id,
                    session["user"]["id"],
                    session["user"]["username"],
                    name,
                    age,
                    timezone_name,
                    experience,
                    reason,
                    datetime.utcnow().isoformat()
                )
            )

            db.commit()

            db.close()

            return redirect(
                url_for(
                    "applications",
                    guild_id=guild_id
                )
            )

    cur.execute(
        """
        SELECT *
        FROM applications
        WHERE guild_id=?
        ORDER BY id DESC
        """,
        (guild_id,)
    )

    applications_list = cur.fetchall()

    db.close()

    return render_template(
        "applications.html",
        guild_id=guild_id,
        applications=applications_list
    )


# =========================
# APPLICATION STATUS
# =========================

@app.route(
    "/application/<int:application_id>/<status>"
)
@login_required
def application_status(
    application_id,
    status
):

    allowed = [
        "Accepted",
        "Rejected",
        "Pending"
    ]

    if status not in allowed:

        return (
            "Invalid status",
            400
        )

    db = get_db()
    cur = db.cursor()

    cur.execute(
        """
        UPDATE applications
        SET status=?
        WHERE id=?
        """,
        (
            status,
            application_id
        )
    )

    db.commit()

    db.close()

    return redirect(
        request.referrer or
        url_for("dashboard")
    )


# =========================
# APPEAL STATUS
# =========================

@app.route(
    "/appeal/<int:appeal_id>/<status>"
)
@login_required
def appeal_status(
    appeal_id,
    status
):

    allowed = [
        "Accepted",
        "Rejected",
        "Pending"
    ]

    if status not in allowed:

        return (
            "Invalid status",
            400
        )

    db = get_db()
    cur = db.cursor()

    cur.execute(
        """
        UPDATE appeals
        SET status=?
        WHERE id=?
        """,
        (
            status,
            appeal_id
        )
    )

    db.commit()

    db.close()

    return redirect(
        request.referrer or
        url_for("dashboard")
    )


# =========================
# SUGGESTION STATUS
# =========================

@app.route(
    "/suggestion/<int:suggestion_id>/<status>"
)
@login_required
def suggestion_status(
    suggestion_id,
    status
):

    allowed = [
        "Approved",
        "Rejected",
        "Implemented",
        "Pending"
    ]

    if status not in allowed:

        return (
            "Invalid status",
            400
        )

    db = get_db()
    cur = db.cursor()

    cur.execute(
        """
        UPDATE suggestions
        SET status=?
        WHERE id=?
        """,
        (
            status,
            suggestion_id
        )
    )

    db.commit()

    db.close()

    return redirect(
        request.referrer or
        url_for("dashboard")
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
