import os
import re
import sqlite3
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.exceptions import Forbidden, NotFound

from datetime import timedelta
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.secret_key = SECRET_KEY
app.permanent_session_lifetime = timedelta(days=30)

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR.parent / "bot-service" / "bot.db"

load_dotenv(BASE_DIR / ".env")

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "")
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-me")
DISCORD_API = "https://discord.com/api"
VALID_ID = re.compile(r"^\d{1,25}$")

OWNER_FEATURES = {
    "staff_access", "settings", "logs", "moderation", "suggestions",
    "appeals", "applications", "tickets", "automod", "announcements",
}
STAFF_FEATURES = {
    "logs", "moderation", "suggestions", "appeals", "applications", "tickets",
}
MEMBER_FEATURES = {"suggestions", "appeals", "applications", "tickets"}

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))
app.secret_key = SECRET_KEY

from datetime import timedelta

app.permanent_session_lifetime = timedelta(days=30)

def get_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db


def column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return any(row["name"] == column for row in cur.fetchall())


def table_has_column(db, table, column):
    cur = db.cursor()
    return column_exists(cur, table, column)


def initialize_database():
    db = get_db()
    cur = db.cursor()
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS guild_permissions (
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'staff',
        added_by TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (guild_id, user_id)
    );

    CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        suggestion TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS appeals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        appeal_type TEXT NOT NULL DEFAULT 'Ban Appeal',
        appeal TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        name TEXT NOT NULL DEFAULT '',
        age TEXT NOT NULL DEFAULT '',
        timezone TEXT NOT NULL DEFAULT '',
        experience TEXT NOT NULL DEFAULT '',
        reason TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        subject TEXT NOT NULL DEFAULT 'Support Ticket',
        status TEXT NOT NULL DEFAULT 'Open',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ticket_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER NOT NULL,
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(ticket_id) REFERENCES tickets(id)
    );

    CREATE TABLE IF NOT EXISTS modlogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL DEFAULT '',
        action TEXT NOT NULL,
        target TEXT NOT NULL,
        moderator TEXT NOT NULL,
        reason TEXT,
        timestamp TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS settings (
        guild_id TEXT PRIMARY KEY,
        log_channel TEXT,
        mod_role TEXT,
        announcement_channel TEXT,
        dashboard_enabled INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS warnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        moderator_id TEXT NOT NULL,
        reason TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS automod_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        rule_type TEXT NOT NULL,
        enabled INTEGER NOT NULL DEFAULT 0,
        config TEXT NOT NULL DEFAULT '',
        updated_by TEXT,
        updated_at TEXT NOT NULL,
        UNIQUE(guild_id, rule_type)
    );
    """)

    migrations = {
        "applications": {
            "name": "TEXT NOT NULL DEFAULT ''",
            "age": "TEXT NOT NULL DEFAULT ''",
            "timezone": "TEXT NOT NULL DEFAULT ''",
            "experience": "TEXT NOT NULL DEFAULT ''",
            "reason": "TEXT NOT NULL DEFAULT ''",
        },
        "modlogs": {"guild_id": "TEXT NOT NULL DEFAULT ''"},
        "guild_permissions": {"created_at": "TEXT NOT NULL DEFAULT ''"},
    }
    for table, columns in migrations.items():
        for column, definition in columns.items():
            if not column_exists(cur, table, column):
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    db.commit()
    db.close()


initialize_database()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def clean_text(value, max_length=4000):
    value = (value or "").strip()
    return value[:max_length]


def valid_discord_id(value):
    return bool(value and VALID_ID.match(str(value)))


def discord_get(path, token):
    response = requests.get(
        f"{DISCORD_API}{path}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def current_user_id():
    return str(session["user"]["id"])


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session or "token" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


def get_user_guild(guild_id):
    try:
        guilds = discord_get(
            "/users/@me/guilds",
            session["token"]
        )
    except requests.RequestException:
        session.clear()
        raise Forbidden(
            "Session expired"
        )
    for guild in guilds:
        if str(guild["id"]) == str(guild_id):
            return guild
    raise NotFound(
        "Guild not found"
    )
def is_staff(guild_id, user_id):
    db = get_db()
    row = db.execute(
        "SELECT 1 FROM guild_permissions WHERE guild_id=? AND user_id=?",
        (str(guild_id), str(user_id)),
    ).fetchone()
    db.close()
    return row is not None

def access_level(guild_id):
    guild = get_user_guild(guild_id)
    if guild.get("owner"):
        return "OWNER", guild
    if is_staff(guild_id, current_user_id()):
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
                raise Forbidden("You do not have permission to access this page.")
            return func(guild_id, level, guild, *args, **kwargs)
        return login_required(wrapper)
    return decorator


def fetch_rows(query, params=()):
    db = get_db()
    rows = db.execute(query, params).fetchall()
    db.close()
    return rows


def update_status(table, item_id, status, allowed):
    if status not in allowed:
        raise NotFound("Invalid status.")
    db = get_db()
    row = db.execute(f"SELECT guild_id FROM {table} WHERE id=?", (item_id,)).fetchone()
    if not row:
        db.close()
        raise NotFound("Item not found.")
    level, _guild = access_level(row["guild_id"])
    if level not in {"OWNER", "STAFF"}:
        db.close()
        raise Forbidden("Only staff can update statuses.")
    db.execute(f"UPDATE {table} SET status=? WHERE id=?", (status, item_id))
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("guild_dashboard", guild_id=row["guild_id"]))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    if not CLIENT_ID or not REDIRECT_URI:
        return render_template("error.html", title="OAuth not configured", message="Discord OAuth environment variables are missing."), 500
    return redirect(
        "https://discord.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}&response_type=code"
        f"&redirect_uri={requests.utils.quote(REDIRECT_URI, safe='')}"
        "&scope=identify%20guilds"
    )


@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return render_template(
            "error.html",
            title="OAuth failed",
            message="Discord did not return an authorization code."
        ), 400

    try:
        token_response = requests.post(
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

        token_response.raise_for_status()

        token_json = token_response.json()

        access_token = token_json["access_token"]

        user = discord_get(
            "/users/@me",
            access_token
        )

    except (KeyError, requests.RequestException):

        return render_template(
            "error.html",
            title="OAuth failed",
            message="Unable to complete Discord login."
        ), 400

    session.permanent = True
    session["token"] = access_token

    session["user"] = {
        "id": str(user["id"]),
        "username": user.get("username", "Discord User"),
        "avatar": user.get("avatar"),
        "access_token": access_token,
    }

    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    try:
        guilds = discord_get("/users/@me/guilds", session["token"])
    except requests.RequestException:
        session.clear()
        return render_template("error.html", title="Discord unavailable", message="Please log in again."), 401
    return render_template("dashboard.html", user=session["user"], guilds=guilds)


@app.route("/guild/<guild_id>")
@login_required
def guild_dashboard(guild_id):
    level, guild = access_level(guild_id)
    template = {
        "OWNER": "owner_dashboard.html",
        "STAFF": "staff_dashboard.html",
        "MEMBER": "member_dashboard.html",
    }[level]
    return render_template(template, guild_id=guild_id, guild_name=guild["name"], level=level)


@app.route("/guild/<guild_id>/staff-access", methods=["GET", "POST"])
@require_feature("staff_access")
def staff_access(guild_id, level, guild):

    db = get_db()

    if request.method == "POST":

        action = request.form.get("action", "add")

        user_id = clean_text(
            request.form.get("user_id"),
            25
        )

        if not valid_discord_id(user_id):

            db.close()

            return render_template(
                "error.html",
                title="Invalid user ID",
                message="Enter a valid Discord user ID."
            ), 400

        if action == "remove":

            db.execute(
                """
                DELETE FROM guild_permissions
                WHERE guild_id=? AND user_id=?
                """,
                (
                    guild_id,
                    user_id
                )
            )

        else:
    
            db.execute(
                """
                INSERT OR REPLACE INTO guild_permissions
                (
                    guild_id,
                    user_id,
                    role,
                    added_by,
                    created_at
                )
                VALUES
                (
                    ?, ?, ?, ?, ?
                )
                """,
                (
                    guild_id,
                    user_id,
                    "staff",
                    current_user_id(),
                    utc_now()
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
    
    staff_users = db.execute(
        """
        SELECT *
        FROM guild_permissions
        WHERE guild_id=?
        ORDER BY user_id
        """,
        (guild_id,)
    ).fetchall()

    db.close()

    return render_template(
        "staff_access.html",
        guild_id=guild_id,
        guild_name=guild["name"],
        staff_users=staff_users
    )

@app.route("/guild/<guild_id>/settings", methods=["GET", "POST"])
@require_feature("settings")
def settings(guild_id, level, guild):
    db = get_db()
    if request.method == "POST":
        values = {
            "log_channel": clean_text(request.form.get("log_channel"), 25),
            "mod_role": clean_text(request.form.get("mod_role"), 25),
            "announcement_channel": clean_text(request.form.get("announcement_channel"), 25),
        }
        for value in values.values():
            if value and not valid_discord_id(value):
                db.close()
                return render_template("error.html", title="Invalid setting", message="Channel and role IDs must be numeric Discord IDs."), 400
        db.execute(
            """
            INSERT INTO settings (guild_id, log_channel, mod_role, announcement_channel)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
            log_channel=excluded.log_channel,
            mod_role=excluded.mod_role,
            announcement_channel=excluded.announcement_channel
            """,
            (guild_id, values["log_channel"], values["mod_role"], values["announcement_channel"]),
        )
        db.commit()
    row = db.execute("SELECT * FROM settings WHERE guild_id=?", (guild_id,)).fetchone()
    db.close()
    return render_template("settings.html", guild_id=guild_id, guild_name=guild["name"], settings=row)


@app.route("/guild/<guild_id>/logs")
@require_feature("logs")
def logs(guild_id, level, guild):
    rows = fetch_rows("SELECT * FROM modlogs WHERE guild_id=? ORDER BY id DESC LIMIT 200", (guild_id,))
    return render_template("logs.html", guild_id=guild_id, guild_name=guild["name"], logs=rows)


@app.route("/guild/<guild_id>/moderation", methods=["GET", "POST"])
@require_feature("moderation")
def moderation(guild_id, level, guild):
    db = get_db()
    if request.method == "POST":
        action = clean_text(request.form.get("action"), 20).lower()
        target = clean_text(request.form.get("user_id"), 25)
        reason = clean_text(request.form.get("reason"), 500)
        if action not in {"warn", "kick", "ban", "unban", "timeout", "untimeout", "purge"} or not valid_discord_id(target):
            db.close()
            return render_template("error.html", title="Invalid moderation action", message="Check the action and target user ID."), 400
        if action == "warn":
            db.execute(
                "INSERT INTO warnings (guild_id, user_id, moderator_id, reason, created_at) VALUES (?, ?, ?, ?, ?)",
                (guild_id, target, current_user_id(), reason, utc_now()),
            )
        db.execute(
            "INSERT INTO modlogs (guild_id, action, target, moderator, reason, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (guild_id, action.upper(), target, current_user_id(), reason, utc_now()),
        )
        db.commit()
    rows = db.execute("SELECT * FROM modlogs WHERE guild_id=? ORDER BY id DESC LIMIT 50", (guild_id,)).fetchall()
    db.close()
    return render_template("moderation.html", guild_id=guild_id, guild_name=guild["name"], logs=rows)


@app.route("/guild/<guild_id>/suggestions", methods=["GET", "POST"])
@require_feature("suggestions")
def suggestions(guild_id, level, guild):
    db = get_db()
    if request.method == "POST":
        suggestion = clean_text(request.form.get("suggestion"), 4000)
        if suggestion:
            db.execute(
                "INSERT INTO suggestions (guild_id, user_id, username, suggestion, created_at) VALUES (?, ?, ?, ?, ?)",
                (guild_id, current_user_id(), session["user"]["username"], suggestion, utc_now()),
            )
            db.commit()
    rows = db.execute("SELECT * FROM suggestions WHERE guild_id=? ORDER BY id DESC", (guild_id,)).fetchall()
    db.close()
    return render_template("suggestions.html", guild_id=guild_id, guild_name=guild["name"], suggestions=rows, level=level)


@app.route("/guild/<guild_id>/appeals", methods=["GET", "POST"])
@require_feature("appeals")
def appeals(guild_id, level, guild):
    db = get_db()

    if request.method == "POST":

        appeal_type = clean_text(
            request.form.get(
                "appeal_type",
                "Ban Appeal"
            ),
            100
        )

        appeal = clean_text(
            request.form.get(
                "appeal"
            ),
            4000
        )

        if appeal:

            db.execute(
                """
                INSERT INTO appeals
                (
                    guild_id,
                    user_id,
                    username,
                    appeal_type,
                    appeal,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    guild_id,
                    current_user_id(),
                    session["user"]["username"],
                    appeal_type,
                    appeal,
                    utc_now()
                )
            )

            db.commit()

    rows = db.execute(
        """
        SELECT *
        FROM appeals
        WHERE guild_id=?
        ORDER BY id DESC
        """,
        (guild_id,)
    ).fetchall()

    db.close()

    return render_template(
        "appeals.html",
        guild_id=guild_id,
        guild_name=guild["name"],
        appeals=rows,
        level=level
    )

