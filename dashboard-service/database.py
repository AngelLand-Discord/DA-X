import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR.parent / "bot-service" / "bot.db"


def get_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db


def initialize_database():
    from dashboard.app import initialize_database as initialize_dashboard_database

    initialize_dashboard_database()
