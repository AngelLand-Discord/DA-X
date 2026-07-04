import os
import re
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "")

SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY",
    "change-me"
)

DATABASE_PATH = (
    BASE_DIR.parent
    / "bot-service"
    / "bot.db"
)

DISCORD_API = "https://discord.com/api"

VALID_ID = re.compile(r"^\d{1,25}$")

OWNER_FEATURES = {
    "staff_access",
    "settings",
    "logs",
    "moderation",
    "suggestions",
    "appeals",
    "applications",
    "tickets",
    "automod",
    "announcements",
    "developer",
}

STAFF_FEATURES = {
    "logs",
    "moderation",
    "suggestions",
    "appeals",
    "applications",
    "tickets",
}

MEMBER_FEATURES = {
    "suggestions",
    "appeals",
    "applications",
    "tickets",
}

BOT_DATABASE = DATABASE_PATH
