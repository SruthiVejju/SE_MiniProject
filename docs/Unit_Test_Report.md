# Unit Test Report

Date: 19 November 2026 (Asia/Kolkata). Baseline commit: `b77ab83`. Application code unchanged for this reporting task. Local Windows environment: Python 3.12.4, Django 6.1.3, Coverage.py 7.17.2, SQLite 3.45.3. Django used its isolated in-memory SQLite test database, not the project's existing database.

## 1. Result and Scope
**PASS: 145/145 Django tests plus 7/7 standalone availability-tool tests. Zero failures, errors or skips.** Django duration: 163.993 seconds. Availability-tool duration: 0.003 seconds. Django system check: no issues.

The inherited Django suite contains unit, ORM, view and integration checks; the total is not 145 isolated unit tests. Availability calculations use synthetic records. No application code or test definitions were changed.

## 2. Reproduction and Evidence
```powershell
$env:COVERAGE_FILE = (Join-Path (Get-Location) 'docs/test_evidence/.coverage')
.\venv\Scripts\python.exe -m coverage run --branch manage.py test --verbosity 2
.\venv\Scripts\python.exe -m coverage json -o docs/test_evidence/coverage.json
.\venv\Scripts\python.exe -m coverage report
.\venv\Scripts\python.exe -m unittest test_availability -v
```

[Raw Django log](test_evidence/django-tests.txt), [availability log](test_evidence/availability-tests.txt), [coverage JSON](test_evidence/coverage.json). Availability-tool tests ran separately and are outside the configured coverage scope.

## 3. Test Class Summary
| Class | Executed | Passed |
|---|---:|---:|
| `api.tests.VersionedAPITests` | 9 | 9 |
| `complaints.tests.ComplaintManagementTests` | 10 | 10 |
| `complaints.tests.ComplaintSubmissionTests` | 11 | 11 |
| `complaints.tests.ComplaintUsabilityTests` | 4 | 4 |
| `core.test_audit.AuditLogIntegrationTests` | 7 | 7 |
| `core.test_audit.AuditLogModelTests` | 3 | 3 |
| `core.test_frontend.FrontendCompatibilityTests` | 3 | 3 |
| `core.test_nfr7_durability.NFR7RequestDurabilityTests` | 2 | 2 |
| `core.test_security.HTTPSecurityTests` | 3 | 3 |
| `core.tests.HomeAndNotificationTests` | 6 | 6 |
| `core.tests.LoginAndLockoutTests` | 6 | 6 |
| `core.tests.SanitizeTests` | 5 | 5 |
| `core.tests.SecurityHeaderTests` | 2 | 2 |
| `core.tests.StudentRegistrationTests` | 3 | 3 |
| `fees.tests.FeeTests` | 9 | 9 |
| `hostel.test_occupancy_report.OccupancyReportTests` | 4 | 4 |
| `hostel.tests.RoomAllocationTests` | 10 | 10 |
| `hostel.tests.StudentDashboardTests` | 8 | 8 |
| `leaves.tests.DecideLeaveTests` | 9 | 9 |
| `leaves.tests.SubmitLeaveTests` | 10 | 10 |
| `notices.tests.NoticeTests` | 5 | 5 |
| `test_availability.AvailabilityTests` | 14 | 14 |
| `visitors.tests.VisitorTests` | 9 | 9 |

## 4. Limits
Passing tests establishes the assertions exercised, not complete SRS acceptance. Real browser testing, participant usability, target-load measurements, full-month uptime, an external payment sandbox and deployed TLS negotiation were not performed. Connection teardown is not an operating-system crash. See [System Validation Report](System_Validation_Report.md).

## 5. Complete Executed Test Inventory
All entries below passed in the recorded run.

