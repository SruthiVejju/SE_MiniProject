"""
Tests for NFR-7: Preserve Submitted Requests After Restart.
Validates:
1. Submissions are saved to durable storage before success is acknowledged to the client.
2. Submitted complaints and leave requests remain available after database/server restart.
"""
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.db import connection, connections
from django.test import Client, TestCase
from django.urls import reverse

from complaints.models import Complaint
from core.models import UserProfile
from leaves.models import LeaveRequest

User = get_user_model()


class NFR7RequestDurabilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'Pass@12345'

        # Student user
        self.student = User.objects.create_user(username='durability_student', password=self.password)
        self.profile = UserProfile.objects.create(
            user=self.student,
            role=UserProfile.STUDENT,
            block='A'
        )

        # Warden user for block A
        self.warden = User.objects.create_user(username='durability_warden', password=self.password)
        UserProfile.objects.create(
            user=self.warden,
            role=UserProfile.WARDEN,
            block='A'
        )

        self.client.login(username='durability_student', password=self.password)

    def simulate_server_restart(self):
        """Simulate a cold process/server restart by forcefully dropping all connections."""
        connections.close_all()

    def test_complaint_persisted_before_acknowledgment_and_survives_restart(self):
        payload = {
            'category': Complaint.ELECTRICAL,
            'description': 'Ceiling fan in room 101 stopped working and makes a buzzing noise.',
        }

        # 1. Client submits request
        response = self.client.post(reverse('complaint-submit'), payload)
        # Client receives acknowledgment (200 success page)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complaint Submitted')

        # 2. Verify persisted in database immediately before acknowledgment
        complaint = Complaint.objects.filter(student=self.student).first()
        self.assertIsNotNone(complaint)
        self.assertEqual(complaint.category, Complaint.ELECTRICAL)
        self.assertEqual(complaint.description, payload['description'])
        self.assertEqual(complaint.status, Complaint.OPEN)
        complaint_uuid = complaint.complaint_id

        # 3. Simulate sudden server / process restart
        self.simulate_server_restart()

        # 4. Verify request remains completely intact in durable storage after restart
        reloaded = Complaint.objects.get(complaint_id=complaint_uuid)
        self.assertEqual(reloaded.student.username, 'durability_student')
        self.assertEqual(reloaded.category, Complaint.ELECTRICAL)
        self.assertEqual(reloaded.description, payload['description'])
        self.assertEqual(reloaded.status, Complaint.OPEN)

    def test_leave_request_persisted_before_acknowledgment_and_survives_restart(self):
        start_date = date.today() + timedelta(days=2)
        end_date = start_date + timedelta(days=3)

        payload = {
            'destination': 'Home Town',
            'from_date': start_date.isoformat(),
            'to_date': end_date.isoformat(),
            'reason': 'Attending sibling marriage ceremony with family.',
        }

        # 1. Client submits leave request
        response = self.client.post(reverse('leave-submit'), payload)
        # Acknowledgment is redirect to my-requests with success message
        self.assertEqual(response.status_code, 302)

        # 2. Verify persisted before client acknowledgment
        leave = LeaveRequest.objects.filter(student=self.student).first()
        self.assertIsNotNone(leave)
        self.assertEqual(leave.destination, 'Home Town')
        self.assertEqual(leave.status, LeaveRequest.PENDING)
        self.assertEqual(leave.block, 'A')
        leave_id = leave.pk

        # 3. Simulate sudden server restart
        self.simulate_server_restart()

        # 4. Verify request remains completely intact in durable storage after restart
        reloaded_leave = LeaveRequest.objects.get(pk=leave_id)
        self.assertEqual(reloaded_leave.student.username, 'durability_student')
        self.assertEqual(reloaded_leave.destination, 'Home Town')
        self.assertEqual(reloaded_leave.from_date, start_date)
        self.assertEqual(reloaded_leave.to_date, end_date)
        self.assertEqual(reloaded_leave.status, LeaveRequest.PENDING)
