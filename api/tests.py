import json
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from complaints.models import Complaint
from core.models import UserProfile
from fees.models import FeeAccount
from hostel.models import Bed, Room
from notices.models import Notice

User = get_user_model()


class VersionedAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'Pass@12345'

        # Admin user
        self.admin = User.objects.create_user(username='api_admin', password=self.password)
        UserProfile.objects.create(user=self.admin, role=UserProfile.ADMIN)

        # Student user in Block A
        self.student = User.objects.create_user(username='api_student', password=self.password)
        UserProfile.objects.create(user=self.student, role=UserProfile.STUDENT, block='A')

        # Student user in Block B
        self.student_b = User.objects.create_user(username='api_student_b', password=self.password)
        UserProfile.objects.create(user=self.student_b, role=UserProfile.STUDENT, block='B')

        # Setup rooms
        self.room = Room.objects.create(block='A', room_number='A101', floor=1)
        self.bed1 = Bed.objects.create(room=self.room, bed_number='B1')
        self.bed2 = Bed.objects.create(room=self.room, bed_number='B2')

    def test_api_roots_and_health(self):
        res_v1 = self.client.get('/api/v1/')
        self.assertEqual(res_v1.status_code, 200)
        self.assertEqual(res_v1['Content-Type'], 'application/json')
        data_v1 = res_v1.json()
        self.assertEqual(data_v1['version'], '1.0')
        self.assertIn('endpoints', data_v1)

        res_v2 = self.client.get('/api/v2/')
        self.assertEqual(res_v2.status_code, 200)
        self.assertEqual(res_v2['Content-Type'], 'application/json')
        data_v2 = res_v2.json()
        self.assertEqual(data_v2['api_version'], '2.0')

        res_health = self.client.get('/api/v1/health/')
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.json()['status'], 'healthy')

    def test_unauthenticated_requests_return_json_401(self):
        res = self.client.get('/api/v1/rooms/')
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res['Content-Type'], 'application/json')
        self.assertEqual(res.json().get('code'), 'UNAUTHORIZED')

    def test_rbac_denial_returns_json_403(self):
        self.client.login(username='api_student', password=self.password)
        # Student cannot access Admin-only occupancy report
        res = self.client.get('/api/v1/reports/occupancy/')
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res['Content-Type'], 'application/json')
        self.assertEqual(res.json().get('code'), 'FORBIDDEN')

    def test_rooms_api_v1(self):
        self.client.login(username='api_student', password=self.password)
        res = self.client.get('/api/v1/rooms/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/json')
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['room_number'], 'A101')
        self.assertEqual(len(data[0]['beds']), 2)

    def test_notices_api_lifecycle(self):
        # Admin creates notice via v1 POST
        self.client.login(username='api_admin', password=self.password)
        payload = {
            'title': 'Library Renovation',
            'content': 'Library reading hall will be closed this weekend.',
            'target_block': 'A',
        }
        res_post = self.client.post(
            '/api/v1/notices/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res_post.status_code, 201)
        self.assertEqual(res_post['Content-Type'], 'application/json')
        created_id = res_post.json()['notice']['id']

        # Student in Block A fetches notices -> sees it
        self.client.login(username='api_student', password=self.password)
        res_list_a = self.client.get('/api/v1/notices/')
        self.assertEqual(res_list_a.status_code, 200)
        items_a = res_list_a.json()
        self.assertTrue(any(item['id'] == created_id for item in items_a))

        # Student in Block B fetches notices -> does NOT see Block A notice
        self.client.login(username='api_student_b', password=self.password)
        res_list_b = self.client.get('/api/v1/notices/')
        self.assertEqual(res_list_b.status_code, 200)
        items_b = res_list_b.json()
        self.assertFalse(any(item['id'] == created_id for item in items_b))

        # Notice detail endpoint
        res_detail = self.client.get(f'/api/v1/notices/{created_id}/')
        # Block B student gets 403 Forbidden
        self.assertEqual(res_detail.status_code, 403)

        # Block A student gets 200
        self.client.login(username='api_student', password=self.password)
        res_detail_ok = self.client.get(f'/api/v1/notices/{created_id}/')
        self.assertEqual(res_detail_ok.status_code, 200)
        self.assertEqual(res_detail_ok.json()['title'], 'Library Renovation')

    def test_complaints_api_v1(self):
        self.client.login(username='api_student', password=self.password)
        payload = {
            'category': 'plumbing',
            'description': 'Water leak under the sink in bathroom 101.',
        }
        res = self.client.post(
            '/api/v1/complaints/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res['Content-Type'], 'application/json')
        complaint_data = res.json()['complaint']
        self.assertEqual(complaint_data['category'], 'plumbing')

        # GET complaints
        res_get = self.client.get('/api/v1/complaints/')
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(len(res_get.json()), 1)

    def test_occupancy_report_api(self):
        self.client.login(username='api_admin', password=self.password)
        res = self.client.get('/api/v1/reports/occupancy/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/json')
        data = res.json()
        self.assertIn('summary', data)
        self.assertIn('blocks', data)
        self.assertEqual(data['summary']['total_rooms'], 1)

    def test_fees_dues_api(self):
        FeeAccount.objects.create(
            student=self.student,
            total_fee=Decimal('12000.00'),
            amount_paid=Decimal('4000.00')
        )
        self.client.login(username='api_student', password=self.password)
        res = self.client.get('/api/v1/fees/dues/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['due'], '8000.00')
        self.assertEqual(data['total_fee'], '12000.00')

    def test_versioning_backward_compatibility_v1_and_v2(self):
        """
        NFR-8 verification:
        Ensures existing v1 integration schema is preserved when v2 is active.
        """
        Notice.objects.create(
            title='Hostel Annual Day',
            content='Celebrations on campus lawn.',
            target_block='',
            posted_by=self.admin
        )

        self.client.login(username='api_student', password=self.password)

        # v1 client receives flat list
        res_v1 = self.client.get('/api/v1/notices/')
        self.assertEqual(res_v1.status_code, 200)
        data_v1 = res_v1.json()
        self.assertIsInstance(data_v1, list)
        self.assertIn('title', data_v1[0])

        # v2 client receives enveloped response with 'meta' and 'data'
        res_v2 = self.client.get('/api/v2/notices/')
        self.assertEqual(res_v2.status_code, 200)
        data_v2 = res_v2.json()
        self.assertIsInstance(data_v2, dict)
        self.assertEqual(data_v2['api_version'], '2.0')
        self.assertIn('meta', data_v2)
        self.assertIn('data', data_v2)
        self.assertIsInstance(data_v2['data'], list)
        self.assertEqual(data_v2['meta']['total_count'], 1)
        self.assertEqual(data_v2['data'][0]['title'], 'Hostel Annual Day')
