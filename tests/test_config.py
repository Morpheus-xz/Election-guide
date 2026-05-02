"""Tests for the application configuration module."""
import pytest
from app.config import (
    APP_NAME, VERSION, GEMINI_MODEL, MAX_RETRIES,
    MAX_MESSAGE_LENGTH, SUPPORTED_COUNTRIES, SUPPORTED_LANGUAGES
)


def test_app_name_not_empty():
    assert len(APP_NAME) > 0

def test_version_semver():
    parts = VERSION.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)

def test_gemini_model_not_empty():
    assert len(GEMINI_MODEL) > 0

def test_max_retries_positive():
    assert MAX_RETRIES > 0

def test_max_message_length_reasonable():
    assert 100 <= MAX_MESSAGE_LENGTH <= 2000

def test_supported_countries_not_empty():
    assert len(SUPPORTED_COUNTRIES) >= 5

def test_every_country_has_flag():
    for name, info in SUPPORTED_COUNTRIES.items():
        assert "flag" in info, f"Country {name} missing flag"
        assert len(info["flag"]) > 0

def test_every_country_has_election_system():
    for name, info in SUPPORTED_COUNTRIES.items():
        assert "election_system" in info, f"Country {name} missing election_system"

def test_supported_languages_includes_english():
    assert "English" in SUPPORTED_LANGUAGES

def test_supported_languages_includes_hindi():
    assert "Hindi" in SUPPORTED_LANGUAGES
