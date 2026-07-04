import threading
import sys
from pathlib import Path

# Add bot-service to Python path
BOT_DIR = Path(__file__).resolve().parent.parent / "bot-service"
sys.path.insert(0, str(BOT_DIR))

from bot import start_bot
from dashboard.app import app


def run_bot():
    start_bot()


bot_thread = threading.Thread(
    target=run_bot,
    daemon=True,
)

bot_thread.start()

app.run(
    host="0.0.0.0",
    port=5000,
    debug=False,
)