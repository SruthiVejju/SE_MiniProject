# Design Deviations from the Submitted Baseline

Date: 19 November 2026. Baseline: original SRS and React/Express SAD. Current design: [Architecture & Design Specification](Architecture_Design.md).

This record documents observed differences for the final demo. It does not claim evaluator approval, retroactive acceptance or completion of unmet requirements. Implementation was not changed during this documentation/reporting task. The rationale below explains practical tradeoffs; it does not establish the historical reason each change was made.

| Area | Submitted baseline | Implemented outcome | Consequence / explanation for demo |
|---|---|---|---|
| Frontend | React SPA calling REST services | Django templates and plain CSS | One runtime and no JavaScript build; forms call views directly. |
| Backend | Independently deployable Express services and API gateway | Modular Django monolith | Domain apps share a process, middleware and database; no network gateway or service isolation. |
| Persistence | PostgreSQL, separate audit store, HostelBlock entity | SQLite; audit table in same DB; string block fields | Simple local setup; SQLite lacks row-level SELECT FOR UPDATE locking. Production concurrency is not proven. |
| Authentication | JWT and bearer headers | Django server-side sessions and cookies | JSON APIs require an existing authenticated session; no JWT issuance endpoint. |
| Password hashing | bcrypt cost >=10 (SEC-REQ-1) | Default Django PBKDF2 | Salted one-way hashes exist, but the specified algorithm is not implemented. |
| Payment | Third-party sandbox confirmation before ledger update | Admin records cash or online payment with supplied reference | No external charge/verification, callbacks, decline handling or gateway integration. FR-10 recording exists; gateway interface remains absent. |
| API contract | REST endpoints for all main workflows | Supplementary /api/v1 and /api/v2 resources; most writes via HTML | Original endpoint paths, auth and expected HTTP statuses do not describe the deployed code. v1 leaves supports GET only. |
| Notification | Separate service with push delivery | Database notifications read on home-page load | No WebSocket/push server; existing leave test checks creation timing, not live delivery to an idle browser. |
| Registration (FR-1) | Name, roll number, department, contact number and email | Username, first/last name, email, block and password | Department/contact fields are absent; username is the login identifier, not a dedicated roll-number field. |
| Complaint validation (FR-5) | 10-500 characters | HTML form matches; JSON API accepts >=5 without the same maximum check | API acceptance differs from the baseline; not corrected in this task. |
| HTTPS (SEC-REQ-3) | TLS >=1.2; reject HTTP at API boundary | Production-mode redirect/secure cookies/HSTS; local HTTP | No provisioned TLS endpoint or negotiation evidence; redirect differs from rejection. |
| Security architecture | Gateway schema validation, rate limiting, immutable audit store | Form/view validation, template escaping, known-account lockout, model-level audit restrictions | No general per-IP gateway limiter; some session-authenticated JSON writes are CSRF exempt; bulk ORM/direct DB access bypasses instance-level audit restrictions. |
| Error handling | REST conflicts, gateway errors, correlation-ID middleware | Form errors/redirects and JSON helper errors | Original universal 409/423/402 and correlation-ID guarantees do not apply. |
| Durability testing | Server-restart resilience | Connection-close/re-query tests | Supports persistence checks; does not establish process-crash or power-loss recovery. |
| Non-functional evidence | Measurable load, browser, usability and availability targets | Scripts and automated checks; incomplete operational/manual evidence | Report unverified criteria as pending, not passed. |

## Demo explanation
Show the current Django workflows and versioned JSON API. Explain that the simplified architecture makes the local academic demonstration easier to run, while independent scaling, gateway integration and several deployment/acceptance guarantees remain outside the implemented snapshot. Refer to the validation report for measured versus unverified results. The technology substitution itself is not evidence that all original requirements are satisfied.
