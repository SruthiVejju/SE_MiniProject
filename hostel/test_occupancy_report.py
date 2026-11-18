"""
Tests for FR-12: Generate Hostel Occupancy Reports & PDF Export.
"""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from core.models import UserProfile
from hostel.models import Allocation, Bed, Room
from hostel.reports import generate_occupancy_pdf, get_occupancy_data
from hostel.services import allocate_bed

User = get_user_model()


class OccupancyReportTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'Pass@12345'

        self.admin = User.objects.create_user(username='admin_occ', password=self.password)
        UserProfile.objects.create(user=self.admin, role=UserProfile.ADMIN)

        self.student1 = User.objects.create_user(username='stu1_occ', password=self.password)
        UserProfile.objects.create(user=self.student1, role=UserProfile.STUDENT, block='A')

        self.student2 = User.objects.create_user(username='stu2_occ', password=self.password)
        UserProfile.objects.create(user=self.student2, role=UserProfile.STUDENT, block='B')

        # Setup Block A: 2 rooms, each with 2 beds (total 4 beds)
        self.room_a1 = Room.objects.create(block='A', room_number='A101', floor=1)
        self.bed_a1_1 = Bed.objects.create(room=self.room_a1, bed_number='B1')
        self.bed_a1_2 = Bed.objects.create(room=self.room_a1, bed_number='B2')

        self.room_a2 = Room.objects.create(block='A', room_number='A102', floor=1)
        self.bed_a2_1 = Bed.objects.create(room=self.room_a2, bed_number='B1')
        self.bed_a2_2 = Bed.objects.create(room=self.room_a2, bed_number='B2')

        # Setup Block B: 1 room with 2 beds (total 2 beds)
        self.room_b1 = Room.objects.create(block='B', room_number='B201', floor=2)
        self.bed_b1_1 = Bed.objects.create(room=self.room_b1, bed_number='B1')
        self.bed_b1_2 = Bed.objects.create(room=self.room_b1, bed_number='B2')

    def test_occupancy_data_calculation_and_matching_allocations(self):
        # Before allocations: 0 occupied, 6 total beds
        data = get_occupancy_data()
        self.assertEqual(data['total_blocks'], 2)
        self.assertEqual(data['total_rooms'], 3)
        self.assertEqual(data['total_beds'], 6)
        self.assertEqual(data['total_occupied'], 0)
        self.assertEqual(data['total_vacant'], 6)
        self.assertEqual(data['overall_rate'], 0.0)

        # Allocate 1 bed in Block A
        allocate_bed(self.student1, self.bed_a1_1.pk, admin_user=self.admin)
        # Allocate 1 bed in Block B
        allocate_bed(self.student2, self.bed_b1_1.pk, admin_user=self.admin)

        data = get_occupancy_data()
        self.assertEqual(data['total_occupied'], 2)
        self.assertEqual(data['total_vacant'], 4)
        self.assertEqual(data['overall_rate'], 33.3)

        block_a = next(b for b in data['blocks'] if b['block'] == 'A')
        self.assertEqual(block_a['rooms'], 2)
        self.assertEqual(block_a['beds'], 4)
        self.assertEqual(block_a['occupied'], 1)
        self.assertEqual(block_a['vacant'], 3)
        self.assertEqual(block_a['rate'], 25.0)

        block_b = next(b for b in data['blocks'] if b['block'] == 'B')
        self.assertEqual(block_b['rooms'], 1)
        self.assertEqual(block_b['beds'], 2)
        self.assertEqual(block_b['occupied'], 1)
        self.assertEqual(block_b['vacant'], 1)
        self.assertEqual(block_b['rate'], 50.0)

    def test_pdf_generation(self):
        allocate_bed(self.student1, self.bed_a1_1.pk, admin_user=self.admin)
        data = get_occupancy_data()
        pdf_bytes = generate_occupancy_pdf(data)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
        self.assertGreater(len(pdf_bytes), 500)

    def test_occupancy_report_html_view(self):
        # Admin can view
        self.client.login(username='admin_occ', password=self.password)
        res = self.client.get(reverse('hostel:occupancy_report'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Hostel Occupancy Report (FR-12)')
        self.assertContains(res, 'Export as PDF')

        # Student is blocked (403)
        self.client.login(username='stu1_occ', password=self.password)
        res_stu = self.client.get(reverse('hostel:occupancy_report'))
        self.assertEqual(res_stu.status_code, 403)

    def test_occupancy_report_pdf_download(self):
        self.client.login(username='admin_occ', password=self.password)
        res = self.client.get(reverse('hostel:occupancy_report_pdf'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', res['Content-Disposition'])
        self.assertTrue(res.content.startswith(b'%PDF'))

        # Query param ?format=pdf also works
        res2 = self.client.get(reverse('hostel:occupancy_report') + '?format=pdf')
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2['Content-Type'], 'application/pdf')
        self.assertTrue(res2.content.startswith(b'%PDF'))
