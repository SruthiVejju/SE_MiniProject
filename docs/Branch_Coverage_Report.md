# Branch Coverage Report

Date: 19 November 2026 (Asia/Kolkata). Baseline commit: `b77ab83`. Application code unchanged for this reporting task. Local Windows environment: Python 3.12.4, Django 6.1.3, Coverage.py 7.17.2, SQLite 3.45.3. Django used its isolated in-memory SQLite test database, not the project's existing database.

## 1. Measured Result
**Branch coverage: 147/206 = 71.36%.** Missing destinations: 59. Partial branches reported by Coverage.py: 43.

This counts alternative control-flow destinations. No separate branch acceptance threshold is specified in the supplied requirements; this report does not invent one. A file with no branch destinations is N/A.

## 2. Method and Scope
```powershell
$env:COVERAGE_FILE = (Join-Path (Get-Location) 'docs/test_evidence/.coverage')
.\venv\Scripts\python.exe -m coverage run --branch manage.py test --verbosity 2
.\venv\Scripts\python.exe -m coverage json -o docs/test_evidence/coverage.json
.\venv\Scripts\python.exe -m coverage report
.\venv\Scripts\python.exe -m unittest test_availability -v
```

The unchanged `.coveragerc` measures core, leaves, visitors, fees, hostel, complaints, notices and api. It excludes migrations, test files/utilities, app/admin files and core management commands. Configuration, templates/CSS, dependencies and standalone availability scripts are outside that scope. Branch tracing was enabled only through `--branch`; CI/configuration were not changed.

Evidence: [coverage JSON](test_evidence/coverage.json), [Coverage.py summary](test_evidence/coverage-summary.txt). Coverage measures execution, not assertion quality or full requirements compliance.

## 3. Per-File Branch Coverage
| File | Branch destinations | Covered | Missing | Branch coverage |
|---|---:|---:|---:|---:|
| `api/auth.py` | 8 | 6 | 2 | 75.00% |
| `api/urls.py` | 0 | 0 | 0 | N/A |
| `api/v1/urls.py` | 0 | 0 | 0 | N/A |
| `api/v1/views.py` | 44 | 22 | 22 | 50.00% |
| `api/v2/urls.py` | 0 | 0 | 0 | N/A |
| `api/v2/views.py` | 12 | 2 | 10 | 16.67% |
| `complaints/forms.py` | 0 | 0 | 0 | N/A |
| `complaints/models.py` | 0 | 0 | 0 | N/A |
| `complaints/urls.py` | 0 | 0 | 0 | N/A |
| `complaints/views.py` | 4 | 4 | 0 | 100.00% |
| `core/audit.py` | 18 | 12 | 6 | 66.67% |
| `core/forms.py` | 2 | 2 | 0 | 100.00% |
| `core/login_forms.py` | 0 | 0 | 0 | N/A |
| `core/middleware.py` | 2 | 2 | 0 | 100.00% |
| `core/models.py` | 6 | 5 | 1 | 83.33% |
| `core/permissions.py` | 2 | 2 | 0 | 100.00% |
| `core/urls.py` | 0 | 0 | 0 | N/A |
| `core/validators.py` | 4 | 4 | 0 | 100.00% |
| `core/views.py` | 30 | 24 | 6 | 80.00% |
| `fees/forms.py` | 4 | 4 | 0 | 100.00% |
| `fees/models.py` | 0 | 0 | 0 | N/A |
| `fees/services.py` | 6 | 5 | 1 | 83.33% |
| `fees/urls.py` | 0 | 0 | 0 | N/A |
| `fees/views.py` | 2 | 2 | 0 | 100.00% |
| `hostel/forms.py` | 0 | 0 | 0 | N/A |
| `hostel/models.py` | 0 | 0 | 0 | N/A |
| `hostel/reports.py` | 4 | 4 | 0 | 100.00% |
| `hostel/services.py` | 6 | 6 | 0 | 100.00% |
| `hostel/urls.py` | 0 | 0 | 0 | N/A |
| `hostel/views.py` | 6 | 5 | 1 | 83.33% |
| `leaves/forms.py` | 4 | 4 | 0 | 100.00% |
| `leaves/models.py` | 0 | 0 | 0 | N/A |
| `leaves/services.py` | 4 | 4 | 0 | 100.00% |
| `leaves/urls.py` | 0 | 0 | 0 | N/A |
| `leaves/views.py` | 6 | 6 | 0 | 100.00% |
| `notices/forms.py` | 4 | 3 | 1 | 75.00% |
| `notices/models.py` | 14 | 8 | 6 | 57.14% |
| `notices/urls.py` | 0 | 0 | 0 | N/A |
| `notices/views.py` | 10 | 7 | 3 | 70.00% |
| `visitors/forms.py` | 0 | 0 | 0 | N/A |
| `visitors/models.py` | 0 | 0 | 0 | N/A |
| `visitors/urls.py` | 0 | 0 | 0 | N/A |
| `visitors/views.py` | 4 | 4 | 0 | 100.00% |

## 4. Missing Source -> Destination Arcs

Negative destinations denote function exits. Exact missing arcs from the measured snapshot:

- `api\auth.py`: 11 -> 13, 47 -> 48.
- `api\v1\views.py`: 76 -> 84, 97 -> 143, 99 -> 100, 103 -> 104, 110 -> 111, 112 -> 113, 172 -> 173, 202 -> 204, 204 -> 205, 204 -> 207, 222 -> 257, 223 -> 224, 227 -> 228, 234 -> 235, 236 -> 237, 269 -> 270, 269 -> 293, 270 -> 271, 270 -> 272, 272 -> 273, 272 -> 275, 300 -> 301.
- `api\v2\views.py`: 37 -> 38, 37 -> 40, 44 -> 45, 44 -> 63, 46 -> 47, 46 -> 55, 48 -> 49, 48 -> 50, 84 -> 92, 93 -> 94.
- `core\audit.py`: 27 -> 28, 30 -> 31, 41 -> 43, 43 -> 44, 77 -> 78, 79 -> 80.
- `core\models.py`: 103 -> 104.
- `core\views.py`: 58 -> 77, 84 -> 85, 87 -> 166, 172 -> 185, 173 -> 181, 197 -> 198.
- `fees\services.py`: 23 -> 24.
- `hostel\views.py`: 40 -> 58.
- `notices\forms.py`: 34 -> 33.
- `notices\models.py`: 39 -> 40, 42 -> 43, 44 -> 45, 46 -> 53, 47 -> 48, 68 -> -55.
- `notices\views.py`: 25 -> 34, 50 -> 76, 52 -> 78.
