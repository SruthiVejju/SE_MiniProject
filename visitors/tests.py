from django.test import TestCase
from django.urls import reverse

from core.models import UserProfile
from core.testutils import make_user

from .models import Visitor


class VisitorTests(TestCase):
    def setUp(self):
        self.guard = make_user('guard', UserProfile.SECURITY)
        self.student = make_user('stu', UserProfile.STUDENT)
        self.client.force_login(self.guard)

    def entry(self, **over):
        data = {'name': 'Ravi Kumar', 'purpose': 'Meeting son', 'host_student': self.student.pk}
        data.update(over)
        return self.client.post(reverse('visitor-entry'), data)

    def test_entry_recorded_with_automatic_timestamp(self):
        self.assertRedirects(self.entry(), reverse('visitor-list'))
        v = Visitor.objects.get()
        self.assertIsNotNone(v.entry_time)
        self.assertIsNone(v.exit_time)
        self.assertTrue(v.is_inside)
        self.assertEqual(v.logged_by, self.guard)
        self.assertIn('Ravi', str(v))

    def test_exit_timestamp_captured(self):
        self.entry()
        v = Visitor.objects.get()
        self.client.post(reverse('visitor-exit', args=[v.pk]))
        v.refresh_from_db()
        self.assertIsNotNone(v.exit_time)
        self.assertFalse(v.is_inside)

    def test_exit_twice_keeps_first_time(self):
        self.entry()
        v = Visitor.objects.get()
        url = reverse('visitor-exit', args=[v.pk])
        self.client.post(url)
        first = Visitor.objects.get().exit_time
        self.client.post(url)
        self.assertEqual(Visitor.objects.get().exit_time, first)

    def test_missing_fields_rejected(self):
        resp = self.entry(name='', purpose='')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Visitor.objects.count(), 0)

    def test_host_must_be_student(self):
        resp = self.entry(host_student=self.guard.pk)
        self.assertIn('host_student', resp.context['form'].errors)

    def test_xss_in_name_sanitised(self):
        self.entry(name='<script>alert(1)</script>Bob')
        self.assertNotIn('<', Visitor.objects.get().name)
        self.assertNotContains(self.client.get(reverse('visitor-list')), '<script>alert')

    def test_sql_injection_in_purpose_is_data(self):
        self.entry(purpose="'; DROP TABLE visitors_visitor; --")
        self.assertEqual(Visitor.objects.count(), 1)

    def test_only_security_guard_allowed(self):
        for user in (self.student, make_user('adm', UserProfile.ADMIN)):
            self.client.force_login(user)
            self.assertEqual(self.client.get(reverse('visitor-list')).status_code, 403)
            self.assertEqual(self.client.post(reverse('visitor-entry'), {}).status_code, 403)

    def test_list_shows_visitors(self):
        self.entry()
        self.assertContains(self.client.get(reverse('visitor-list')), 'Ravi Kumar')
