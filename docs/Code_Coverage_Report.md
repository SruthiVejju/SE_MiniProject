# Code Coverage Report

Date: 19 November 2026 (Asia/Kolkata). Baseline commit: `b77ab83`. Application code unchanged for this reporting task. Local Windows environment: Python 3.12.4, Django 6.1.3, Coverage.py 7.17.2, SQLite 3.45.3. Django used its isolated in-memory SQLite test database, not the project's existing database.

## 1. Measured Result
**Statement coverage: 1044/1145 = 91.18%.** Missing executable statements: 101.

Coverage.py's combined statement-and-branch percentage is **88.16%**, distinct from pure statement coverage. Both aggregate values exceed the existing 70% gate. The aggregate gate does not establish 70% coverage for every module.

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

## 3. Per-File Statement Coverage
| File | Statements | Covered | Missing | Statement coverage |
|---|---:|---:|---:|---:|
| `api/auth.py` | 37 | 34 | 3 | 91.89% |
| `api/urls.py` | 3 | 3 | 0 | 100.00% |
| `api/v1/urls.py` | 3 | 3 | 0 | 100.00% |
| `api/v1/views.py` | 124 | 94 | 30 | 75.81% |
| `api/v2/urls.py` | 3 | 3 | 0 | 100.00% |
| `api/v2/views.py` | 45 | 26 | 19 | 57.78% |
| `complaints/forms.py` | 17 | 17 | 0 | 100.00% |
| `complaints/models.py` | 24 | 23 | 1 | 95.83% |
| `complaints/urls.py` | 3 | 3 | 0 | 100.00% |
| `complaints/views.py` | 32 | 32 | 0 | 100.00% |
| `core/audit.py` | 45 | 36 | 9 | 80.00% |
| `core/forms.py` | 16 | 16 | 0 | 100.00% |
| `core/login_forms.py` | 5 | 5 | 0 | 100.00% |
| `core/middleware.py` | 11 | 11 | 0 | 100.00% |
| `core/models.py` | 62 | 58 | 4 | 93.55% |
| `core/permissions.py` | 21 | 21 | 0 | 100.00% |
| `core/urls.py` | 3 | 3 | 0 | 100.00% |
| `core/validators.py` | 25 | 25 | 0 | 100.00% |
| `core/views.py` | 109 | 97 | 12 | 88.99% |
| `fees/forms.py` | 22 | 22 | 0 | 100.00% |
| `fees/models.py` | 26 | 26 | 0 | 100.00% |
| `fees/services.py` | 24 | 23 | 1 | 95.83% |
| `fees/urls.py` | 3 | 3 | 0 | 100.00% |
| `fees/views.py` | 23 | 23 | 0 | 100.00% |
| `hostel/forms.py` | 13 | 13 | 0 | 100.00% |
| `hostel/models.py` | 31 | 30 | 1 | 96.77% |
| `hostel/reports.py` | 52 | 52 | 0 | 100.00% |
| `hostel/services.py` | 27 | 24 | 3 | 88.89% |
| `hostel/urls.py` | 4 | 4 | 0 | 100.00% |
| `hostel/views.py` | 51 | 42 | 9 | 82.35% |
| `leaves/forms.py` | 22 | 22 | 0 | 100.00% |
| `leaves/models.py` | 20 | 20 | 0 | 100.00% |
| `leaves/services.py` | 27 | 27 | 0 | 100.00% |
| `leaves/urls.py` | 3 | 3 | 0 | 100.00% |
| `leaves/views.py` | 40 | 40 | 0 | 100.00% |
| `notices/forms.py` | 23 | 23 | 0 | 100.00% |
| `notices/models.py` | 38 | 31 | 7 | 81.58% |
| `notices/urls.py` | 4 | 4 | 0 | 100.00% |
| `notices/views.py` | 41 | 39 | 2 | 95.12% |
| `visitors/forms.py` | 15 | 15 | 0 | 100.00% |
| `visitors/models.py` | 16 | 16 | 0 | 100.00% |
| `visitors/urls.py` | 3 | 3 | 0 | 100.00% |
| `visitors/views.py` | 29 | 29 | 0 | 100.00% |

## 4. Missing Executable Lines

- `api\auth.py`: 48, 51, 52.
- `api\v1\views.py`: 100, 104, 111, 113, 143, 151, 152, 173, 174, 175, 176, 204, 205, 207, 224, 228, 235, 237, 257, 267, 269, 270, 271, 272, 273, 275, 277, 291, 293, 301.
- `api\v2\views.py`: 35, 36, 37, 38, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 55, 63, 94, 127, 128.
- `complaints\models.py`: 57.
- `core\audit.py`: 28, 31, 44, 45, 64, 65, 66, 78, 80.
- `core\models.py`: 72, 104, 105, 112.
- `core\views.py`: 77, 85, 166, 185, 198, 212, 213, 214, 215, 217, 222, 223.
- `fees\services.py`: 24.
- `hostel\models.py`: 77.
- `hostel\services.py`: 75, 77, 81.
- `hostel\views.py`: 17, 19, 23, 28, 52, 53, 65, 67, 74.
- `notices\models.py`: 31, 32, 40, 43, 45, 48, 53.
- `notices\views.py`: 76, 78.
