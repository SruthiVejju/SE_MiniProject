class SecurityHeadersMiddleware:
    """Adds browser-side XSS/clickjacking mitigations to every response."""

    CSP = ("default-src 'self'; script-src 'self'; style-src 'self'; "
           "img-src 'self' data:; frame-ancestors 'none'; form-action 'self'")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # The Django admin relies on inline scripts/styles, so leave its CSP alone.
        if not request.path.startswith('/admin/'):
            response.setdefault('Content-Security-Policy', self.CSP)
        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('Referrer-Policy', 'same-origin')
        return response