@app.route("/guild/<guild_id>/applications", methods=["GET", "POST"])
@require_feature("applications")
def applications(guild_id, level, guild):
    db = get_db()
    if request.method == "POST":
        fields = {name: clean_text(request.form.get(name), 1000) for name in ["name", "age", "timezone", "experience", "reason"]}
        if all(fields.values()):
            columns = ["guild_id", "user_id", "username", "name", "age", "timezone", "experience", "reason", "created_at"]
            values = [guild_id, current_user_id(), session["user"]["username"], fields["name"], fields["age"], fields["timezone"], fields["experience"], fields["reason"], utc_now()]
            if table_has_column(db, "applications", "application"):
                columns.append("application")
                values.append(
                    f"Name: {fields['name']}\nAge: {fields['age']}\nTimezone: {fields['timezone']}\nExperience: {fields['experience']}\nReason: {fields['reason']}"
                )
            placeholders = ", ".join("?" for _ in columns)
            db.execute(
                f"INSERT INTO applications ({', '.join(columns)}) VALUES ({placeholders})",
                values,
            )
            db.commit()
    rows = db.execute("SELECT * FROM applications WHERE guild_id=? ORDER BY id DESC", (guild_id,)).fetchall()
    db.close()
    return render_template("applications.html", guild_id=guild_id, guild_name=guild["name"], applications=rows, level=level)


