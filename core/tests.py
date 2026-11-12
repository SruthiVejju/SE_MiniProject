from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AuditLog, Notification, UserProfile
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

class RegistrationAndAuthenticationTests(TestCase):

    def create_auth_user(
        self,
        username,
        password="Violet!River#2026",
        role=UserProfile.STUDENT
    ):
        User = get_user_model()

        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password=password
        )

        UserProfile.objects.create(
            user=user,
            role=role
        )

        return user

    def registration_data(self, roll_number="REGTEST001"):
        return {
            "full_name": "Test Student",
            "roll_number": roll_number,
            "department": "CSE",
            "contact_number": "9876543210",
            "email": f"{roll_number}@example.com",
            "password": "Violet!River#2026",
            "confirm_password": "Violet!River#2026",
        }

    def test_student_registration(self):
        response = self.client.post(
            reverse("register"),
            self.registration_data()
        )

        User = get_user_model()
        user = User.objects.get(username="REGTEST001")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.profile.role, UserProfile.STUDENT)
        self.assertEqual(user.profile.full_name, "Test Student")
        self.assertTrue(
            user.check_password("Violet!River#2026")
        )

        self.assertTrue(
            AuditLog.objects.filter(
                event=AuditLog.REGISTRATION,
                user=user
            ).exists()
        )

    def test_password_uses_bcrypt(self):
        user = self.create_auth_user("BCRYPT001")

        self.assertEqual(
            identify_hasher(user.password).algorithm,
            "bcrypt_sha256"
        )

    def test_duplicate_roll_number_rejected(self):
        User = get_user_model()
        User.objects.create_user(username="DUPLICATE001")

        response = self.client.post(
            reverse("register"),
            self.registration_data("DUPLICATE001")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "This roll number is already registered."
        )

    def test_successful_login(self):
        user = self.create_auth_user("LOGIN001")

        response = self.client.post(
            reverse("login"),
            {
                "username": "LOGIN001",
                "password": "Violet!River#2026",
            }
        )

        user.profile.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))
        self.assertEqual(user.profile.failed_login_attempts, 0)

        self.assertTrue(
            AuditLog.objects.filter(
                event=AuditLog.LOGIN_SUCCESS,
                user=user
            ).exists()
        )

    def test_all_four_roles_can_login(self):
        roles = [
            UserProfile.STUDENT,
            UserProfile.WARDEN,
            UserProfile.ADMIN,
            UserProfile.SECURITY,
        ]

        for index, role in enumerate(roles):
            username = f"ROLEUSER{index}"

            self.create_auth_user(username, role=role)

            response = self.client.post(
                reverse("login"),
                {
                    "username": username,
                    "password": "Violet!River#2026",
                }
            )

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse("home"))

            self.client.logout()

    def test_failed_login_increments_counter(self):
        user = self.create_auth_user("FAILED001")

        self.client.post(
            reverse("login"),
            {
                "username": "FAILED001",
                "password": "WrongPassword!123",
            }
        )

        user.profile.refresh_from_db()

        self.assertEqual(user.profile.failed_login_attempts, 1)

        self.assertTrue(
            AuditLog.objects.filter(
                event=AuditLog.LOGIN_FAILURE,
                user=user
            ).exists()
        )

    def test_five_failed_attempts_lock_account(self):
        user = self.create_auth_user("LOCKTEST001")

        for attempt in range(5):
            response = self.client.post(
                reverse("login"),
                {
                    "username": "LOCKTEST001",
                    "password": "WrongPassword!123",
                }
            )

        user.profile.refresh_from_db()

        self.assertEqual(user.profile.failed_login_attempts, 5)
        self.assertIsNotNone(user.profile.locked_until)
        self.assertGreater(
            user.profile.locked_until,
            timezone.now()
        )
        self.assertContains(
            response,
            "Five failed attempts!"
        )

    def test_correct_password_rejected_during_lock(self):
        user = self.create_auth_user("LOCKTEST002")

        user.profile.failed_login_attempts = 5
        user.profile.locked_until = (
            timezone.now() + timedelta(minutes=15)
        )
        user.profile.save()

        response = self.client.post(
            reverse("login"),
            {
                "username": "LOCKTEST002",
                "password": "Violet!River#2026",
            }
        )

        self.assertContains(
            response,
            "Account temporarily locked"
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session
        )

    def test_expired_lock_allows_login(self):
        user = self.create_auth_user("EXPIRED001")

        user.profile.failed_login_attempts = 5
        user.profile.locked_until = (
            timezone.now() - timedelta(seconds=1)
        )
        user.profile.save()

        response = self.client.post(
            reverse("login"),
            {
                "username": "EXPIRED001",
                "password": "Violet!River#2026",
            }
        )

        user.profile.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.profile.failed_login_attempts, 0)
        self.assertIsNone(user.profile.locked_until)

    def test_successful_login_resets_failed_attempts(self):
        user = self.create_auth_user("RESET001")

        user.profile.failed_login_attempts = 3
        user.profile.save()

        self.client.post(
            reverse("login"),
            {
                "username": "RESET001",
                "password": "Violet!River#2026",
            }
        )

        user.profile.refresh_from_db()

        self.assertEqual(user.profile.failed_login_attempts, 0)

    def test_logout_records_audit_event(self):
        user = self.create_auth_user("LOGOUT001")

        self.client.force_login(user)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(
            response,
            reverse("login")
        )

        self.assertTrue(
            AuditLog.objects.filter(
                event=AuditLog.LOGOUT,
                user=user
            ).exists()
        )

    def test_failed_login_for_unknown_user_is_logged(self):
        self.client.post(
            reverse("login"),
            {
                "username": "UNKNOWN001",
                "password": "WrongPassword!123",
            }
        )

        self.assertTrue(
            AuditLog.objects.filter(
                event=AuditLog.LOGIN_FAILURE,
                identifier="UNKNOWN001",
                user__isnull=True
            ).exists()
        )
