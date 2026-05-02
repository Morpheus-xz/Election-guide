"""
Unit tests for Pydantic request/response models.
Validates field constraints, defaults, and validators.
"""
import pytest
from pydantic import ValidationError
from app.main import (
    ChatRequest, ChatResponse, QuizRequest, QuizQuestion,
    CompareRequest, TimelineEvent, GlossaryTerm, FactResponse
)


# ── ChatRequest ─────────────────────────────────────────────────────────────

def test_chat_request_valid():
    """Valid ChatRequest must be created without error."""
    req = ChatRequest(message="Hello", country="India", language="English")
    assert req.country == "India"
    assert req.language == "English"


def test_chat_request_defaults():
    """ChatRequest must apply correct defaults."""
    req = ChatRequest(message="Hello")
    assert req.country == "India"
    assert req.language == "English"
    assert req.history == []


def test_chat_request_message_stripped():
    """Message validator must strip surrounding whitespace."""
    req = ChatRequest(message="  Hello World  ")
    assert req.message == "Hello World"


def test_chat_request_empty_message_fails():
    """Empty message must raise ValidationError."""
    with pytest.raises(ValidationError):
        ChatRequest(message="")


def test_chat_request_blank_message_fails():
    """Whitespace-only message must raise ValidationError."""
    with pytest.raises(ValidationError):
        ChatRequest(message="   ")


def test_chat_request_message_too_long_fails():
    """Message over MAX_MESSAGE_LENGTH must raise ValidationError."""
    with pytest.raises(ValidationError):
        ChatRequest(message="x" * 501)


def test_chat_request_exactly_max_length_accepted():
    """Message of exactly 500 chars must be accepted."""
    req = ChatRequest(message="x" * 500)
    assert len(req.message) == 500


# ── TimelineEvent ───────────────────────────────────────────────────────────

def test_timeline_event_valid():
    """Valid TimelineEvent must be created correctly."""
    event = TimelineEvent(date="April 1", event="Nominations open")
    assert event.date == "April 1"
    assert event.event == "Nominations open"


def test_timeline_event_missing_field_fails():
    """TimelineEvent without required fields must raise ValidationError."""
    with pytest.raises(ValidationError):
        TimelineEvent(date="April 1")


# ── QuizRequest ─────────────────────────────────────────────────────────────

def test_quiz_request_defaults():
    """QuizRequest must have correct defaults."""
    req = QuizRequest()
    assert req.country == "India"
    assert req.topic == "General Election Process"


def test_quiz_request_custom():
    """QuizRequest must accept custom country and topic."""
    req = QuizRequest(country="United States", topic="Electoral College")
    assert req.country == "United States"
    assert req.topic == "Electoral College"


# ── CompareRequest ──────────────────────────────────────────────────────────

def test_compare_request_valid():
    """Valid CompareRequest must be created without error."""
    req = CompareRequest(country1="India", country2="United States")
    assert req.country1 == "India"
    assert req.country2 == "United States"


def test_compare_request_missing_field_fails():
    """CompareRequest without both countries must raise ValidationError."""
    with pytest.raises(ValidationError):
        CompareRequest(country1="India")


# ── GlossaryTerm ────────────────────────────────────────────────────────────

def test_glossary_term_with_optional_example():
    """GlossaryTerm must work with and without optional example field."""
    t1 = GlossaryTerm(term="EVM", definition="Electronic Voting Machine")
    assert t1.example is None
    t2 = GlossaryTerm(term="EVM", definition="Electronic Voting Machine",
                      example="Used in all Indian elections since 1999")
    assert t2.example is not None
