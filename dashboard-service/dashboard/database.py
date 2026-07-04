import sqlite3

from .config import DATABASE_PATH


def get_db():

    db = sqlite3.connect(DATABASE_PATH)

    db.row_factory = sqlite3.Row

    return db


def execute(query, params=()):

    db = get_db()

    cur = db.execute(query, params)

    db.commit()

    db.close()

    return cur


def fetchone(query, params=()):

    db = get_db()

    row = db.execute(query, params).fetchone()

    db.close()

    return row


def fetchall(query, params=()):

    db = get_db()

    rows = db.execute(query, params).fetchall()

    db.close()

    return rows


def column_exists(cur, table, column):

    cur.execute(f"PRAGMA table_info({table})")

    return any(
        row["name"] == column
        for row in cur.fetchall()
    )


def table_has_column(table, column):

    db = get_db()

    cur = db.cursor()

    exists = column_exists(
        cur,
        table,
        column
    )

    db.close()

    return exists


def initialize_database():

    db = get_db()

    cur = db.cursor()

    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS command_queue(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            guild_id TEXT NOT NULL,

            requested_by TEXT NOT NULL,

            command_type TEXT NOT NULL,

            command_name TEXT NOT NULL,

            payload TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'PENDING',

            error TEXT,

            created_at TEXT NOT NULL,

            started_at TEXT,

            finished_at TEXT

        );
        """
    )

    db.commit()

    db.close()


# -----------------------------------------
# Queue Helpers
# -----------------------------------------

def add_command(
    guild_id,
    requested_by,
    command_type,
    command_name,
    payload,
    created_at,
):

    execute(
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
        (?, ?, ?, ?, ?, ?)
        """,
        (
            guild_id,
            requested_by,
            command_type,
            command_name,
            payload,
            created_at,
        ),
    )


def get_next_command():

    return fetchone(
        """
        SELECT *

        FROM command_queue

        WHERE status='PENDING'

        ORDER BY id

        LIMIT 1
        """
    )


def start_command(command_id):

    execute(
        """
        UPDATE command_queue

        SET
            status='RUNNING',
            started_at=datetime('now')

        WHERE id=?
        """,
        (command_id,),
    )


def finish_command(command_id):

    execute(
        """
        UPDATE command_queue

        SET
            status='COMPLETED',
            finished_at=datetime('now')

        WHERE id=?
        """,
        (command_id,),
    )


def fail_command(
    command_id,
    error,
):

    execute(
        """
        UPDATE command_queue

        SET
            status='FAILED',
            error=?,
            finished_at=datetime('now')

        WHERE id=?
        """,
        (
            str(error),
            command_id,
        ),
    )
