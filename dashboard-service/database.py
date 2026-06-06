import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = (
    BASE_DIR.parent /
    "bot-service" /
    "bot.db"
)

def get_db():

    db = sqlite3.connect(
        DATABASE_PATH
    )

    db.row_factory = sqlite3.Row

    return db


def initialize_database():

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

    db.commit()
    db.close()
