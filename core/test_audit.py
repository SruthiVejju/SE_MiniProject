"""
Tests for SEC-REQ-5: Append-only Audit Log.
"""
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from core.audit import (
    AUTH_LOGIN_FAILED,
    AUTH_LOGIN_SUCCESS,
    AUTH_LOGOUT,
    FEE_PAYMENT_RECORDED,
    ROOM_ALLOCATION_CREATED,
    log_audit_event,
    verify_audit_retention,
)
from core.models import AuditLog, UserProfile
from fees.models import FeeAccount
from fees.services import record_payment
from hostel.models import Bed, Room
from hostel.services import allocate_bed

User = get_user_model()


class AuditLogModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='audituser', password='password123')

    def test_create_audit_entry_with_retention(self):
        entry = log_audit_event(
            AUTH_LOGIN_SUCCESS,
            actor=self.user,
            details={'ip': '127.0.0.1'}
        )
        self.assertIsNotNone(entry)
        self.assertEqual(entry.action, AUTH_LOGIN_SUCCESS)
        self.assertEqual(entry.actor, self.user)
        self.assertEqual(entry.actor_username, 'audituser')
        self.assertIsNotNone(entry.retention_until)
        # Verify retention is at least 365 days
        diff = entry.retention_until - entry.timestamp
        self.assertGreaterEqual(diff.total_seconds(), 364 * 86400)
        self.assertTrue(verify_audit_retention())

    def test_audit_log_is_append_only_cannot_update(self):
        entry = log_audit_event('test.action', actor=self.user)
        self.assertIsNotNone(entry.pk)
        entry.action = 'modified.action'
        with self.assertRaises(PermissionError):
            entry.save()

    def test_audit_log_cannot_be_deleted(self):
        entry = log_audit_event('test.action', actor=self.user)
        with self.assertRaises(PermissionError):
            entry.delete()


class AuditLogIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'Pass@12345'
        self.student_user = User.objects.create_user(username='student1', password=self.password)
        UserProfile.objects.create(user=self.student_user, role=UserProfile.STUDENT, block='A')

        self.admin_user = User.objects.create_user(username='admin1', password=self.password)
        UserProfile.objects.create(user=self.admin_user, role=UserProfile.ADMIN)

    def test_login_success_creates_audit_log(self):
        res = self.client.post(reverse('login'), {'username': 'student1', 'password': self.password})
        self.assertEqual(res.status_code, 302)
        log = AuditLog.objects.filter(action=AUTH_LOGIN_SUCCESS, actor_username='student1').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.student_user)

    def test_login_failure_creates_audit_log(self):
        res = self.client.post(reverse('login'), {'username': 'student1', 'password': 'wrongpassword'})
        self.assertEqual(res.status_code, 200)
        log = AuditLog.objects.filter(action=AUTH_LOGIN_FAILED, actor_username='student1').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.details.get('locked'), False)

    def test_login_failure_unknown_user_creates_audit_log(self):
        res = self.client.post(reverse('login'), {'username': 'unknown_person', 'password': 'randompassword'})
        self.assertEqual(res.status_code, 200)
        log = AuditLog.objects.filter(action=AUTH_LOGIN_FAILED, actor_username='unknown_person').first()
        self.assertIsNotNone(log)
        self.assertIsNone(log.actor)

    def test_logout_creates_audit_log(self):
        self.client.login(username='student1', password=self.password)
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, 302)
        log = AuditLog.objects.filter(action=AUTH_LOGOUT, actor_username='student1').first()
        self.assertIsNotNone(log)

    def test_fee_payment_creates_audit_log(self):
        account = FeeAccount.objects.create(student=self.student_user, total_fee=Decimal('5000'))
        payment = record_payment(account.pk, Decimal('1500'), 'cash', '', self.admin_user)
        log = AuditLog.objects.filter(action=FEE_PAYMENT_RECORDED).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.admin_user)
        self.assertEqual(log.details['receipt_number'], payment.receipt_number)
        self.assertEqual(log.details['amount'], '1500')

    def test_room_allocation_creates_audit_log(self):
        room = Room.objects.create(block='A', room_number='101')
        bed = Bed.objects.create(room=room, bed_number='B1')
        alloc = allocate_bed(self.student_user, bed.pk, admin_user=self.admin_user)
        log = AuditLog.objects.filter(action=ROOM_ALLOCATION_CREATED).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.admin_user)
        self.assertEqual(log.details['student'], 'student1')
        self.assertEqual(log.details['bed_number'], 'B1')

    def test_audit_log_view_rbac(self):
        # Anonymous cannot access
        res = self.client.get(reverse('audit-logs'))
        self.assertEqual(res.status_code, 302)

        # Student cannot access (403)
        self.client.login(username='student1', password=self.password)
        res = self.client.get(reverse('audit-logs'))
        self.assertEqual(res.status_code, 403)

        # Admin can access
        self.client.login(username='admin1', password=self.password)
        res = self.client.get(reverse('audit-logs'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Security & Administrative Audit Logs')

        # Filter by action
        res = self.client.get(reverse('audit-logs') + f'?action={AUTH_LOGIN_SUCCESS}')
        self.assertEqual(res.status_code, 200)
