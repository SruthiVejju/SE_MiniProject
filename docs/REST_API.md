# Versioned REST API Specification (NFR-8)

## 1. Overview
In accordance with **NFR-8** from the Software Requirements Specification (SRS) and Section 4.2 of the Software Architecture & Design Specification (SAD):
> *The system shall expose a versioned, documented REST API returning JSON, so that a new API version does not break existing client integrations.*

The Hostel Management System exposes versioned REST APIs under `/api/v1/` and `/api/v2/`.

---

## 2. API Design & Versioning Strategy

### 2.1 URI Path Versioning
API endpoints are segregated by major version paths (`/api/v1/` and `/api/v2/`).
- **Backward Compatibility**: Any addition, modification, or redesign of resource structures is introduced in a new API version path without altering existing version paths.
- **Contract Stability**: Existing client integrations communicating with `/api/v1/` continue functioning without disruption even when `/api/v2/` is released.

### 2.2 Content-Type and Status Codes
- All responses return `Content-Type: application/json` (except PDF report downloads requesting `format=pdf`).
- Standard HTTP status codes are returned:
  - `200 OK`: Request succeeded.
  - `201 Created`: Resource successfully created.
  - `400 Bad Request`: Input validation failure or malformed JSON payload.
  - `401 Unauthorized`: Authentication credentials missing or invalid.
  - `403 Forbidden`: Access denied due to Role-Based Access Control (RBAC).
  - `404 Not Found`: Resource does not exist.
  - `405 Method Not Allowed`: HTTP method not supported for endpoint.

---

## 3. Endpoints Catalogue

### 3.1 Common & Health
- **`GET /api/v1/health/`**: Health status check.
  - Response: `{"status": "healthy", "version": "1.0"}`

### 3.2 Hostel Rooms & Occupancy (FR-12)
- **`GET /api/v1/rooms/`**: List all rooms and beds with occupancy status. Requires authentication.
- **`GET /api/v1/reports/occupancy/`**: Generate real-time occupancy metrics (total rooms, total beds, occupied beds, vacant beds, occupancy rate %). Requires `Admin` role.
  - Optional: `?format=pdf` exports report directly as a downloadable PDF (`Content-Type: application/pdf`).

### 3.3 Notices & Announcements (FR-11)
- **`GET /api/v1/notices/`**: List notices visible to caller.
  - Students only receive notices matching their hostel block or general notices.
  - Admins and Wardens receive all notices.
- **`POST /api/v1/notices/`**: Publish a new notice. Requires `Admin` role.
  - Request body:
    ```json
    {
      "title": "Maintenance Notice",
      "content": "Water maintenance scheduled for Saturday.",
      "target_block": "A"
    }
    ```
- **`GET /api/v1/notices/{id}/`**: Retrieve details of a specific notice. Enforces audience visibility restrictions.

### 3.4 Maintenance Complaints (FR-5, NFR-7)
- **`GET /api/v1/complaints/`**: List complaints. Students see their own complaints; Wardens see complaints from their assigned block.
- **`POST /api/v1/complaints/`**: Submit a new maintenance complaint. Requires `Student` role. Enforces transactional durability (NFR-7) before returning `201 Created`.
  - Request body:
    ```json
    {
      "category": "electrical",
      "description": "Ceiling light flickering in room 102."
    }
    ```

### 3.5 Student Leave Requests (FR-7, NFR-7)
- **`GET /api/v1/leaves/`**: Retrieve leave requests.

### 3.6 Student Fee Dues (FR-4)
- **`GET /api/v1/fees/dues/`**: Retrieve outstanding fee dues for the authenticated student.

---

## 4. API v2 Evolution (Metadata Envelope)
API v2 introduces an envelope pattern for resource collections while preserving flat schemas in v1:
- **`GET /api/v2/rooms/`**: Enveloped response with `meta` (total rooms, total beds, occupied beds, vacant beds) and `data`.
- **`GET /api/v2/notices/`**: Enveloped response with `meta` (total count, user role, timestamp) and `data`.
- **`GET /api/v2/reports/occupancy/`**: Enveloped summary and per-block metrics.