@app.route("/guild/<guild_id>/tickets", methods=["GET", "POST"])
@require_feature("tickets")
def tickets(guild_id, level, guild):
    db = get_db()
    if request.method == "POST":
        action = clean_text(request.form.get("action"), 20)
        ticket_id = request.form.get("ticket_id")
        if action == "open":
            subject = clean_text(request.form.get("subject"), 200) or "Support Ticket"
            message = clean_text(request.form.get("message"), 4000)
            now = utc_now()
            cur = db.execute(
                "INSERT INTO tickets (guild_id, user_id, username, subject, status, created_at, updated_at) VALUES (?, ?, ?, ?, 'Open', ?, ?)",
                (guild_id, current_user_id(), session["user"]["username"], subject, now, now),
            )
            if message:
                db.execute(
                    "INSERT INTO ticket_messages (ticket_id, guild_id, user_id, username, message, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (cur.lastrowid, guild_id, current_user_id(), session["user"]["username"], message, now),
                )
        elif ticket_id and ticket_id.isdigit():
            ticket = db.execute("SELECT * FROM tickets WHERE id=? AND guild_id=?", (ticket_id, guild_id)).fetchone()
            if not ticket:
                db.close()
                raise NotFound("Ticket not found.")
            owns_ticket = str(ticket["user_id"]) == current_user_id()
            if action == "reply":
                message = clean_text(request.form.get("message"), 4000)
                if message and (level in {"OWNER", "STAFF"} or owns_ticket):
                    db.execute(
                        "INSERT INTO ticket_messages (ticket_id, guild_id, user_id, username, message, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (ticket_id, guild_id, current_user_id(), session["user"]["username"], message, utc_now()),
                    )
                    db.execute("UPDATE tickets SET updated_at=? WHERE id=?", (utc_now(), ticket_id))
            elif level in {"OWNER", "STAFF"} and action in {"Close", "Reopen", "Delete"}:
                if action == "Delete":
                    db.execute("DELETE FROM ticket_messages WHERE ticket_id=?", (ticket_id,))
                    db.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
                else:
                    db.execute("UPDATE tickets SET status=?, updated_at=? WHERE id=?", (action.replace("Reopen", "Open"), utc_now(), ticket_id))
        db.commit()
    if level in {"OWNER", "STAFF"}:
        ticket_rows = db.execute("SELECT * FROM tickets WHERE guild_id=? ORDER BY updated_at DESC", (guild_id,)).fetchall()
    else:
        ticket_rows = db.execute("SELECT * FROM tickets WHERE guild_id=? AND user_id=? ORDER BY updated_at DESC", (guild_id, current_user_id())).fetchall()
    messages = db.execute("SELECT * FROM ticket_messages WHERE guild_id=? ORDER BY created_at", (guild_id,)).fetchall()
    db.close()
    return render_template("tickets.html", guild_id=guild_id, guild_name=guild["name"], tickets=ticket_rows, messages=messages, level=level)


