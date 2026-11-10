from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Notification, UserProfile
from .testutils import make_user
from .validators import clean_text_field, sanitize_text, validate_length
from django.contrib.auth.models import User

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import LoginAttempt

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



class StudentRegistrationTests(TestCase):

    def test_successful_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newstudent01',
            'first_name': 'Ananya',
            'last_name': 'Sharma',
            'email': 'ananya.test02@example.com',
            'block': 'A',
            'password1': 'HMS_Test@2026Secure',
            'password2': 'HMS_Test@2026Secure',
        })

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username='newstudent01')
        self.assertEqual(user.email, 'ananya.test02@example.com')
        self.assertEqual(user.profile.role, UserProfile.STUDENT)
        self.assertEqual(user.profile.block, 'A')
        self.assertNotEqual(user.password, 'HMS_Test@2026Secure')
        self.assertTrue(user.check_password('HMS_Test@2026Secure'))

    def test_registration_rejects_duplicate_email(self):
        User.objects.create_user(
            username='existing',
            email='ananya.test02@example.com',
            password='Existing@123'
        )

        response = self.client.post(reverse('register'), {
            'username': 'newstudent02',
            'first_name': 'Ananya',
            'last_name': 'Sharma',
            'email': 'ananya.test02@example.com',
            'block': 'A',
            'password1': 'HMS_Test@2026Secure',
            'password2': 'HMS_Test@2026Secure',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newstudent02').exists())

    def test_registration_rejects_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'newstudent03',
            'first_name': 'Ananya',
            'last_name': 'Sharma',
            'email': 'ananya.test03@example.com',
            'block': 'A',
            'password1': 'HMS_Test@2026Secure',
            'password2': 'Different@2026Secure',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newstudent03').exists())



class LoginAndLockoutTests(TestCase):

    def setUp(self):
        self.user = make_user('loginstudent', UserProfile.STUDENT)
        self.login_url = reverse('login')

    def test_successful_login(self):
        self.user.set_password('StrongPass@123')
        self.user.save()

        response = self.client.post(self.login_url, {
            'username': 'loginstudent',
            'password': 'StrongPass@123',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_invalid_password_increments_attempts(self):
        self.user.set_password('StrongPass@123')
        self.user.save()

        self.client.post(self.login_url, {
            'username': 'loginstudent',
            'password': 'WrongPass@123',
        })

        attempt = LoginAttempt.objects.get(user=self.user)
        self.assertEqual(attempt.failed_attempts, 1)

    def test_five_failed_attempts_lock_account(self):
        self.user.set_password('StrongPass@123')
        self.user.save()

        for _ in range(5):
            self.client.post(self.login_url, {
                'username': 'loginstudent',
                'password': 'WrongPass@123',
            })

        attempt = LoginAttempt.objects.get(user=self.user)
        self.assertTrue(attempt.is_locked())
        self.assertIsNotNone(attempt.locked_until)

    def test_correct_password_rejected_during_lockout(self):
        self.user.set_password('StrongPass@123')
        self.user.save()

        attempt = LoginAttempt.objects.create(
            user=self.user,
            failed_attempts=0,
            locked_until=timezone.now() + timedelta(minutes=15),
        )

        response = self.client.post(self.login_url, {
            'username': 'loginstudent',
            'password': 'StrongPass@123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_successful_login_resets_attempts(self):
        self.user.set_password('StrongPass@123')
        self.user.save()

        attempt = LoginAttempt.objects.create(
            user=self.user,
            failed_attempts=3,
        )

        self.client.post(self.login_url, {
            'username': 'loginstudent',
            'password': 'StrongPass@123',
        })

        attempt.refresh_from_db()
        self.assertEqual(attempt.failed_attempts, 0)
        self.assertIsNone(attempt.locked_until)

    def test_logout(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('logout'))

        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)
