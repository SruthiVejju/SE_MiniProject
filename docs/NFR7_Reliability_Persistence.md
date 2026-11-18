# Non-Functional Requirement 7 (NFR-7): Persistence and Reliability

## 1. Requirement Specification
From the Software Requirements Specification (SRS):
> **NFR-7 (Reliability):** *The system shall not lose any submitted complaint or leave request even if the server restarts, by persisting each submission to durable storage before acknowledging it to the client.*

## 2. Technical Implementation

### 2.1 Persistence-Before-Acknowledgment
HMS enforces transactional boundaries on all user submission endpoints:
1. **Complaints**: `complaints.views.submit_complaint` wraps database persistence in `with transaction.atomic():`. The model instance (`complaint.save()`) is committed to the relational database before the success view (`complaints/success.html`) is rendered and HTTP 200 is acknowledged.
2. **Leave Requests**: `leaves.services.submit_leave` is decorated with `@transaction.atomic`. The request is persisted and assigned to the relevant block warden before an HTTP 302 redirect acknowledges successful submission.

### 2.2 Crash Resilience & Restart Survival
Because database write operations are committed synchronously before acknowledging receipt to the HTTP client:
- An in-flight process crash or abrupt server restart will not cause lost or orphaned submissions.
- Once a client receives a `200 OK` or redirect acknowledgment, the corresponding request is guaranteed to exist in durable storage.

## 3. Verification
Automated test suite `core.test_nfr7_durability.NFR7RequestDurabilityTests` validates:
- Immediate database persistence before client acknowledgment.
- Durability across cold server/process restarts (simulated via database connection teardown `connections.close_all()`).
- Data integrity retention for all complaint and leave request fields.
