"""Static checks backing the cross-browser guidance in docs/Cross_Browser_Test_Report.md."""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class FrontendCompatibilityTests(SimpleTestCase):
    def test_base_template_declares_doctype_charset_and_viewport(self):
        html = (Path(settings.BASE_DIR) / 'templates' / 'base.html').read_text()
        self.assertTrue(html.lstrip().lower().startswith('<!doctype html>'))
        self.assertIn('charset="utf-8"', html)
        self.assertIn('name="viewport"', html)

    def test_no_inline_scripts_or_styles(self):
        for path in (Path(settings.BASE_DIR) / 'templates').rglob('*.html'):
            text = path.read_text().lower()
            self.assertNotIn('<script', text, path)
            self.assertNotIn('style=', text, path)

    def test_css_avoids_browser_specific_prefixes(self):
        css = (Path(settings.BASE_DIR) / 'static' / 'css' / 'hms.css').read_text()
        for prefix in ('-webkit-', '-moz-', '-ms-'):
            self.assertNotIn(prefix, css)
