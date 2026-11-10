
import unittest
from datetime import datetime, timezone, timedelta

from availability_report import calculate_availability


class AvailabilityTests(unittest.TestCase):

    def setUp(self):
        self.start = datetime(
            2026, 11, 10, 10, 0, tzinfo=timezone.utc
        )

    def test_100_percent_availability(self):
        records = [
            (self.start, "UP"),
            (self.start + timedelta(seconds=60), "UP"),
            (self.start + timedelta(seconds=120), "UP"),
        ]

        result = calculate_availability(records)

        self.assertEqual(result["availability"], 100.0)
        self.assertEqual(result["downtime_seconds"], 0)

    def test_downtime_reduces_availability(self):
        records = [
            (self.start, "UP"),
            (self.start + timedelta(seconds=60), "DOWN"),
            (self.start + timedelta(seconds=120), "UP"),
        ]

        result = calculate_availability(records)

        self.assertEqual(result["availability"], 50.0)
        self.assertEqual(result["downtime_seconds"], 60)

    def test_planned_maintenance_is_excluded(self):
        records = [
            (self.start, "UP"),
            (self.start + timedelta(seconds=60), "DOWN"),
            (self.start + timedelta(seconds=120), "UP"),
        ]

        maintenance = [
            (
                self.start + timedelta(seconds=60),
                self.start + timedelta(seconds=120),
            )
        ]

        result = calculate_availability(records, maintenance)

        self.assertEqual(result["availability"], 100.0)
        self.assertEqual(result["excluded_seconds"], 60)

    def test_long_monitoring_gap_is_not_counted(self):
        records = [
            (self.start, "UP"),
            (self.start + timedelta(seconds=60), "UP"),
            (self.start + timedelta(seconds=600), "UP"),
        ]

        result = calculate_availability(records)

        self.assertEqual(result["monitored_seconds"], 60)
        self.assertEqual(result["unmonitored_seconds"], 540)

    def test_insufficient_records(self):
        with self.assertRaises(ValueError):
            calculate_availability([
                (self.start, "UP")
            ])

    def test_incomplete_month_sample_does_not_claim_full_coverage(self):
        records = [
            (self.start, "UP"),
            (self.start + timedelta(seconds=60), "UP"),
        ]

        result = calculate_availability(records)

        # The interval is available, but it represents only 60 seconds,
        # not a complete calendar month.
        self.assertEqual(result["availability"], 100.0)
        self.assertEqual(result["monitored_seconds"], 60)

    def test_duplicate_timestamps_do_not_count_as_uptime(self):
        records = [
            (self.start, "UP"),
            (self.start, "DOWN"),
        ]

        with self.assertRaises(ValueError):
            calculate_availability(records)


if __name__ == "__main__":
    unittest.main()
