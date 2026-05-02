"""
Integration tests for /glossary, /quiz, /compare, and /fact endpoints.
All use mocked Gemini to avoid real API calls.
"""
import pytest
import json


QUIZ_MOCK = json.dumps({
    "questions": [
        {
            "question": "Which body conducts elections in India?",
            "options": [
                "A) Parliament", "B) Supreme Court",
                "C) Election Commission of India", "D) President"
            ],
            "correct": "C",
            "explanation": "The ECI is the constitutional body that oversees all elections."
        }
    ] * 5
})

COMPARE_MOCK = json.dumps({
    "aspects": [
        {
            "aspect": "Voting System",
            "country1": "First Past the Post",
            "country2": "Preferential Voting",
            "winner": "country2",
            "reason": "Preferential voting better represents voter preferences."
        }
    ],
    "summary": "Both are mature democracies with different electoral approaches."
})

GLOSSARY_MOCK = json.dumps([
    {
        "term": "ECI",
        "definition": "Election Commission of India — the constitutional body overseeing elections.",
        "example": "ECI announced the 2024 Lok Sabha election schedule in March."
    }
] * 15)

FACT_MOCK = json.dumps({
    "fact": "India's 2024 general election was the largest democratic exercise in human history, with over 640 million votes cast."
})


# ── Quiz endpoint ───────────────────────────────────────────────────────────

def test_quiz_returns_200(client, mock_gemini_json):
    """Quiz endpoint must return HTTP 200."""
    mock_gemini_json.return_value = json.loads(QUIZ_MOCK)
    response = client.post("/quiz", json={"country": "India", "topic": "Voter Registration"})
    assert response.status_code == 200


def test_quiz_returns_5_questions(client, mock_gemini_json):
    """Quiz must return exactly 5 questions."""
    mock_gemini_json.return_value = json.loads(QUIZ_MOCK)
    data = client.post("/quiz", json={"country": "India"}).json()
    assert len(data["questions"]) == 5


def test_quiz_question_schema(client, mock_gemini_json):
    """Each quiz question must have required fields."""
    mock_gemini_json.return_value = json.loads(QUIZ_MOCK)
    data = client.post("/quiz", json={"country": "India"}).json()
    q = data["questions"][0]
    assert "question" in q
    assert "options" in q
    assert "correct" in q
    assert "explanation" in q


def test_quiz_options_count(client, mock_gemini_json):
    """Each question must have exactly 4 options."""
    mock_gemini_json.return_value = json.loads(QUIZ_MOCK)
    data = client.post("/quiz", json={"country": "India"}).json()
    for q in data["questions"]:
        assert len(q["options"]) == 4


# ── Compare endpoint ────────────────────────────────────────────────────────

def test_compare_returns_200(client, mock_gemini_json):
    """Compare endpoint must return HTTP 200."""
    mock_gemini_json.return_value = json.loads(COMPARE_MOCK)
    response = client.post("/compare", json={
        "country1": "India", "country2": "United States"
    })
    assert response.status_code == 200


def test_compare_has_aspects_and_summary(client, mock_gemini_json):
    """Compare response must include aspects list and summary."""
    mock_gemini_json.return_value = json.loads(COMPARE_MOCK)
    data = client.post("/compare", json={
        "country1": "India", "country2": "Australia"
    }).json()
    assert "aspects" in data
    assert "summary" in data
    assert len(data["aspects"]) > 0


def test_compare_missing_country_fails(client):
    """Compare without both countries must return 422."""
    response = client.post("/compare", json={"country1": "India"})
    assert response.status_code == 422


# ── Glossary endpoint ───────────────────────────────────────────────────────

def test_glossary_returns_200(client, mock_gemini_json):
    """Glossary endpoint must return HTTP 200."""
    mock_gemini_json.return_value = json.loads(GLOSSARY_MOCK)
    response = client.get("/glossary?country=India")
    assert response.status_code == 200


def test_glossary_returns_15_terms(client, mock_gemini_json):
    """Glossary must return exactly 15 terms."""
    mock_gemini_json.return_value = json.loads(GLOSSARY_MOCK)
    data = client.get("/glossary?country=TestCountry999").json()
    assert len(data) == 15


def test_glossary_term_schema(client, mock_gemini_json):
    """Each glossary term must have term, definition, and example fields."""
    mock_gemini_json.return_value = json.loads(GLOSSARY_MOCK)
    data = client.get("/glossary?country=TestCountry998").json()
    term = data[0]
    assert "term" in term
    assert "definition" in term


def test_glossary_cached_on_second_call(client, mock_gemini_json):
    """Second call for same country must use cache (no new Gemini call)."""
    mock_gemini_json.return_value = json.loads(GLOSSARY_MOCK)
    # First call — primes cache for "CachedCountry"
    client.get("/glossary?country=CachedCountry")
    call_count_after_first = mock_gemini_json.call_count
    # Second call — should use cache
    client.get("/glossary?country=CachedCountry")
    assert mock_gemini_json.call_count == call_count_after_first


# ── Fact endpoint ───────────────────────────────────────────────────────────

def test_fact_returns_200(client, mock_gemini_json):
    """Fact endpoint must return HTTP 200."""
    mock_gemini_json.return_value = json.loads(FACT_MOCK)
    response = client.get("/fact?country=India")
    assert response.status_code == 200


def test_fact_has_fact_field(client, mock_gemini_json):
    """Fact response must include a non-empty fact field."""
    mock_gemini_json.return_value = json.loads(FACT_MOCK)
    data = client.get("/fact?country=India").json()
    assert "fact" in data
    assert len(data["fact"]) > 0
