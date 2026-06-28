import os
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv

# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

BOT_DIR = BASE_DIR.parent / "bot-service"

DATABASE_PATH = BOT_DIR / "bot.db"

# -------------------------------------------------
# Environment
# -------------------------------------------------

load_dotenv(BASE_DIR / ".env")

# -------------------------------------------------
# Discord OAuth
# -------------------------------------------------

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")

CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")

REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "")

DISCORD_API = "https://discord.com/api"

# -------------------------------------------------
# Discord Bot
# -------------------------------------------------

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

DEV_ID = int(os.getenv("DEV_ID", "0"))

# -------------------------------------------------
# Flask
# -------------------------------------------------

SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-me")

SESSION_LIFETIME = timedelta(days=30)

# -------------------------------------------------
# Dashboard
# -------------------------------------------------

APP_NAME = "DA-X"

APP_VERSION = "2.0.0"

DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

HOST = "0.0.0.0"

PORT = int(os.getenv("PORT", "10000"))

# -------------------------------------------------
# Validation
# -------------------------------------------------

VALID_DISCORD_ID_LENGTH = 25
