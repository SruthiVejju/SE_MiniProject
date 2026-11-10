from django.test import SimpleTestCase, override_settings


@override_settings(
    DEBUG=False,
    SECURE_SSL_REDIRECT=True,
    SECURE_HSTS_SECONDS=31536000,
    SESSION_COOKIE_SECURE=True,
    CSRF_COOKIE_SECURE=True,
)
class HTTPSecurityTests(SimpleTestCase):

    def test_http_request_redirects_to_https(self):
        response = self.client.get('/', secure=False)
        self.assertEqual(response.status_code, 301)
        self.assertTrue(response.url.startswith('https://'))

    def test_https_request_is_allowed(self):
        response = self.client.get('/', secure=True)
        self.assertNotEqual(response.status_code, 301)

    def test_security_settings_are_enabled(self):
        from django.conf import settings

        self.assertTrue(settings.SECURE_SSL_REDIRECT)
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)
        self.assertEqual(settings.SECURE_HSTS_SECONDS, 31536000)