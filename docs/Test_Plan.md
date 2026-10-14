# Software Test Plan

---

## 1. Introduction

### 1.1 Purpose

This Test Plan defines the strategy, scope, resources, and schedule for verifying that the Hostel Management System (HMS) satisfies the functional, non-functional, and security requirements defined in the [Software Requirements Specification](SRS.md).

### 1.2 Scope

This plan covers system-level verification of the twelve functional requirements (FR-1..FR-12), the eight non-functional requirements (NFR-1..NFR-8), and the five security requirements (SEC-REQ-1..SEC-REQ-5) defined in the SRS. Unit testing internal to each service (targeting NFR-5's 70% coverage bar) is performed continuously by developers and is not itemized here; this plan focuses on system/acceptance-level test cases.

### 1.3 References

- [SRS.md](SRS.md) — Software Requirements Specification, v1.0.
- [Architecture_Design.md](Architecture_Design.md) — Software Architecture & Design Specification, v1.0.
- IEEE Std 829-2008.

### 1.4 Definitions, Acronyms, Abbreviations

| Term | Meaning |
|---|---|
| FR / NFR | Functional / Non-Functional Requirement (see SRS Section 3) |
| SEC-REQ | Security Requirement (see SRS Section 6.2) |
| RBAC | Role-Based Access Control |
| TC | Test Case |

---

## 2. Test Strategy Overview

### 2.1 Objectives

Confirm that each FR/NFR/SEC-REQ in the SRS is implemented correctly, that the system rejects invalid or malicious input safely, and that performance and usability targets are met before the mini-project is submitted for evaluation.

### 2.2 Test Levels

| Level | Performed By | Focus |
|---|---|---|
| Unit | Developers | Individual service functions (targets NFR-5) |
| Integration | Developers/Testers | Service-to-service and service-to-DB interaction |
| System | Testers | End-to-end use cases via the API/UI (this plan's focus) |
| Security | Testers | Input validation, RBAC, authentication hardening (Section 5.1) |

### 2.3 Roles and Responsibilities

| Role | Responsibility |
|---|---|
| Test Lead | Owns this plan, tracks execution and defects |
| Developer | Fixes defects, supports test data setup |
| Tester | Executes test cases, logs results |

### 2.4 Test Environment

A staging deployment of HMS (Web Client, API services, PostgreSQL) with seeded test data (sample students, hostel blocks, rooms/beds) and a sandboxed Payment Gateway. Load testing (TC-07) uses a load-generation tool capable of simulating 200 concurrent virtual users.

---

## 3. Features to be Tested / Not to be Tested

### 3.1 Features to be Tested

- Account registration and authentication (FR-1, FR-2)
- Room/bed allocation (FR-3)
- Allocation and dues viewing (FR-4)
- Complaint submission and management (FR-5, FR-6)
- Leave/outpass request and approval (FR-7, FR-8)
- Visitor entry/exit logging (FR-9)
- Fee payment recording (FR-10)
- Notices (FR-11) and occupancy reporting (FR-12)
- Performance, portability, and reliability targets (NFR-1, NFR-6, NFR-7)
- Security controls: password hashing, RBAC, TLS enforcement, input sanitization, audit logging (SEC-REQ-1..5)

### 3.2 Features Not to be Tested (This Phase)

- Mess-menu planning and inventory/asset management (out of scope per SRS Section 1.4).
- Multi-campus federation.
- Third-party Payment Gateway's own internal correctness (only the HMS-side integration is tested, using the gateway's sandbox).

---

## 4. Test Approach

### 4.1 Approach

Each functional and security test case is executed against the API (and, where relevant, the Web Client UI) using both valid ("happy path") and invalid/boundary inputs. Non-functional test cases use dedicated tooling (load generator for performance, multiple browsers for portability).

### 4.2 Entry Criteria

- The build under test deploys successfully to the staging environment.
- Test data (students, hostel blocks, rooms/beds) is seeded.

### 4.3 Exit / Item Pass-Fail Criteria

- A test case **passes** if the actual result matches the expected result exactly, including correct HTTP status codes and persisted data state.
- The overall test cycle **passes** if 100% of Security test cases (Section 5.1) pass with no high-severity findings, and at least 90% of Functional and Non-Functional test cases pass with no open Critical/High defects.

### 4.4 Suspension and Resumption Criteria

Testing is suspended if the staging environment becomes unavailable or if a Critical defect blocks execution of more than 30% of remaining test cases; it resumes once the blocking defect is fixed and redeployed.

---

## 5. Test Cases

### 5.1 Security Validation Test Cases

| TC ID | Title | Precondition | Steps | Expected Result | Traces To |
|---|---|---|---|---|---|
| TC-09 | RBAC — Student cannot access another student's fee record | Two registered students A and B, both logged in | 1. Log in as Student A. 2. Call `GET /api/students/{B_id}/allocation` using A's JWT. | Server responds `403 Forbidden`; no fee/allocation data for B is returned. | SEC-REQ-2 |
| TC-10 | Input sanitization — SQL injection / XSS on login | Login endpoint available | 1. Submit `POST /api/auth/login` with `rollNo = "' OR '1'='1"` and a script-tag payload in the password field. | Server responds `400`/`401` (not authenticated, no server error); payload is neither executed nor reflected unescaped; no unauthorized login occurs. | SEC-REQ-4 |

### 5.2 Functional Test Cases

| TC ID | Title | Precondition | Steps | Expected Result | Traces To |
|---|---|---|---|---|---|
| TC-01 | Duplicate registration is rejected | A student with roll number `PES1UG24CS001` already exists | 1. Submit `POST /api/auth/register` with the same roll number. | Server responds `400`/`409`; no duplicate account is created. | FR-1 |
| TC-02 | Successful room allocation | Student exists; Bed `B-101-1` is VACANT | 1. Admin submits `POST /api/allocations` for the student and bed. | Server responds `201 Created`; bed status becomes OCCUPIED; student's allocation is retrievable via FR-4 endpoint. | FR-3 |
| TC-03 | Allocation to an already-occupied bed is rejected | Bed `B-101-1` is already OCCUPIED (from TC-02) | 1. Admin submits `POST /api/allocations` for a different student on the same bed. | Server responds `409 Conflict`; original allocation is unchanged. | FR-3 |
| TC-04 | Complaint submission with valid description | Student is logged in | 1. Submit `POST /api/complaints` with category `Electrical` and a 50-character description. | Server responds `201 Created` with a unique complaint ID. | FR-5 |
| TC-05 | Warden updates complaint status | A complaint exists in `Open` status for the warden's block | 1. Warden submits `PATCH /api/complaints/{id}` with status `In-Progress` and a remark. | Server responds `200 OK`; complaint status is updated and visible to the student. | FR-6 |
| TC-06 | Cash fee payment generates a receipt | Student has an outstanding due balance | 1. Admin submits `POST /api/fees/payments` with mode `CASH` and a valid amount. | Server responds `201 Created` with a unique receipt number; the student's due balance decreases by the paid amount. | FR-10 |

### 5.3 Non-Functional Test Cases

| TC ID | Title | Precondition | Steps | Expected Result | Traces To |
|---|---|---|---|---|---|
| TC-07 | Dashboard response time under load | Staging environment seeded with 5,000 student accounts | 1. Simulate 200 concurrent virtual users requesting `GET /api/students/{id}/allocation`. 2. Measure response times. | 95% of requests complete within 2 seconds. | NFR-1, NFR-4 |
| TC-08 | Cross-browser rendering | Web client deployed to staging | 1. Load the Student dashboard on the latest two major versions of Chrome, Firefox, and Edge. | UI renders correctly and is fully functional on all six browser/version combinations. | NFR-6 |

---

## 6. Traceability Matrix

| SRS Requirement | Test Case(s) |
|---|---|
| FR-1 | TC-01 |
| FR-2 | TC-09 (RBAC/auth boundary), TC-10 (auth input hardening) |
| FR-3 | TC-02, TC-03 |
| FR-4 | TC-07 |
| FR-5 | TC-04 |
| FR-6 | TC-05 |
| FR-7, FR-8 | *(Planned for Part-2 execution cycle — see Section 8)* |
| FR-9, FR-11, FR-12 | *(Planned for Part-2 execution cycle — see Section 8)* |
| FR-10 | TC-06 |
| NFR-1, NFR-4 | TC-07 |
| NFR-6 | TC-08 |
| SEC-REQ-2 | TC-09 |
| SEC-REQ-4 | TC-10 |
| SEC-REQ-1, SEC-REQ-3, SEC-REQ-5 | *(Planned for Part-2 execution cycle — see Section 8)* |

---

## 7. Risks and Contingencies

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Payment Gateway sandbox unavailable during testing | Medium | Medium | Mock the gateway response for fee-payment test cases if the sandbox is down. |
| Load-testing tooling unavailable in the course environment | Medium | Low | Fall back to a smaller simulated concurrency (e.g., 20 users) and extrapolate, noting the deviation in the test report. |
| Test data conflicts across parallel test runs | Low | Medium | Reset/reseed the staging database before each test cycle. |

---

## 8. Test Deliverables & Schedule

| Deliverable | Due |
|---|---|
| This Test Plan | Part-1 (28 Sept 2026) |
| Test case execution log and defect report | Part-2 |
| Remaining test cases for FR-7, FR-8, FR-9, FR-11, FR-12, SEC-REQ-1, SEC-REQ-3, SEC-REQ-5 | Part-2, alongside implementation of those features |

---

## 9. Approvals

| Role | Name | Date |
|---|---|---|
| Test Lead | *(Project team)* | 28 Sept 2026 |
| Instructor / Evaluator | *(Pending review)* | — |
