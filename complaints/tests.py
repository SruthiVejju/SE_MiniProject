from django.test import TestCase
from django.urls import reverse

from core.models import UserProfile
from core.testutils import make_user

from .models import Complaint


def complaint_payload(**overrides):
    data = {
        'category': Complaint.ELECTRICAL,
        'description': 'The lights in my room are not working.',
    }
    data.update(overrides)
    return data


class ComplaintSubmissionTests(TestCase):
    def setUp(self):
        self.student = make_user('complaint_student', UserProfile.STUDENT, 'A')
        self.warden = make_user('complaint_warden', UserProfile.WARDEN, 'A')
        self.url = reverse('complaint-submit')
        self.client.force_login(self.student)

    def test_valid_complaint_is_saved(self):
        response = self.client.post(self.url, complaint_payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Complaint.objects.count(), 1)

        complaint = Complaint.objects.get()
        self.assertEqual(complaint.student, self.student)
        self.assertEqual(complaint.category, Complaint.ELECTRICAL)
        self.assertContains(response, str(complaint.complaint_id))

    def test_all_valid_categories_are_accepted(self):
        for category, _label in Complaint.CATEGORY_CHOICES:
            response = self.client.post(
                self.url,
                complaint_payload(category=category)
            )
            self.assertEqual(response.status_code, 200)

        self.assertEqual(Complaint.objects.count(), 4)

    def test_invalid_category_is_rejected(self):
        response = self.client.post(
            self.url,
            complaint_payload(category='invalid')
        )

        self.assertIn('category', response.context['form'].errors)
        self.assertEqual(Complaint.objects.count(), 0)

    def test_description_shorter_than_10_characters_is_rejected(self):
        response = self.client.post(
            self.url,
            complaint_payload(description='Too short')
        )

        self.assertIn('description', response.context['form'].errors)
        self.assertEqual(Complaint.objects.count(), 0)

    def test_description_longer_than_500_characters_is_rejected(self):
        response = self.client.post(
            self.url,
            complaint_payload(description='A' * 501)
        )

        self.assertIn('description', response.context['form'].errors)
        self.assertEqual(Complaint.objects.count(), 0)

    def test_description_of_exactly_10_characters_is_accepted(self):
        response = self.client.post(
            self.url,
            complaint_payload(description='1234567890')
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Complaint.objects.count(), 1)

    def test_description_of_exactly_500_characters_is_accepted(self):
        response = self.client.post(
            self.url,
            complaint_payload(description='A' * 500)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Complaint.objects.count(), 1)

    def test_each_complaint_receives_a_unique_id(self):
        self.client.post(self.url, complaint_payload())
        self.client.post(
            self.url,
            complaint_payload(category=Complaint.PLUMBING)
        )

        complaints = list(Complaint.objects.all())

        self.assertEqual(len(complaints), 2)
        self.assertNotEqual(
            complaints[0].complaint_id,
            complaints[1].complaint_id
        )

    def test_only_students_can_submit_complaints(self):
        self.client.force_login(self.warden)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Complaint.objects.count(), 0)

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_get_displays_complaint_form(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Submit Maintenance Complaint')

class ComplaintManagementTests(TestCase):
    def setUp(self):
        self.warden_a = make_user(
            'warden_block_a',
            UserProfile.WARDEN,
            'A'
        )
        self.warden_b = make_user(
            'warden_block_b',
            UserProfile.WARDEN,
            'B'
        )

        self.student_a = make_user(
            'student_block_a',
            UserProfile.STUDENT,
            'A'
        )
        self.student_b = make_user(
            'student_block_b',
            UserProfile.STUDENT,
            'B'
        )

        self.complaint_a = Complaint.objects.create(
            student=self.student_a,
            category=Complaint.ELECTRICAL,
            description='Electrical problem in my room.'
        )

        self.complaint_b = Complaint.objects.create(
            student=self.student_b,
            category=Complaint.PLUMBING,
            description='Water leakage in my bathroom.'
        )

        self.url = reverse('complaint-list')
        self.client.force_login(self.warden_a)

    def test_warden_sees_only_complaints_from_assigned_block(self):
        response = self.client.get(self.url)

        self.assertContains(
            response,
            str(self.complaint_a.complaint_id)
        )
        self.assertNotContains(
            response,
            str(self.complaint_b.complaint_id)
        )

    def test_warden_can_view_another_block_after_login(self):
        self.client.force_login(self.warden_b)

        response = self.client.get(self.url)

        self.assertContains(
            response,
            str(self.complaint_b.complaint_id)
        )
        self.assertNotContains(
            response,
            str(self.complaint_a.complaint_id)
        )

    def test_warden_can_change_status_to_in_progress(self):
        response = self.client.post(
            reverse('complaint-update', args=[self.complaint_a.pk]),
            {
                'status': Complaint.IN_PROGRESS,
                'remark': 'Technician assigned.'
            }
        )

        self.assertRedirects(response, self.url)

        self.complaint_a.refresh_from_db()
        self.assertEqual(
            self.complaint_a.status,
            Complaint.IN_PROGRESS
        )
        self.assertEqual(
            self.complaint_a.remark,
            'Technician assigned.'
        )

    def test_warden_can_mark_complaint_resolved(self):
        self.client.post(
            reverse('complaint-update', args=[self.complaint_a.pk]),
            {
                'status': Complaint.RESOLVED,
                'remark': 'Repair completed.'
            }
        )

        self.complaint_a.refresh_from_db()
        self.assertEqual(
            self.complaint_a.status,
            Complaint.RESOLVED
        )

    def test_warden_can_keep_optional_remark_empty(self):
        self.client.post(
            reverse('complaint-update', args=[self.complaint_a.pk]),
            {
                'status': Complaint.OPEN,
                'remark': ''
            }
        )

        self.complaint_a.refresh_from_db()
        self.assertEqual(self.complaint_a.remark, '')

    def test_warden_cannot_update_other_blocks_complaint(self):
        response = self.client.post(
            reverse('complaint-update', args=[self.complaint_b.pk]),
            {
                'status': Complaint.RESOLVED,
                'remark': 'Unauthorized update.'
            }
        )

        self.assertEqual(response.status_code, 404)

        self.complaint_b.refresh_from_db()
        self.assertEqual(self.complaint_b.status, Complaint.OPEN)
        self.assertEqual(self.complaint_b.remark, '')

    def test_invalid_status_is_rejected(self):
        response = self.client.post(
            reverse('complaint-update', args=[self.complaint_a.pk]),
            {
                'status': 'invalid',
                'remark': ''
            }
        )

        self.assertRedirects(response, self.url)

        self.complaint_a.refresh_from_db()
        self.assertEqual(self.complaint_a.status, Complaint.OPEN)

    def test_student_cannot_access_warden_dashboard(self):
        self.client.force_login(self.student_a)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_access_warden_dashboard(self):
        admin = make_user(
            'complaint_admin',
            UserProfile.ADMIN,
            'A'
        )
        self.client.force_login(admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_access_warden_dashboard(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_update_requires_post(self):
        response = self.client.get(
            reverse('complaint-update', args=[self.complaint_a.pk])
        )

        self.assertEqual(response.status_code, 405)