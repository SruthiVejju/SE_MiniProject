# HTTPS and TLS 1.2+ Deployment Configuration

## 1. Overview

The application uses Django security settings to enforce HTTPS in production and protect session and CSRF cookies.

Local development continues to use HTTP.

## 2. Django Security Settings

The production configuration enables:

- HTTPS redirection using `SECURE_SSL_REDIRECT`.
- Secure session cookies using `SESSION_COOKIE_SECURE`.
- Secure CSRF cookies using `CSRF_COOKIE_SECURE`.
- HTTP Strict Transport Security (HSTS) using `SECURE_HSTS_SECONDS`.
- HSTS subdomain protection and preload.

## 3. TLS Configuration

TLS must be configured at the web server or reverse proxy.

For Nginx, configure the HTTPS server with:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

The server must also be configured with valid SSL certificates.

## 4. HTTP Handling

In production, Django redirects HTTP requests to HTTPS through `SECURE_SSL_REDIRECT`.

The repository currently does not define separate API endpoints. Therefore, API-specific HTTP rejection cannot be independently verified until API endpoints are introduced.

## 5. Verification

The automated Django security tests verify:

- HTTP-to-HTTPS redirection.
- HTTPS request handling.
- Production HTTPS and secure-cookie settings.

TLS protocol negotiation must be verified against the deployed HTTPS server to confirm TLS 1.2 or higher.