# Software Engineering Mini-Project

## TEAM H15 - Hostel Management System
- Shashank Vinayak - PES1UG24CS435
- Shubashtiha Gowtham - PES1UG24CS450
- Simran Joshi - PES1UG24CS455
- Sruthi Vejju - PES1UG24CS472

A web-based system to digitize hostel administration: student registration, room/bed allocation, fee collection, complaint handling, leave/outpass management, visitor logging, notices, and occupancy reporting.

## Part-1 Deliverables

| # | Deliverable | Document |
|---|---|---|
| 1 | Software Requirements Specification (IEEE 830) | [`docs/SRS.md`](docs/SRS.md) |
| 2 | Test Plan (IEEE 829), incl. 10 test cases and security validation | [`docs/Test_Plan.md`](docs/Test_Plan.md) |
| 3 | Software Architecture & Design Specification (IEEE 1016) | [`docs/Architecture_Design.md`](docs/Architecture_Design.md) |

## Diagrams

Rendered UML diagrams live in [`docs/diagrams/`](docs/diagrams/); their editable PlantUML sources are in [`docs/diagrams/src/`](docs/diagrams/src/).

- Use Case Diagram â€” `use-case-diagram.png`
- Component Diagram â€” `component-diagram.png`
- Sequence Diagrams â€” `sequence-login.png`, `sequence-room-allocation.png`, `sequence-fee-payment.png`

The four architecture/sequence PNGs and PlantUML sources can be regenerated from their shared definitions with:

```bash
python docs/diagrams/src/render_current_diagrams.py
```

This documentation-only renderer requires Pillow and uses Arial from Windows fonts. The unchanged use-case diagram retains its separate PlantUML source.

## Running the application

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Tests, coverage and security scan

```bash
coverage run manage.py test && coverage report   # fails below 70% (NFR-5)
bandit -r core leaves visitors fees config -x '*/tests.py,*/testutils.py' --severity-level high   # SEC-REQ-4
```

Cross-browser plan and results: [`docs/Cross_Browser_Test_Report.md`](docs/Cross_Browser_Test_Report.md).

## Final architecture and deviations

The implemented system is a Django modular monolith using server-rendered templates, SQLite and session authentication. The current [Architecture & Design Specification](docs/Architecture_Design.md) and [complete deviation record](docs/Design_Deviations.md) reconcile it with the original submitted design and identify remaining acceptance gaps.

## Final test reports

- [Unit Test Report](docs/Unit_Test_Report.md)
- [System Validation Report](docs/System_Validation_Report.md)
- [Code Coverage Report](docs/Code_Coverage_Report.md)
- [Branch Coverage Report](docs/Branch_Coverage_Report.md)
## Agile Project Management (Jira)

- **Live Jira Scrum Board**: [Hostel Management System Board](https://achalasreenath948.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog)
- **Total Story Points**: 99 SP across 3 Sprints and 8 Epics
- **Methodology**: Scrum with 2-week timeboxed sprints and Fibonacci estimation

### Team Workload Distribution

| Team Member | Roll Number | GitHub Handle | Assigned Scope | Story Points |
|---|---|---|---|---|
| **Sruthi Vejju** | PES1UG24CS472 | `@SruthiVejju` | Registration, Login & Lockout, RBAC, Password Hashing, Performance & Availability | **25 SP** |
| **Simran Joshi** | PES1UG24CS455 | `@joshi-simran` | Room Allocation, Dues View, Complaints System, Usability, 5k Scalability, HTTPS/TLS | **26 SP** |
| **Shashank Vinayak** | PES1UG24CS435 | `@shashankv2303` | Leave/Outpass, Visitor Logs, Fee Payments, 70% Test Gate, Cross-Browser, Input Scan | **25 SP** |
| **Shubashtiha Gowtham** | PES1UG24CS450 | `@shubashithagowtham-ship-it` | Notices Broadcast, Occupancy PDF Reports, Durability, Versioned REST API, Audit Log | **23 SP** |

### Sprints Overview
- **Sprint 1 (40 SP)**: Core Foundation, Basic Operations, Fee Payments, Security Baseline & 70% Coverage Gate
- **Sprint 2 (39 SP)**: Complaints Management, Notices, Occupancy PDF Export, Durability, REST API & Audit Logging
- **Sprint 3 (20 SP)**: Dashboard Load Testing (200 concurrent users), 99% Availability Monitoring & Usability Validation
