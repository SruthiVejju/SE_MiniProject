
import csv
import calendar
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "uptime_log.csv"
MAINTENANCE_FILE = BASE_DIR / "maintenance_windows.csv"

CHECK_INTERVAL = 60
MAX_GAP = CHECK_INTERVAL * 2
AVAILABILITY_TARGET = 99.0


def calculate_availability(records, maintenance_windows=None):
    """
    Calculate availability from consecutive health-check records.

    Only intervals up to MAX_GAP are considered monitored.
    The previous check's status is applied to the interval
    ending at the next check.
    """

    if len(records) < 2:
        raise ValueError("At least two monitoring records are required.")

    maintenance_windows = maintenance_windows or []
    records = sorted(records, key=lambda item: item[0])

    total_seconds = 0
    uptime_seconds = 0
    excluded_seconds = 0
    unmonitored_seconds = 0

    for (previous_time, status), (next_time, _) in zip(
        records, records[1:]
    ):
        interval = (next_time - previous_time).total_seconds()

        if interval <= 0:
            continue

        if interval > MAX_GAP:
            unmonitored_seconds += interval
            continue

        excluded = 0

        for maintenance_start, maintenance_end in maintenance_windows:
            overlap_start = max(previous_time, maintenance_start)
            overlap_end = min(next_time, maintenance_end)

            if overlap_end > overlap_start:
                excluded += (
                    overlap_end - overlap_start
                ).total_seconds()

        eligible = max(0, interval - excluded)

        total_seconds += eligible
        excluded_seconds += excluded

        if status == "UP":
            uptime_seconds += eligible

    if total_seconds <= 0:
        raise ValueError("No eligible monitoring duration found.")

    downtime_seconds = total_seconds - uptime_seconds

    return {
        "monitored_seconds": total_seconds,
        "uptime_seconds": uptime_seconds,
        "downtime_seconds": downtime_seconds,
        "excluded_seconds": excluded_seconds,
        "unmonitored_seconds": unmonitored_seconds,
        "availability": (
            uptime_seconds / total_seconds
        ) * 100,
    }


def load_monitoring_records():
    """Load all uptime records from the CSV file."""

    records = []

    if not LOG_FILE.exists():
        raise FileNotFoundError(
            "Uptime log not found. Run uptime_monitor.py first."
        )

    with LOG_FILE.open("r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            timestamp = datetime.fromisoformat(row["timestamp"])

            if timestamp.tzinfo is None:
                raise ValueError(
                    "Monitoring timestamps must include a timezone."
                )

            status = row["status"].upper()

            if status not in ("UP", "DOWN"):
                raise ValueError(
                    f"Invalid monitoring status: {status}"
                )

            records.append((timestamp, status))

    return sorted(records, key=lambda item: item[0])


def load_maintenance_windows():
    """Load only maintenance announced at least 24 hours beforehand."""

    windows = []

    if not MAINTENANCE_FILE.exists():
        return windows

    with MAINTENANCE_FILE.open("r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            start = datetime.fromisoformat(row["start_time"])
            end = datetime.fromisoformat(row["end_time"])
            announced = datetime.fromisoformat(row["announced_at"])

            if not all(
                value.tzinfo is not None
                for value in (start, end, announced)
            ):
                raise ValueError(
                    "Maintenance timestamps must include a timezone."
                )

            if end <= start:
                raise ValueError(
                    "Maintenance end must be after its start."
                )

            if announced <= start - timedelta(hours=24):
                windows.append((start, end))

    return windows


def generate_monthly_report(year, month):
    """Generate availability report for a calendar month."""

    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12.")

    records = load_monitoring_records()

    month_start = datetime(
        year, month, 1, tzinfo=timezone.utc
    )

    if month == 12:
        month_end = datetime(
            year + 1, 1, 1, tzinfo=timezone.utc
        )
    else:
        month_end = datetime(
            year, month + 1, 1, tzinfo=timezone.utc
        )

    # Include the nearest record before and after the month.
    before = [
        record for record in records
        if record[0] < month_start
    ]

    inside = [
        record for record in records
        if month_start <= record[0] < month_end
    ]

    after = [
        record for record in records
        if record[0] >= month_end
    ]

    month_records = before[-1:] + inside + after[:1]

    if len(month_records) < 2:
        print(
            "Insufficient monitoring records to calculate "
            "this month's availability."
        )
        return

    maintenance = load_maintenance_windows()

    # Clip monitoring records to the requested calendar month.
    clipped_records = []

    for timestamp, status in month_records:
        if timestamp < month_start:
            timestamp = month_start
        elif timestamp > month_end:
            timestamp = month_end

        if not clipped_records or timestamp > clipped_records[-1][0]:
            clipped_records.append((timestamp, status))

    # Add a boundary record at month end using the last known status.
    if clipped_records[-1][0] < month_end:
        clipped_records.append(
            (month_end, clipped_records[-1][1])
        )

    result = calculate_availability(
        clipped_records,
        maintenance
    )

    days_in_month = calendar.monthrange(year, month)[1]
    expected_seconds = days_in_month * 24 * 60 * 60

    monitored_seconds = result["monitored_seconds"]
    coverage = monitored_seconds / expected_seconds * 100

    # Do not claim monthly compliance when monitoring coverage
    # is incomplete.
    enough_coverage = (
        result["unmonitored_seconds"] == 0
        and abs(monitored_seconds - expected_seconds) < 1
    )

    passed = (
        enough_coverage
        and result["availability"] >= AVAILABILITY_TARGET
    )

    print(
        f"\nAvailability Report: "
        f"{calendar.month_name[month]} {year}"
    )

    print("-" * 45)
    print(
        f"Expected month duration: "
        f"{expected_seconds:.0f} seconds"
    )
    print(
        f"Monitored duration: "
        f"{monitored_seconds:.0f} seconds"
    )
    print(
        f"Monitoring coverage: {coverage:.2f}%"
    )
    print(
        f"Uptime: {result['uptime_seconds']:.0f} seconds"
    )
    print(
        f"Downtime: {result['downtime_seconds']:.0f} seconds"
    )
    print(
        f"Excluded maintenance: "
        f"{result['excluded_seconds']:.0f} seconds"
    )
    print(
        f"Unmonitored gaps: "
        f"{result['unmonitored_seconds']:.0f} seconds"
    )
    print(
        f"Availability: {result['availability']:.2f}%"
    )
    print(
        f"Required target: {AVAILABILITY_TARGET:.2f}%"
    )

    if not enough_coverage:
        print("Result: INSUFFICIENT MONITORING COVERAGE")
    elif passed:
        print("Result: PASS")
    else:
        print("Result: BELOW TARGET")


if __name__ == "__main__":
    try:
        year = int(input("Enter year (YYYY): "))
        month = int(input("Enter month (1-12): "))

        generate_monthly_report(year, month)

    except (ValueError, FileNotFoundError) as error:
        print(f"Error: {error}")
