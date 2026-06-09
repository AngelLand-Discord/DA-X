import sys
from pathlib import Path
import threading

ROOT = Path(__file__).resolve().parent.parent

sys.path.append(
    str(ROOT / "bot-service")
)

from dashboard.app import app
from bot import start_bot


threading.Thread(
    target=start_bot,
    daemon=True
).start()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
