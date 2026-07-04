import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import json

DATABASE_PATH = Path(__file__).resolve().parents[1] / "bot.db"

DB = sqlite3.connect(DATABASE_PATH, isolation_level=None, check_same_thread=False)
DB.row_factory = sqlite3.Row
CUR = DB.cursor()


def now():
    return datetime.now(timezone.utc).isoformat()


def column_exists(table, column):
    CUR.execute(f"PRAGMA table_info({table})")
    return any(row["name"] == column for row in CUR.fetchall())


def initialize_database():
    CUR.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS judgements (
        user_id TEXT NOT NULL,
        role_id TEXT NOT NULL,
        PRIMARY KEY (user_id, role_id)
    );

    CREATE TABLE IF NOT EXISTS tempbans (
        user_id TEXT PRIMARY KEY,
        unban_time TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS guild_permissions (
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'staff',
        added_by TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT '',
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
        appeal TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending',
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
    
    CREATE TABLE IF NOT EXISTS command_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id TEXT NOT NULL,
        requested_by TEXT NOT NULL,
        command_type TEXT NOT NULL,
        command_name TEXT NOT NULL,
        payload TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending',
        error TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT

    );
    CREATE TABLE IF NOT EXISTS invites (
        guild_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        count INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (guild_id, user_id)
    );

    CREATE TABLE IF NOT EXISTS dashboard_users (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        access_token TEXT,
        refresh_token TEXT,
        expires_at TEXT
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
            if not column_exists(table, column):
                CUR.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def log_action(guild_id, action, target, moderator, reason=""):
    CUR.execute(
        """
        INSERT INTO modlogs (guild_id, action, target, moderator, reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (str(guild_id), str(action), str(target), str(moderator), reason, now()),
    )


def add_warning(guild_id, user_id, moderator_id, reason=""):
    CUR.execute(
        """
        INSERT INTO warnings (guild_id, user_id, moderator_id, reason, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(guild_id), str(user_id), str(moderator_id), reason, now()),
    )
    log_action(guild_id, "WARN", user_id, moderator_id, reason)


def get_mod_history(guild_id, user_id):
    CUR.execute(
        """
        SELECT action, COUNT(*) as count
        FROM modlogs
        WHERE guild_id=? AND target=?
        GROUP BY action
        """,
        (str(guild_id), str(user_id)),
    )
    return CUR.fetchall()


def save_tempban(user_id, unban_time):
    CUR.execute("INSERT OR REPLACE INTO tempbans VALUES (?, ?)", (str(user_id), unban_time.isoformat()))


def remove_tempban(user_id):
    CUR.execute("DELETE FROM tempbans WHERE user_id=?", (str(user_id),))


def get_tempbans():
    CUR.execute("SELECT * FROM tempbans")
    return CUR.fetchall()


def save_judgement(user_id, role_id):
    CUR.execute("INSERT OR IGNORE INTO judgements VALUES (?, ?)", (str(user_id), str(role_id)))


def get_judgements(user_id):
    CUR.execute("SELECT role_id FROM judgements WHERE user_id=?", (str(user_id),))
    return CUR.fetchall()


def clear_judgements(user_id):
    CUR.execute("DELETE FROM judgements WHERE user_id=?", (str(user_id),))


def add_invite(guild_id, user_id):
    CUR.execute(
        """
        INSERT INTO invites (guild_id, user_id, count)
        VALUES (?, ?, 1)
        ON CONFLICT(guild_id, user_id) DO UPDATE SET count=count+1
        """,
        (str(guild_id), str(user_id)),
    )


def get_invites(guild_id):
    CUR.execute("SELECT * FROM invites WHERE guild_id=? ORDER BY count DESC", (str(guild_id),))
    return CUR.fetchall()


def get_automod_rules(guild_id):
    CUR.execute("SELECT * FROM automod_rules WHERE guild_id=? AND enabled=1", (str(guild_id),))
    return {row["rule_type"]: row["config"] for row in CUR.fetchall()}


def create_ticket(guild_id, user_id, username, subject, message=""):
    created = now()
    CUR.execute(
        """
        INSERT INTO tickets (guild_id, user_id, username, subject, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'Open', ?, ?)
        """,
        (str(guild_id), str(user_id), username, subject, created, created),
    )
    ticket_id = CUR.lastrowid
    if message:
        add_ticket_message(ticket_id, guild_id, user_id, username, message)
    return ticket_id


def add_ticket_message(ticket_id, guild_id, user_id, username, message):
    CUR.execute(
        """
        INSERT INTO ticket_messages (ticket_id, guild_id, user_id, username, message, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (ticket_id, str(guild_id), str(user_id), username, message, now()),
    )
    CUR.execute("UPDATE tickets SET updated_at=? WHERE id=?", (now(), ticket_id))


def set_ticket_status(ticket_id, guild_id, status):
    CUR.execute(
        "UPDATE tickets SET status=?, updated_at=? WHERE id=? AND guild_id=?",
        (status, now(), ticket_id, str(guild_id)),
    )


def get_open_ticket_for_user(guild_id, user_id):
    CUR.execute(
        """
        SELECT * FROM tickets
        WHERE guild_id=? AND user_id=? AND status='Open'
        ORDER BY id DESC LIMIT 1
        """,
        (str(guild_id), str(user_id)),
    )
    return CUR.fetchone()
def queue_command(
    guild_id,
    requested_by,
    command_type,
    command_name,
    payload,
):

    CUR.execute(
        """
        INSERT INTO command_queue
        (
            guild_id,
            requested_by,
            command_type,
            command_name,
            payload,
            created_at
        )
        VALUES
        (
            ?,?,?,?,?,?
        )
        """,
        (
            str(guild_id),
            str(requested_by),
            command_type,
            command_name,
            json.dumps(payload),
            now(),
        ),
    )

    return CUR.lastrowid


def get_next_command():

    CUR.execute(
        """
        SELECT *
        FROM command_queue
        WHERE status='Pending'
        ORDER BY id
        LIMIT 1
        """
    )

    return CUR.fetchone()


def start_command(command_id):

    CUR.execute(
        """
        UPDATE command_queue
        SET
            status='Running',
            started_at=?
        WHERE id=?
        """,
        (
            now(),
            command_id,
        ),
    )


def finish_command(command_id):

    CUR.execute(
        """
        UPDATE command_queue
        SET
            status='Completed',
            completed_at=?
        WHERE id=?
        """,
        (
            now(),
            command_id,
        ),
    )


def fail_command(command_id, error):

    CUR.execute(
        """
        UPDATE command_queue
        SET
            status='Failed',
            error=?,
            completed_at=?
        WHERE id=?
        """,
        (
            str(error),
            now(),
            command_id,
        ),
    )
