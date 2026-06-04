import sqlite3
from datetime import datetime, timezone

DB = sqlite3.connect(
    "bot.db",
    isolation_level=None,
    check_same_thread=False
)

DB.row_factory = sqlite3.Row

CUR = DB.cursor()


def initialize_database():
    CUR.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS judgements (
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, role_id)
    );

    CREATE TABLE IF NOT EXISTS tempbans (
        user_id INTEGER PRIMARY KEY,
        unban_time TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS modlogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        target INTEGER NOT NULL,
        moderator INTEGER NOT NULL,
        reason TEXT,
        timestamp TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS invites (
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        count INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (guild_id, user_id)
    );

    CREATE TABLE IF NOT EXISTS settings (
        guild_id INTEGER PRIMARY KEY,
        log_channel INTEGER,
        mod_role INTEGER,
        announcement_channel INTEGER,
        dashboard_enabled INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS dashboard_users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        access_token TEXT,
        refresh_token TEXT,
        expires_at TEXT
    );
    """)


def now():
    return datetime.now(timezone.utc)


def log_action(
    action: str,
    target: int,
    moderator: int,
    reason: str = ""
):
    CUR.execute(
        """
        INSERT INTO modlogs
        (
            action,
            target,
            moderator,
            reason,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            action,
            target,
            moderator,
            reason,
            now().isoformat()
        )
    )


def get_mod_history(user_id: int):
    CUR.execute(
        """
        SELECT action,
               COUNT(*) as count
        FROM modlogs
        WHERE target=?
        GROUP BY action
        """,
        (user_id,)
    )

    return CUR.fetchall()


def save_tempban(user_id: int, unban_time):
    CUR.execute(
        """
        INSERT OR REPLACE INTO tempbans
        VALUES (?, ?)
        """,
        (
            user_id,
            unban_time.isoformat()
        )
    )


def remove_tempban(user_id: int):
    CUR.execute(
        """
        DELETE FROM tempbans
        WHERE user_id=?
        """,
        (user_id,)
    )


def get_tempbans():
    CUR.execute(
        """
        SELECT *
        FROM tempbans
        """
    )

    return CUR.fetchall()


def save_judgement(user_id: int, role_id: int):
    CUR.execute(
        """
        INSERT OR IGNORE INTO judgements
        VALUES (?, ?)
        """,
        (
            user_id,
            role_id
        )
    )


def get_judgements(user_id: int):
    CUR.execute(
        """
        SELECT role_id
        FROM judgements
        WHERE user_id=?
        """,
        (user_id,)
    )

    return CUR.fetchall()


def clear_judgements(user_id: int):
    CUR.execute(
        """
        DELETE FROM judgements
        WHERE user_id=?
        """,
        (user_id,)
    )


def add_invite(guild_id: int, user_id: int):
    CUR.execute(
        """
        INSERT INTO invites
        (
            guild_id,
            user_id,
            count
        )
        VALUES (?, ?, 1)

        ON CONFLICT(guild_id, user_id)
        DO UPDATE SET count=count+1
        """,
        (
            guild_id,
            user_id
        )
    )


def get_invites(guild_id: int):
    CUR.execute(
        """
        SELECT *
        FROM invites
        WHERE guild_id=?
        ORDER BY count DESC
        """,
        (guild_id,)
    )

    return CUR.fetchall()