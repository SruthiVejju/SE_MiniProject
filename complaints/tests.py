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