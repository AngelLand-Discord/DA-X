import sys
from pathlib import Path
import threading

print("STEP 1")

ROOT = Path(__file__).resolve().parent.parent

BOT_DIR = ROOT / "bot-service"

sys.path.insert(
    0,
    str(BOT_DIR)
)

print("STEP 3")

from dashboard.app import app

print("STEP 4")

print(sys.path)

from bot import start_bot

print("STEP 5")

threading.Thread(
    target=start_bot,
    daemon=True
).start()

print("STEP 6")

if __name__ == "__main__":

    print("STEP 7")

    app.run(
        host="0.0.0.0",
        port=10000
    )