@app.route("/guild/<guild_id>/automod", methods=["GET", "POST"])
@require_feature("settings")
def automod(guild_id, level, guild):
    db = get_db()
    if request.method == "POST":
        for rule_type in ["bad_words", "spam", "invite_links", "caps_spam", "mass_mentions"]:
            enabled = 1 if request.form.get(f"{rule_type}_enabled") == "on" else 0
            config = clean_text(request.form.get(f"{rule_type}_config"), 1000)
            db.execute(
                """
                INSERT INTO automod_rules (guild_id, rule_type, enabled, config, updated_by, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(guild_id, rule_type) DO UPDATE SET
                enabled=excluded.enabled, config=excluded.config, updated_by=excluded.updated_by, updated_at=excluded.updated_at
                """,
                (guild_id, rule_type, enabled, config, current_user_id(), utc_now()),
            )
        db.commit()
    rows = db.execute("SELECT * FROM automod_rules WHERE guild_id=? ORDER BY rule_type", (guild_id,)).fetchall()
    db.close()
    rules = {row["rule_type"]: row for row in rows}
    return render_template("automod.html", guild_id=guild_id, guild_name=guild["name"], rules=rules)


@app.route("/suggestion/<int:item_id>/<status>")
@login_required
def suggestion_status(item_id, status):
    return update_status("suggestions", item_id, status, {"Approved", "Rejected", "Implemented", "Pending"})


@app.route("/appeal/<int:item_id>/<status>")
@login_required
def appeal_status(item_id, status):
    return update_status("appeals", item_id, status, {"Accepted", "Rejected", "Pending"})


@app.route("/application/<int:item_id>/<status>")
@login_required
def application_status(item_id, status):
    return update_status("applications", item_id, status, {"Accepted", "Rejected", "Pending"})


@app.errorhandler(403)
def forbidden(error):
    if "Session expired" in str(error):
        return redirect(
            url_for("login")
        )
    return render_template(
        "error.html",
        title="Access denied",
        message=str(error)
    ), 403

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", title="Not found", message=str(error)), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", title="Server error", message="DA-X hit an internal error. Please try again."), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
