import sqlite3
from contextlib import closing

from dashboard.config import DATABASE_PATH


def get_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db


def execute(query, params=()):
    with closing(get_db()) as db:
        cur = db.execute(query, params)
        db.commit()
        return cur.lastrowid


def fetch_one(query, params=()):
    with closing(get_db()) as db:
        return db.execute(query, params).fetchone()


def fetch_all(query, params=()):
    with closing(get_db()) as db:
        return db.execute(query, params).fetchall()


def column_exists(table, column):
    with closing(get_db()) as db:
        cur = db.execute(f"PRAGMA table_info({table})")
        return any(row["name"] == column for row in cur.fetchall())


def table_has_column(table, column):
    return column_exists(table, column)


def initialize_database():

    with closing(get_db()) as db:

        cur = db.cursor()

        cur.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS guild_permissions (
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'staff',
                added_by TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id,user_id)
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
                created_at TEXT NOT NULL
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
                dashboard_enabled INTEGER DEFAULT 1
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
                punishment TEXT NOT NULL DEFAULT 'warn',
                threshold INTEGER DEFAULT 5,
                duration INTEGER DEFAULT 10,
                ignored_roles TEXT DEFAULT '',
                ignored_channels TEXT DEFAULT '',
                config TEXT DEFAULT '',
                updated_by TEXT,
                updated_at TEXT NOT NULL,
                UNIQUE(guild_id, rule_type)
            );

            CREATE TABLE IF NOT EXISTS command_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT,
                requested_by TEXT,
                command_type TEXT,
                command_name TEXT,
                payload TEXT,
                status TEXT DEFAULT 'Pending',
                result TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            );
            """
        )

        migrations = {
            "applications": {
                "name": "TEXT NOT NULL DEFAULT ''",
                "age": "TEXT NOT NULL DEFAULT ''",
                "timezone": "TEXT NOT NULL DEFAULT ''",
                "experience": "TEXT NOT NULL DEFAULT ''",
                "reason": "TEXT NOT NULL DEFAULT ''",
            },
            "modlogs": {
                "guild_id": "TEXT NOT NULL DEFAULT ''"
            },
            "guild_permissions": {
                "created_at": "TEXT NOT NULL DEFAULT ''"
            },
            "appeals": {
                "appeal_type": "TEXT NOT NULL DEFAULT 'Ban Appeal'"
            },
        }

        for table, columns in migrations.items():

            for column, definition in columns.items():

                if not column_exists(table, column):

                    cur.execute(
                        f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
                    )

        db.commit()