| Class / method | Result |
|---|---|
| `api.tests.VersionedAPITests.test_api_roots_and_health` | PASS |
| `api.tests.VersionedAPITests.test_complaints_api_v1` | PASS |
| `api.tests.VersionedAPITests.test_fees_dues_api` | PASS |
| `api.tests.VersionedAPITests.test_notices_api_lifecycle` | PASS |
| `api.tests.VersionedAPITests.test_occupancy_report_api` | PASS |
| `api.tests.VersionedAPITests.test_rbac_denial_returns_json_403` | PASS |
| `api.tests.VersionedAPITests.test_rooms_api_v1` | PASS |
| `api.tests.VersionedAPITests.test_unauthenticated_requests_return_json_401` | PASS |
| `api.tests.VersionedAPITests.test_versioning_backward_compatibility_v1_and_v2` | PASS |
| `complaints.tests.ComplaintManagementTests.test_anonymous_user_cannot_access_warden_dashboard` | PASS |
| `complaints.tests.ComplaintManagementTests.test_invalid_status_is_rejected` | PASS |
| `complaints.tests.ComplaintManagementTests.test_non_warden_cannot_access_warden_dashboard` | PASS |
| `complaints.tests.ComplaintManagementTests.test_update_requires_post` | PASS |
| `complaints.tests.ComplaintManagementTests.test_warden_can_change_status_to_in_progress` | PASS |
| `complaints.tests.ComplaintManagementTests.test_warden_can_keep_optional_remark_empty` | PASS |
| `complaints.tests.ComplaintManagementTests.test_warden_can_mark_complaint_resolved` | PASS |
| `complaints.tests.ComplaintManagementTests.test_warden_can_view_another_block_after_login` | PASS |
| `complaints.tests.ComplaintManagementTests.test_warden_cannot_update_other_blocks_complaint` | PASS |
| `complaints.tests.ComplaintManagementTests.test_warden_sees_only_complaints_from_assigned_block` | PASS |
| `complaints.tests.ComplaintSubmissionTests.test_all_valid_categories_are_accepted` | PASS |
| `complaints.tests.ComplaintSubmissionTests.test_anonymous_user_is_redirected_to_login` | PASS |
| `complaints.tests.ComplaintSubmissionTests.test_description_longer_than_500_characters_is_rejected` | PASS |
| `complaints.tests.ComplaintSubmissionTests.test_description_of_exactly_10_characters_is_accepted` | PASS |
| `complaints.tests.ComplaintSubmissionTests.test_description_of_exactly_500_characters_is_accepted` | PASS |
| `complaints.tests.ComplaintSubmissionTests.test_description_shorter_than_10_characters_is_rejected` | PASS |
| `complaints.tests.ComplaintSubmissionTests.test_each_complaint_receives_a_unique_id` | PASS |
| `complaints.tests.ComplaintSubmissionTests.test_get_displays_complaint_form` | PASS |
| `complaints.tests.ComplaintSubmissionTests.test_invalid_category_is_rejected` | PASS |
| `complaints.tests.ComplaintSubmissionTests.test_only_students_can_submit_complaints` | PASS |
| `complaints.tests.ComplaintSubmissionTests.test_valid_complaint_is_saved` | PASS |
| `complaints.tests.ComplaintUsabilityTests.test_form_explains_description_length` | PASS |
| `complaints.tests.ComplaintUsabilityTests.test_form_has_clear_heading_and_instructions` | PASS |
| `complaints.tests.ComplaintUsabilityTests.test_form_has_example_description` | PASS |
| `complaints.tests.ComplaintUsabilityTests.test_success_page_shows_complaint_id_and_next_steps` | PASS |
| `core.test_audit.AuditLogIntegrationTests.test_audit_log_view_rbac` | PASS |
| `core.test_audit.AuditLogIntegrationTests.test_fee_payment_creates_audit_log` | PASS |
| `core.test_audit.AuditLogIntegrationTests.test_login_failure_creates_audit_log` | PASS |
| `core.test_audit.AuditLogIntegrationTests.test_login_failure_unknown_user_creates_audit_log` | PASS |
| `core.test_audit.AuditLogIntegrationTests.test_login_success_creates_audit_log` | PASS |
| `core.test_audit.AuditLogIntegrationTests.test_logout_creates_audit_log` | PASS |
| `core.test_audit.AuditLogIntegrationTests.test_room_allocation_creates_audit_log` | PASS |
| `core.test_audit.AuditLogModelTests.test_audit_log_cannot_be_deleted` | PASS |
| `core.test_audit.AuditLogModelTests.test_audit_log_is_append_only_cannot_update` | PASS |
| `core.test_audit.AuditLogModelTests.test_create_audit_entry_with_retention` | PASS |
| `core.test_nfr7_durability.NFR7RequestDurabilityTests.test_complaint_persisted_before_acknowledgment_and_survives_restart` | PASS |
| `core.test_nfr7_durability.NFR7RequestDurabilityTests.test_leave_request_persisted_before_acknowledgment_and_survives_restart` | PASS |
| `core.tests.HomeAndNotificationTests.test_home_requires_login` | PASS |
| `core.tests.HomeAndNotificationTests.test_home_shows_notifications_escaped` | PASS |
| `core.tests.HomeAndNotificationTests.test_mark_read` | PASS |
| `core.tests.HomeAndNotificationTests.test_mark_read_get_does_nothing` | PASS |
| `core.tests.HomeAndNotificationTests.test_str_methods` | PASS |
| `core.tests.HomeAndNotificationTests.test_user_without_profile_is_forbidden_on_role_views` | PASS |
| `core.tests.LoginAndLockoutTests.test_correct_password_rejected_during_lockout` | PASS |
| `core.tests.LoginAndLockoutTests.test_five_failed_attempts_lock_account` | PASS |
| `core.tests.LoginAndLockoutTests.test_invalid_password_increments_attempts` | PASS |
| `core.tests.LoginAndLockoutTests.test_logout` | PASS |
| `core.tests.LoginAndLockoutTests.test_successful_login` | PASS |
| `core.tests.LoginAndLockoutTests.test_successful_login_resets_attempts` | PASS |
| `core.tests.SanitizeTests.test_length_validation` | PASS |
| `core.tests.SanitizeTests.test_none_is_empty` | PASS |
| `core.tests.SanitizeTests.test_removes_control_chars_and_collapses_whitespace` | PASS |
| `core.tests.SanitizeTests.test_removes_event_handlers_and_js_scheme` | PASS |
| `core.tests.SanitizeTests.test_strips_script_tags` | PASS |
| `core.tests.SecurityHeaderTests.test_admin_site_has_no_csp` | PASS |
| `core.tests.SecurityHeaderTests.test_headers_present_on_app_pages` | PASS |
| `core.tests.StudentRegistrationTests.test_registration_rejects_duplicate_email` | PASS |
| `core.tests.StudentRegistrationTests.test_registration_rejects_password_mismatch` | PASS |
| `core.tests.StudentRegistrationTests.test_successful_registration` | PASS |
| `fees.tests.FeeTests.test_cash_payment_updates_fee_record_and_issues_receipt` | PASS |
| `fees.tests.FeeTests.test_non_positive_amount_rejected` | PASS |
| `fees.tests.FeeTests.test_online_payment_requires_reference` | PASS |
| `fees.tests.FeeTests.test_online_payment_with_reference` | PASS |
| `fees.tests.FeeTests.test_overpayment_rejected` | PASS |
| `fees.tests.FeeTests.test_receipt_numbers_unique` | PASS |
| `fees.tests.FeeTests.test_receipt_page_and_access_control` | PASS |
| `fees.tests.FeeTests.test_reference_rejects_special_characters` | PASS |
| `fees.tests.FeeTests.test_service_rejects_non_positive_amount` | PASS |
| `hostel.test_occupancy_report.OccupancyReportTests.test_occupancy_data_calculation_and_matching_allocations` | PASS |
| `hostel.test_occupancy_report.OccupancyReportTests.test_occupancy_report_html_view` | PASS |
| `hostel.test_occupancy_report.OccupancyReportTests.test_occupancy_report_pdf_download` | PASS |
| `hostel.test_occupancy_report.OccupancyReportTests.test_pdf_generation` | PASS |
| `hostel.tests.RoomAllocationTests.test_admin_can_access_allocation_page` | PASS |
| `hostel.tests.RoomAllocationTests.test_admin_can_allocate_available_bed` | PASS |
| `hostel.tests.RoomAllocationTests.test_admin_can_allocate_using_form` | PASS |
| `hostel.tests.RoomAllocationTests.test_allocated_bed_removed_from_available_choices` | PASS |
| `hostel.tests.RoomAllocationTests.test_allocation_is_associated_with_correct_student` | PASS |
| `hostel.tests.RoomAllocationTests.test_duplicate_room_is_rejected` | PASS |
| `hostel.tests.RoomAllocationTests.test_non_admin_cannot_access_allocation_page` | PASS |
| `hostel.tests.RoomAllocationTests.test_occupied_bed_cannot_be_allocated_again` | PASS |
| `hostel.tests.RoomAllocationTests.test_student_cannot_receive_two_active_beds` | PASS |
| `hostel.tests.RoomAllocationTests.test_warden_cannot_be_allocated_a_bed` | PASS |
| `hostel.tests.StudentDashboardTests.test_admin_cannot_access_student_dashboard` | PASS |
| `hostel.tests.StudentDashboardTests.test_dashboard_displays_correct_fee_dues` | PASS |
| `hostel.tests.StudentDashboardTests.test_dashboard_uses_limited_database_queries` | PASS |
| `hostel.tests.StudentDashboardTests.test_student_can_view_own_dashboard` | PASS |
| `hostel.tests.StudentDashboardTests.test_student_cannot_view_another_students_allocation` | PASS |
| `hostel.tests.StudentDashboardTests.test_student_without_allocation_can_view_dashboard` | PASS |
| `hostel.tests.StudentDashboardTests.test_student_without_fee_account_can_view_dashboard` | PASS |
| `hostel.tests.StudentDashboardTests.test_unauthenticated_user_is_redirected_to_login` | PASS |
| `leaves.tests.DecideLeaveTests.test_approve_saves_decision_and_notifies_within_a_minute` | PASS |
| `leaves.tests.DecideLeaveTests.test_cannot_decide_twice` | PASS |
| `leaves.tests.DecideLeaveTests.test_get_not_allowed` | PASS |
| `leaves.tests.DecideLeaveTests.test_invalid_action_ignored` | PASS |
| `leaves.tests.DecideLeaveTests.test_other_block_warden_forbidden` | PASS |
| `leaves.tests.DecideLeaveTests.test_pending_list_scoped_to_block` | PASS |
| `leaves.tests.DecideLeaveTests.test_reject` | PASS |
| `leaves.tests.DecideLeaveTests.test_str` | PASS |
| `leaves.tests.DecideLeaveTests.test_student_cannot_decide` | PASS |
| `leaves.tests.SubmitLeaveTests.test_my_requests_only_lists_own` | PASS |
| `leaves.tests.SubmitLeaveTests.test_only_students_can_submit` | PASS |
| `leaves.tests.SubmitLeaveTests.test_past_from_date_rejected` | PASS |
| `leaves.tests.SubmitLeaveTests.test_required_fields` | PASS |
| `leaves.tests.SubmitLeaveTests.test_short_reason_rejected` | PASS |
| `leaves.tests.SubmitLeaveTests.test_sql_injection_treated_as_data` | PASS |
| `leaves.tests.SubmitLeaveTests.test_student_without_warden_still_stored` | PASS |
| `leaves.tests.SubmitLeaveTests.test_to_before_from_rejected` | PASS |
| `leaves.tests.SubmitLeaveTests.test_valid_request_stored_and_routed_to_block_warden` | PASS |
| `leaves.tests.SubmitLeaveTests.test_xss_payload_sanitised_and_escaped` | PASS |
| `notices.tests.NoticeTests.test_admin_can_publish_block_specific_notice` | PASS |
| `notices.tests.NoticeTests.test_admin_can_publish_general_notice` | PASS |
| `notices.tests.NoticeTests.test_notice_search` | PASS |
| `notices.tests.NoticeTests.test_student_cannot_publish_notice` | PASS |
| `notices.tests.NoticeTests.test_student_visibility_rules` | PASS |
| `visitors.tests.VisitorTests.test_entry_recorded_with_automatic_timestamp` | PASS |
| `visitors.tests.VisitorTests.test_exit_timestamp_captured` | PASS |
| `visitors.tests.VisitorTests.test_exit_twice_keeps_first_time` | PASS |
| `visitors.tests.VisitorTests.test_host_must_be_student` | PASS |
| `visitors.tests.VisitorTests.test_list_shows_visitors` | PASS |
| `visitors.tests.VisitorTests.test_missing_fields_rejected` | PASS |
| `visitors.tests.VisitorTests.test_only_security_guard_allowed` | PASS |
| `visitors.tests.VisitorTests.test_sql_injection_in_purpose_is_data` | PASS |
| `visitors.tests.VisitorTests.test_xss_in_name_sanitised` | PASS |
| `core.test_frontend.FrontendCompatibilityTests.test_base_template_declares_doctype_charset_and_viewport` | PASS |
| `core.test_frontend.FrontendCompatibilityTests.test_css_avoids_browser_specific_prefixes` | PASS |
| `core.test_frontend.FrontendCompatibilityTests.test_no_inline_scripts_or_styles` | PASS |
| `core.test_security.HTTPSecurityTests.test_http_request_redirects_to_https` | PASS |
| `core.test_security.HTTPSecurityTests.test_https_request_is_allowed` | PASS |
| `core.test_security.HTTPSecurityTests.test_security_settings_are_enabled` | PASS |
| `test_availability.AvailabilityTests.test_100_percent_availability` | PASS |
| `test_availability.AvailabilityTests.test_downtime_reduces_availability` | PASS |
| `test_availability.AvailabilityTests.test_duplicate_timestamps_do_not_count_as_uptime` | PASS |
| `test_availability.AvailabilityTests.test_incomplete_month_sample_does_not_claim_full_coverage` | PASS |
| `test_availability.AvailabilityTests.test_insufficient_records` | PASS |
| `test_availability.AvailabilityTests.test_long_monitoring_gap_is_not_counted` | PASS |
| `test_availability.AvailabilityTests.test_planned_maintenance_is_excluded` | PASS |
| `test_availability.AvailabilityTests.test_100_percent_availability` | PASS |
| `test_availability.AvailabilityTests.test_downtime_reduces_availability` | PASS |
| `test_availability.AvailabilityTests.test_duplicate_timestamps_do_not_count_as_uptime` | PASS |
| `test_availability.AvailabilityTests.test_incomplete_month_sample_does_not_claim_full_coverage` | PASS |
| `test_availability.AvailabilityTests.test_insufficient_records` | PASS |
| `test_availability.AvailabilityTests.test_long_monitoring_gap_is_not_counted` | PASS |
| `test_availability.AvailabilityTests.test_planned_maintenance_is_excluded` | PASS |
