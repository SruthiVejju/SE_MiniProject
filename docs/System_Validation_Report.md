# System Validation Report

Date: 19 November 2026 (Asia/Kolkata). Baseline commit: `b77ab83`. Application code unchanged for this reporting task. Local Windows environment: Python 3.12.4, Django 6.1.3, Coverage.py 7.17.2, SQLite 3.45.3. Django used its isolated in-memory SQLite test database, not the project's existing database.

## 1. Conclusion
**Automated regression: PASS (145 Django tests + 7 availability-tool tests). Full SRS acceptance: INCOMPLETE.** Several baseline requirements differ from the implementation; manual/operational checks remain unperformed. The full Test Plan exit criteria are not signed off.

Validation combines actual execution of the inherited tests and inspection of implementation/documents. Django's in-process test client exercises forms, views, sessions and ORM state; it is not a live browser/network test. No application changes were made.

## 2. Evidence
- [Unit Test Report](Unit_Test_Report.md), [Django log](test_evidence/django-tests.txt), [availability log](test_evidence/availability-tests.txt): zero failures/errors/skips.
- [Code Coverage Report](Code_Coverage_Report.md): 91.18% statements; combined statement/branch metric 88.16%.
- [Branch Coverage Report](Branch_Coverage_Report.md): 71.36% branch destinations.
- [Bandit JSON](test_evidence/security-scan.json): zero high-severity findings and no scan errors. Lower-severity results were filtered out; metrics record one low-severity finding. Static scanning does not prove absence of vulnerabilities.

Security scan command:
```powershell
.\venv\Scripts\python.exe -m bandit -r core leaves visitors fees hostel complaints notices api config -x '*/tests.py,*/testutils.py,*/test_*.py' --severity-level high -f json -o docs/test_evidence/security-scan.json
```

## 3. Functional Requirement Results
PASS refers only to the tested implemented workflow. PARTIAL means the original acceptance criteria are not fully established.

| Requirement | Executed evidence / observed limitation | Assessment |
|---|---|---|
| FR-1 Registration | Registration, duplicate-email and password-mismatch tests pass. Department/contact and dedicated roll-number field absent. | PARTIAL |
| FR-2 Login | Success, failed-attempt count, five-failure lockout, rejection during lockout, reset and logout tests pass. | PASS tested session flow |
| FR-3 Allocation | Allocation, occupied-bed and duplicate-student rejection, role checks pass. No production concurrency test; SQLite has no row-level SELECT FOR UPDATE. | PASS sequential flows |
| FR-4 Allocation/dues | Own-dashboard, dues, query-count and isolation tests pass; two-second target not measured. | PARTIAL |
| FR-5 Complaints | HTML 10/500-character boundaries, categories and unique IDs pass; API accepts >=5 without matching maximum enforcement. | PARTIAL |
| FR-6 Complaint management | Warden status/remarks, block restrictions and role tests pass. | PASS tested flows |
| FR-7 Leave submission | Required fields/dates, routing, own-list and role checks pass. | PASS tested flows |
| FR-8 Decisions | Approve/reject and notification creation within one minute pass. Live notification delivery to an idle browser not verified. | PARTIAL |
| FR-9 Visitors | Guard-only entry/exit, host checks, timestamps and repeated-exit handling pass. | PASS tested flows |
| FR-10 Fees | Cash/online-reference recording, receipts, balances and rejection tests pass; no gateway integration. | PASS recording; integration absent |
| FR-11 Notices | General/block visibility, publishing permissions and search pass. | PASS tested flows |
| FR-12 Occupancy | Calculations, active allocation totals, report page and PDF generation/download pass. | PASS tested flows |

## 4. Non-Functional and Security Results
| Requirement | Measured evidence / limitation | Assessment |
|---|---|---|
| NFR-1 Performance | Query-count test passes; no 200-user p95 latency result. | NOT VERIFIED at target |
| NFR-2 Availability | Seven synthetic monitoring/report calculation tests pass; no full-month uptime data. | NOT VERIFIED operationally |
| NFR-3 Usability | Form/help/success-page checks pass; no five-participant timed study. | NOT VERIFIED with users |
| NFR-4 Scalability | Seeding/load tools exist; no measured 5,000-account target-load result. | NOT VERIFIED |
| NFR-5 Maintainability | 91.18% statements, 88.16% combined metric exceed aggregate 70% gate; some files remain below 70%. | PASS aggregate gate only |
| NFR-6 Portability | Three static HTML/CSS tests pass; manual browser matrix is TBD. | NOT VERIFIED on six versions |
| NFR-7 Reliability | Complaint/leave persistence and connection teardown/re-query pass; no OS process crash. | PARTIAL |
| NFR-8 Compatibility | Actual v1/v2 schemas and session-authenticated API checks pass. | PASS tested contracts |
| SEC-REQ-1 Passwords | Default PBKDF2 rather than required bcrypt; no dedicated bcrypt test in discovered suite. | BASELINE DEVIATION |
| SEC-REQ-2 RBAC | Role, own-data and block tests pass for exercised endpoints. | PASS tested cases |
| SEC-REQ-3 TLS | Three production-mode Django security tests pass; no real TLS negotiation; redirects instead of HTTP rejection. | PARTIAL / deviation |
| SEC-REQ-4 Input security | Sanitization tests and zero-high Bandit scan pass. Some session-authenticated JSON writes are CSRF exempt; API bounds differ. | PARTIAL; no blanket security sign-off |
| SEC-REQ-5 Audit | Events, instance update/delete blocking, 365-day metadata and admin-view RBAC pass; DB immutability/operational retention not established. | PARTIAL |

## 5. Original Test Plan Reconciliation
| Original cases | Execution against actual code |
|---|---|
| TC-01 | Duplicate email tested; exact original duplicate-roll-number API contract not executed. |
| TC-02, TC-03 | Equivalent HTML/service allocation tests pass; original REST 201/409 endpoints absent. |
| TC-04 | Complaint submission passes; API/form validation differences remain. |
| TC-05 | HTML warden update passes; original PATCH endpoint absent. |
| TC-06 | Payment service/receipt tests pass; original POST API absent. |
| TC-07 | Target load/data volume not executed. |
| TC-08 | Static checks only; browser matrix pending. |
| TC-09 | Own-data/RBAC tests pass; original JWT endpoint request not executed. |
| TC-10 | Related sanitization checks/static scan pass; exact original login API payload case not executed. |
| TC-11, TC-12 | Actual notice and occupancy/PDF checks pass. |
| TC-13 | Connection-teardown persistence checks pass; no process restart. |
| TC-14 | Actual versioned API compatibility checks pass. |
| TC-15 | Audit instance immutability/retention metadata checks pass, with limits above. |

## 6. Outstanding Acceptance Work
Browser/version tests, five-person usability timing, performance/scalability measurements, monthly uptime and deployed TLS verification remain unperformed. Registration, bcrypt, gateway integration, original API contracts/validation and notification/audit guarantees require either separate implementation or explicit acceptance of the documented differences.

The [original Test Plan](Test_Plan.md) remains unchanged. The [current SAD](Architecture_Design.md) and [Design Deviations](Design_Deviations.md) reconcile the design. This report records pending criteria rather than presenting unperformed tests as successful.
