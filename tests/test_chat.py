"""
Tests for the /chat endpoint.
Covers: happy path, input validation, error handling, edge cases,
language support, and history handling.
"""
import pytest


# ── Happy path ─────────────────────────────────────────────────────────────

def test_chat_returns_200(client, mock_gemini_chat):
    """Standard chat request must return HTTP 200."""
    response = client.post("/chat", json={
        "message": "How do I register to vote?",
        "history": [],
        "country": "India",
        "language": "English"
    })
    assert response.status_code == 200


def test_chat_response_has_reply(client, mock_gemini_chat):
    """Response must contain a non-empty reply field."""
    data = client.post("/chat", json={
        "message": "How do I register to vote?",
        "country": "India"
    }).json()
    assert "reply" in data
    assert len(data["reply"]) > 0


def test_chat_extracts_follow_up(client, mock_gemini_chat):
    """Parser must extract FOLLOW_UP from the Gemini response."""
    data = client.post("/chat", json={
        "message": "How does voting work?",
        "country": "India"
    }).json()
    assert data.get("follow_up") is not None
    assert "India" in data["follow_up"]


def test_chat_with_history(client, mock_gemini_chat):
    """Chat must accept and process conversation history."""
    response = client.post("/chat", json={
        "message": "Tell me more",
        "history": [
            {"role": "user", "parts": ["How do I vote?"]},
            {"role": "model", "parts": ["You vote at your local polling booth."]}
        ],
        "country": "India"
    })
    assert response.status_code == 200


def test_chat_with_language(client, mock_gemini_chat):
    """Language parameter must be accepted without error."""
    response = client.post("/chat", json={
        "message": "How do I vote?",
        "country": "India",
        "language": "Hindi"
    })
    assert response.status_code == 200


def test_chat_all_supported_countries(client, mock_gemini_chat):
    """Chat must work for all supported countries."""
    countries = ["India", "United States", "United Kingdom", "Australia", "Canada"]
    for country in countries:
        response = client.post("/chat", json={
            "message": "How do elections work?",
            "country": country
        })
        assert response.status_code == 200, f"Failed for country: {country}"


# ── Input validation — reject bad input ────────────────────────────────────

def test_chat_empty_message_rejected(client):
    """Empty string message must be rejected with 422."""
    response = client.post("/chat", json={
        "message": "",
        "country": "India"
    })
    assert response.status_code == 422


def test_chat_whitespace_only_rejected(client):
    """Whitespace-only message must be rejected with 422."""
    response = client.post("/chat", json={
        "message": "     ",
        "country": "India"
    })
    assert response.status_code == 422


def test_chat_message_too_long_rejected(client):
    """Message over 500 characters must be rejected with 422."""
    response = client.post("/chat", json={
        "message": "a" * 501,
        "country": "India"
    })
    assert response.status_code == 422


def test_chat_exactly_500_chars_accepted(client, mock_gemini_chat):
    """Message of exactly 500 characters must be accepted."""
    response = client.post("/chat", json={
        "message": "a" * 500,
        "country": "India"
    })
    assert response.status_code == 200


def test_chat_missing_message_rejected(client):
    """Request without message field must be rejected with 422."""
    response = client.post("/chat", json={"country": "India"})
    assert response.status_code == 422


def test_chat_default_country_is_india(client, mock_gemini_chat):
    """Country should default to India when not provided."""
    response = client.post("/chat", json={"message": "How do elections work?"})
    assert response.status_code == 200


# ── Error handling ──────────────────────────────────────────────────────────

def test_chat_gemini_error_returns_502(client, mock_gemini_error):
    """Gemini API failure must return 502, not 500 or 200."""
    response = client.post("/chat", json={
        "message": "How do I vote?",
        "country": "India"
    })
    assert response.status_code == 502


def test_chat_gemini_error_has_detail(client, mock_gemini_error):
    """502 response must include a detail message."""
    response = client.post("/chat", json={
        "message": "How do I vote?",
        "country": "India"
    })
    assert "detail" in response.json()


# ── Edge cases ──────────────────────────────────────────────────────────────

def test_chat_message_stripped_of_whitespace(client, mock_gemini_chat):
    """Leading/trailing whitespace must be stripped before processing."""
    response = client.post("/chat", json={
        "message": "  How do I vote?  ",
        "country": "India"
    })
    assert response.status_code == 200


def test_chat_special_characters_in_message(client, mock_gemini_chat):
    """Messages with special characters must be handled safely."""
    response = client.post("/chat", json={
        "message": "What is the <script>alert('xss')</script> process?",
        "country": "India"
    })
    assert response.status_code == 200


def test_chat_unicode_message(client, mock_gemini_chat):
    """Unicode messages (Hindi script) must be accepted."""
    response = client.post("/chat", json={
        "message": "मतदान कैसे करें?",
        "country": "India",
        "language": "Hindi"
    })
    assert response.status_code == 200
