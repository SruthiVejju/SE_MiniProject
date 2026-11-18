# Security Requirement 5 (SEC-REQ-5): Append-Only Audit Logging

## 1. Overview
In compliance with **SEC-REQ-5** from the Software Requirements Specification (SRS) and the Software Architecture & Design Specification (SAD Section 3.2, 3.5, and 4.3):
> *The system shall record all authentication events (success and failure) and administrative actions (fee edits, room allocation changes) in an append-only audit log retained for a minimum of one year.*

The Hostel Management System (HMS) provides a centralized, immutable audit log store implemented via the `AuditLog` model in the `core` app and managed through `core/audit.py`.

---

## 2. Architecture & Design

### 2.1 Audit Log Model Structure
The `AuditLog` model captures:
- `timestamp`: UTC datetime of the event (`DateTimeField`, indexed).
- `action`: Standardized event action string (`CharField`, indexed).
- `actor`: Foreign key to `auth.User` (nullable to handle failed logins by non-existent users).
- `actor_username`: Captured username string at time of event.
- `ip_address`: Client IP address extracted safely from headers (`GenericIPAddressField`).
- `details`: Context-specific JSON metadata dictionary (`JSONField`).
- `retention_until`: Expiration cutoff date, automatically set to `timestamp + 365 days` (1 year minimum retention).

### 2.2 Append-Only Guarantees & Immutability
To guarantee that audit trails cannot be altered or purged through normal application operations:
1. **Model-level Immutability**:
   - Calling `.save()` on an existing entry (`pk is not None`) raises a `PermissionError`.
   - Calling `.delete()` on an entry raises a `PermissionError`.
2. **Administrative Access Restrictions**:
   - In Django Admin (`AuditLogAdmin`), `has_add_permission`, `has_change_permission`, and `has_delete_permission` all return `False`.
   - The admin interface is strictly read-only.
3. **Role-Based Access Control**:
   - The `/audit/` web dashboard view is guarded by `@role_required(UserProfile.ADMIN)`. Students, wardens, and unauthorized users receive `403 Forbidden` or redirect.

---

## 3. Audited Event Actions

| Action Identifier | Category | Trigger / Context |
|---|---|---|
| `auth.login.success` | Authentication | Successful user login with valid credentials. |
| `auth.login.failed` | Authentication | Failed login attempt (invalid credentials, unknown username, or locked account). |
| `auth.logout` | Authentication | Explicit user logout. |
| `hostel.allocation.created` | Admin Action | Bed allocation created for a student by an administrator. |
| `hostel.allocation.deactivated` | Admin Action | Bed allocation deactivated or cancelled. |
| `fees.payment.recorded` | Admin Action | Fee payment recorded by an administrator with unique receipt generation. |
| `notices.notice.published` | Admin Action | Announcement/notice published by an administrator. |

---

## 4. Retention Policy & Verification
All audit records automatically calculate `retention_until = timestamp + timedelta(days=365)`.
Compliance can be verified programmatically using `core.audit.verify_audit_retention()`, which checks that all audit entries satisfy the 365-day retention requirement.
