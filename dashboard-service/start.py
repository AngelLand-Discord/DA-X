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

print("STEP 2")
print(sys.path[:5])

from dashboard.app import app

print("STEP 3")

from bot import start_bot

print("STEP 4")

threading.Thread(
    target=start_bot,
    daemon=True
).start()

print("STEP 5")

if __name__ == "__main__":

    print("STEP 6")

    app.run(
        host="0.0.0.0",
        port=10000
    )
