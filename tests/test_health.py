"""Tests for the /health and /countries meta endpoints."""
import pytest


def test_health_returns_200(client):
    """Health endpoint must return HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_schema(client):
    """Health response must contain all required fields."""
    data = client.get("/health").json()
    assert data["status"] == "ok"
    assert "model" in data
    assert "version" in data
    assert "app_name" in data


def test_health_model_is_gemini(client):
    """Model field must reference a Gemini model."""
    data = client.get("/health").json()
    assert "gemini" in data["model"].lower()


def test_health_version_format(client):
    """Version must follow semantic versioning (e.g. 3.0.0)."""
    data = client.get("/health").json()
    parts = data["version"].split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)


def test_countries_returns_list(client):
    """Countries endpoint must return a non-empty list."""
    response = client.get("/countries")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_countries_schema(client):
    """Every country entry must have name, flag, and election_system."""
    data = client.get("/countries").json()
    for country in data:
        assert "name" in country
        assert "flag" in country
        assert "election_system" in country


def test_countries_includes_india(client):
    """India must always be in the supported countries list."""
    data = client.get("/countries").json()
    names = [c["name"] for c in data]
    assert "India" in names


def test_countries_flags_are_emoji(client):
    """Country flags should be non-empty strings (emoji or text)."""
    data = client.get("/countries").json()
    for country in data:
        assert len(country["flag"]) > 0
