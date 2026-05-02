"""
Unit tests for the _parse_chat_response parser function.
Tests timeline extraction, follow-up extraction, and text cleaning.
"""
import pytest
from app.main import _parse_chat_response


# ── Timeline extraction ─────────────────────────────────────────────────────

def test_extracts_timeline_basic():
    """Parser must extract a basic TIMELINE block."""
    raw = (
        "Here is India's election timeline.\n\n"
        "TIMELINE:\n"
        "📅 March 1 — Nominations open\n"
        "📅 April 5 — Campaign period begins\n"
        "📅 April 19 — Polling day\n\n"
        "FOLLOW_UP: Want to know about polling booths?"
    )
    reply, timeline, follow_up = _parse_chat_response(raw)
    assert timeline is not None
    assert len(timeline) == 3
    assert timeline[0]["date"] == "March 1"
    assert timeline[0]["event"] == "Nominations open"


def test_extracts_timeline_with_dash_separator():
    """Parser must handle hyphen separator in timeline lines."""
    raw = "TIMELINE:\n📅 April 1 - Voting begins\n"
    _, timeline, _ = _parse_chat_response(raw)
    assert timeline is not None
    assert len(timeline) == 1


def test_no_timeline_returns_none():
    """Response without TIMELINE block must return None for timeline."""
    raw = "India uses First Past the Post.\nFOLLOW_UP: Want to know more?"
    _, timeline, _ = _parse_chat_response(raw)
    assert timeline is None


def test_empty_timeline_returns_none():
    """TIMELINE block with no valid lines must return None."""
    raw = "TIMELINE:\nThis has no dates.\nFOLLOW_UP: Continue?"
    _, timeline, _ = _parse_chat_response(raw)
    assert timeline is None


# ── Follow-up extraction ────────────────────────────────────────────────────

def test_extracts_follow_up():
    """Parser must extract text after FOLLOW_UP: marker."""
    raw = "Some answer.\nFOLLOW_UP: Would you like to know about EVMs?"
    _, _, follow_up = _parse_chat_response(raw)
    assert follow_up == "Would you like to know about EVMs?"


def test_no_follow_up_returns_none():
    """Response without FOLLOW_UP must return None."""
    raw = "India uses First Past the Post voting."
    _, _, follow_up = _parse_chat_response(raw)
    assert follow_up is None


def test_follow_up_stripped_of_whitespace():
    """Follow-up text must be stripped of surrounding whitespace."""
    raw = "Answer.\nFOLLOW_UP:   What about registration?   "
    _, _, follow_up = _parse_chat_response(raw)
    assert follow_up == "What about registration?"


# ── Reply cleaning ──────────────────────────────────────────────────────────

def test_reply_excludes_timeline_marker():
    """Cleaned reply must not contain the TIMELINE: marker."""
    raw = "Main answer.\nTIMELINE:\n📅 Jan 1 — Start\nFOLLOW_UP: More?"
    reply, _, _ = _parse_chat_response(raw)
    assert "TIMELINE:" not in reply


def test_reply_excludes_follow_up_marker():
    """Cleaned reply must not contain the FOLLOW_UP: marker."""
    raw = "Main answer.\nFOLLOW_UP: Continue?"
    reply, _, _ = _parse_chat_response(raw)
    assert "FOLLOW_UP:" not in reply


def test_reply_not_empty_after_cleaning():
    """Cleaned reply must not be empty when there is actual content."""
    raw = "India has one of the world's largest democratic elections.\nFOLLOW_UP: Want more?"
    reply, _, _ = _parse_chat_response(raw)
    assert len(reply.strip()) > 0


def test_reply_no_excessive_blank_lines():
    """Cleaned reply must not have more than 2 consecutive newlines."""
    raw = "Line one.\n\n\n\n\nLine two.\nFOLLOW_UP: More?"
    reply, _, _ = _parse_chat_response(raw)
    assert "\n\n\n" not in reply


# ── Combined extraction ─────────────────────────────────────────────────────

def test_full_response_with_all_fields():
    """Parser must correctly extract all fields from a complete response."""
    raw = (
        "India's election has multiple phases.\n\n"
        "1. Announcement\n2. Nominations\n3. Polling\n\n"
        "TIMELINE:\n"
        "📅 Week 1 — Announcement\n"
        "📅 Week 3 — Nominations close\n"
        "📅 Week 6 — Polling day\n\n"
        "FOLLOW_UP: Want to know how votes are counted?"
    )
    reply, timeline, follow_up = _parse_chat_response(raw)
    assert "India's election" in reply
    assert timeline is not None and len(timeline) == 3
    assert follow_up == "Want to know how votes are counted?"
    assert "TIMELINE:" not in reply
    assert "FOLLOW_UP:" not in reply
