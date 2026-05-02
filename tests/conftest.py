"""
Shared pytest fixtures for the Civvy Election Guide test suite.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.fixture(scope="module")
def client():
    """
    Module-scoped FastAPI test client.
    Avoids re-importing the app for every test function.
    """
    from app.main import app
    return TestClient(app)


@pytest.fixture
def mock_gemini_chat():
    """
    Mocks the Gemini _gemini() coroutine for chat tests.
    Returns a realistic Civvy-style response including FOLLOW_UP.
    """
    mock_response = (
        "India uses the **First Past the Post** voting system.\n\n"
        "1. Each constituency elects one MP.\n"
        "2. The candidate with the most votes wins.\n"
        "3. The Election Commission of India (ECI) oversees the process.\n\n"
        "FOLLOW_UP: Would you like to know about voter registration in India?"
    )
    with patch("app.main._gemini", new_callable=AsyncMock) as mock:
        mock.return_value = mock_response
        yield mock


@pytest.fixture
def mock_gemini_json():
    """Mocks the _gemini_json() helper for structured-output endpoints."""
    with patch("app.main._gemini_json", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_gemini_error():
    """Simulates a Gemini API failure for error-path tests."""
    with patch("app.main._gemini", new_callable=AsyncMock) as mock:
        mock.side_effect = Exception("Gemini API unavailable")
        yield mock
