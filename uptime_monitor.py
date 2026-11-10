
import csv
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

HEALTH_URL = "http://127.0.0.1:8000/health/"
LOG_FILE = Path(__file__).parent / "uptime_log.csv"
CHECK_INTERVAL = 60


def check_health():
    start_time = time.perf_counter()

    try:
        response = requests.get(HEALTH_URL, timeout=10)
        response_time = round(
            (time.perf_counter() - start_time) * 1000, 2
        )

        status = "UP" if response.status_code == 200 else "DOWN"
        status_code = response.status_code
        error = ""

    except requests.RequestException as exception:
        response_time = round(
            (time.perf_counter() - start_time) * 1000, 2
        )
        status = "DOWN"
        status_code = ""
        error = str(exception)

    file_exists = LOG_FILE.exists()
    timestamp = datetime.now(timezone.utc).isoformat()

    with LOG_FILE.open("a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "status",
                "status_code",
                "response_time_ms",
                "error"
            ])

        writer.writerow([
            timestamp,
            status,
            status_code,
            response_time,
            error
        ])

    print(f"{timestamp} | {status} | {response_time} ms")


if __name__ == "__main__":
    print("Uptime monitoring started. Press Ctrl+C to stop.")

    try:
        while True:
            check_health()
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nUptime monitoring stopped.")
