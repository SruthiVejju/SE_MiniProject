from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Notification, UserProfile
from .testutils import make_user
from .validators import clean_text_field, sanitize_text, validate_length


class SanitizeTests(TestCase):
    def test_strips_script_tags(self):
        self.assertNotIn('<', sanitize_text('<script>alert(1)</script>hello'))

    def test_removes_event_handlers_and_js_scheme(self):
        out = sanitize_text('<img src=x onerror=alert(1)> javascript:alert(1)')
        self.assertNotIn('onerror=', out.lower())
        self.assertNotIn('javascript:', out.lower())

    def test_removes_control_chars_and_collapses_whitespace(self):
        self.assertEqual(sanitize_text('a\x00b   c\n d'), 'ab c d')

    def test_none_is_empty(self):
        self.assertEqual(sanitize_text(None), '')

    def test_length_validation(self):
        with self.assertRaises(ValidationError):
            validate_length('ab', 3, 10, 'Field')
        self.assertEqual(clean_text_field(' ok text ', 'F', 2, 20), 'ok text')
        with self.assertRaises(ValidationError):
            clean_text_field('<b></b>', 'F', 1, 20)


class SecurityHeaderTests(TestCase):
    def test_headers_present_on_app_pages(self):
        user = make_user('stu', UserProfile.STUDENT)
        self.client.force_login(user)
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp['X-Content-Type-Options'], 'nosniff')
        self.assertIn("default-src 'self'", resp['Content-Security-Policy'])

    def test_admin_site_has_no_csp(self):
        resp = self.client.get('/admin/login/')
        self.assertNotIn('Content-Security-Policy', resp)


class HomeAndNotificationTests(TestCase):
    def setUp(self):
        self.user = make_user('stu', UserProfile.STUDENT)
        self.client.force_login(self.user)

    def test_home_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('home')).status_code, 302)

    def test_home_shows_notifications_escaped(self):
        Notification.objects.create(user=self.user, message='<b>hi</b>')
        resp = self.client.get(reverse('home'))
        self.assertContains(resp, '&lt;b&gt;hi&lt;/b&gt;')

    def test_mark_read(self):
        Notification.objects.create(user=self.user, message='x')
        self.client.post(reverse('notifications-read'))
        self.assertFalse(self.user.notifications.filter(is_read=False).exists())

    def test_mark_read_get_does_nothing(self):
        Notification.objects.create(user=self.user, message='x')
        self.client.get(reverse('notifications-read'))
        self.assertTrue(self.user.notifications.filter(is_read=False).exists())

    def test_user_without_profile_is_forbidden_on_role_views(self):
        from django.contrib.auth import get_user_model
        u = get_user_model().objects.create_user('noprof')
        self.client.force_login(u)
        self.assertEqual(self.client.get(reverse('leave-mine')).status_code, 403)
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)

    def test_str_methods(self):
        n = Notification.objects.create(user=self.user, message='m')
        self.assertIn('m', str(n))
        self.assertIn('student', str(self.user.profile))
