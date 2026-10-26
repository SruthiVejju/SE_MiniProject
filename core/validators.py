"""Server-side input validation and sanitisation (SEC-REQ-4)."""
import re
import unicodedata

from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

_CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
_DANGEROUS_SCHEME = re.compile(r'(javascript|vbscript|data)\s*:', re.IGNORECASE)
_EVENT_HANDLER = re.compile(r'\bon\w+\s*=', re.IGNORECASE)


def sanitize_text(value):
    """Strip HTML tags, control characters and script-ish payloads from text.

    Output is still HTML-escaped by Django templates; this is defence in depth.
    """
    if value is None:
        return ''
    value = unicodedata.normalize('NFKC', str(value))
    value = _CONTROL_CHARS.sub('', value)
    value = strip_tags(value)
    value = _DANGEROUS_SCHEME.sub('', value)
    value = _EVENT_HANDLER.sub('', value)
    value = value.replace('<', '').replace('>', '')
    return ' '.join(value.split())


def validate_length(value, min_len, max_len, label='Value'):
    if not (min_len <= len(value) <= max_len):
        raise ValidationError(
            f'{label} must be between {min_len} and {max_len} characters.')
    return value


def clean_text_field(value, label, min_len=1, max_len=255):
    """Sanitise then length-check; rejects input that sanitises to nothing."""
    cleaned = sanitize_text(value)
    validate_length(cleaned, min_len, max_len, label)
    return cleaned
