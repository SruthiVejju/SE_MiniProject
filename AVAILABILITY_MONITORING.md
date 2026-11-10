# System Availability Monitoring (NFR-2)

## Overview
The Hostel Management System includes a health-check endpoint and an uptime monitoring utility to measure service availability.

## Health Check
- Endpoint: `/health/`
- HTTP 200: Application and database are healthy.
- HTTP 503: Health check failed.

## Uptime Monitoring
Run the Django server first, then execute:

```bash
python uptime_monitor.py
```

The monitor checks the health endpoint every 60 seconds and records:
- UTC timestamp
- UP/DOWN status
- HTTP status code
- Response time
- Error details

Records are stored in `uptime_log.csv`.

Press `Ctrl+C` to stop monitoring.

## Monthly Availability Report
Run:

```bash
python availability_report.py
```

Enter the required year and month.

The report calculates uptime, downtime, excluded maintenance, unmonitored gaps, and availability percentage.

## Planned Maintenance
Add maintenance windows to `maintenance_windows.csv` using:

```csv
start_time,end_time,announced_at,description
```

All timestamps must include a timezone. Maintenance is excluded only when announced at least 24 hours before its start.

## Tests
Run:

```bash
python -m unittest test_availability -v
```

The tests cover successful availability, downtime, maintenance exclusion, unmonitored gaps, and insufficient records.

## Availability Target
The required monthly availability target is 99%.

A short monitoring run verifies the monitoring mechanism but does not establish compliance for a complete calendar month. Actual monthly availability must be assessed using accumulated monitoring records.