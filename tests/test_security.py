"""
Tests for security headers, rate limiting, and the /translate endpoint.
Verifies OWASP header presence and input validation on all new endpoints.
"""
import pytest


# ── Security headers ────────────────────────────────────────────────────────

def test_security_headers_on_get(client):
    """Every GET response must include OWASP security headers."""
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_security_headers_on_post(client, mock_gemini_chat):
    """Security headers must be present on POST responses too."""
    response = client.post("/chat", json={
        "message": "How do I vote?",
        "country": "India"
    })
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_hsts_header_present(client):
    """Strict-Transport-Security header must be set for HTTPS enforcement."""
    response = client.get("/health")
    hsts = response.headers.get("Strict-Transport-Security", "")
    assert "max-age" in hsts
    assert "31536000" in hsts


def test_permissions_policy_present(client):
    """Permissions-Policy header must restrict unnecessary browser APIs."""
    response = client.get("/health")
    assert "Permissions-Policy" in response.headers


def test_security_headers_on_404(client):
    """Security headers must be present even on 404 responses."""
    response = client.get("/this-endpoint-does-not-exist")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"


def test_security_headers_on_countries(client):
    """Security headers must be present on /countries endpoint."""
    response = client.get("/countries")
    assert response.headers.get("X-Frame-Options") == "DENY"


# ── /translate endpoint ─────────────────────────────────────────────────────

def test_translate_endpoint_registered(client):
    """POST /translate must be a registered route (not 404 or 405)."""
    response = client.post("/translate", json={
        "text": "How do I vote?",
        "target_language": "hi"
    })
    # 200 = Cloud Translation worked
    # 502 = endpoint exists but Cloud Translation not configured in test env
    # 503 = translation library unavailable
    assert response.status_code in [200, 502, 503]


def test_translate_missing_target_language(client):
    """Translate without target_language must return 422."""
    response = client.post("/translate", json={"text": "Hello"})
    assert response.status_code == 422


def test_translate_empty_text_rejected(client):
    """Translate with empty text must return 422."""
    response = client.post("/translate", json={
        "text": "",
        "target_language": "hi"
    })
    assert response.status_code == 422


def test_translate_text_too_long_rejected(client):
    """Translate with text over 2000 characters must return 422."""
    response = client.post("/translate", json={
        "text": "a" * 2001,
        "target_language": "hi"
    })
    assert response.status_code == 422


def test_translate_valid_request_accepted(client):
    """Valid translate request must be accepted (not 422)."""
    response = client.post("/translate", json={
        "text": "How do elections work?",
        "target_language": "hi"
    })
    assert response.status_code != 422


def test_translate_with_source_language(client):
    """Translate with optional source_language must not fail validation."""
    response = client.post("/translate", json={
        "text": "How do elections work?",
        "target_language": "hi",
        "source_language": "en"
    })
    assert response.status_code != 422
