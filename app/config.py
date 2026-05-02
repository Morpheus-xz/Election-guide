"""
Civvy Election Guide — Application Configuration

Single source of truth for all application constants.
Import from here — never hardcode values in other modules.

Usage:
    from app.config import GEMINI_MODEL, SUPPORTED_COUNTRIES
"""

APP_NAME: str = "Civvy - Election Guide"
VERSION: str = "4.0.0"
GEMINI_MODEL: str = "gemini-2.5-flash"
MAX_RETRIES: int = 3
MAX_MESSAGE_LENGTH: int = 500
MAX_HISTORY_TURNS: int = 20

SUPPORTED_COUNTRIES: dict[str, dict] = {
    "India": {
        "flag": "🇮🇳",
        "election_system": "Parliamentary democracy; First Past the Post; managed by the Election Commission of India",
        "stats": [
            {"label": "Lok Sabha Seats", "value": "543"},
            {"label": "Registered Voters", "value": "96.8 Cr"},
            {"label": "EVMs Since", "value": "1999"},
        ],
    },
    "United States": {
        "flag": "🇺🇸",
        "election_system": "Federal republic; Electoral College for president; state-run elections",
        "stats": [
            {"label": "Electoral Votes", "value": "538"},
            {"label": "To Win", "value": "270 votes"},
            {"label": "Election Cycle", "value": "4 years"},
        ],
    },
    "United Kingdom": {
        "flag": "🇬🇧",
        "election_system": "Parliamentary monarchy; First Past the Post; 650 MP constituencies",
        "stats": [
            {"label": "Commons Seats", "value": "650"},
            {"label": "Registered Voters", "value": "47 M+"},
            {"label": "Voting Age", "value": "18 years"},
        ],
    },
    "Australia": {
        "flag": "🇦🇺",
        "election_system": "Federal parliamentary democracy; compulsory preferential voting; AEC-managed",
        "stats": [
            {"label": "House Seats", "value": "151"},
            {"label": "Senate Seats", "value": "76"},
            {"label": "Voting", "value": "Compulsory"},
        ],
    },
    "Canada": {
        "flag": "🇨🇦",
        "election_system": "Federal parliamentary democracy; First Past the Post; Elections Canada",
        "stats": [
            {"label": "Commons Seats", "value": "338"},
            {"label": "Registered Voters", "value": "27 M+"},
            {"label": "Election Cycle", "value": "4 years"},
        ],
    },
    "Other": {
        "flag": "🌍",
        "election_system": "General election concepts and universal democratic principles explained",
        "stats": [
            {"label": "Coverage", "value": "Global"},
            {"label": "Focus", "value": "Principles"},
            {"label": "Approach", "value": "Universal"},
        ],
    },
}

SUPPORTED_LANGUAGES: list[str] = [
    "English",
    "Hindi",
    "Tamil",
    "Telugu",
    "Bengali",
    "Marathi",
    "Spanish",
    "French",
]
