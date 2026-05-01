"""
Civvy Election Guide — FastAPI Backend  v3.0.0
Handles all AI interactions, response parsing, and structured endpoints.
"""

import asyncio
import json
import logging
import os
import re
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from google import genai
from google.genai import types

from app.config import (
    APP_NAME,
    GEMINI_MODEL,
    MAX_MESSAGE_LENGTH,
    MAX_RETRIES,
    SUPPORTED_COUNTRIES,
    VERSION,
)
from app.prompt import SYSTEM_ACK, SYSTEM_PROMPT

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title=APP_NAME, version=VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Gemini client (initialised once at import time) ─────────────────────────
_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# ─── Module-level cache for glossary (slow to generate, rarely changes) ──────
_glossary_cache: dict[str, list[dict]] = {}


# ══════════════════════════════════════════════════════════════════════════════
# Pydantic Models
# ══════════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, Any]] = []
    country: str = "India"
    language: str = "English"

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Reject empty or oversized messages at the boundary."""
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty.")
        if len(v) > MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message exceeds {MAX_MESSAGE_LENGTH} characters.")
        return v


class TimelineEvent(BaseModel):
    date: str
    event: str


class ChatResponse(BaseModel):
    reply: str
    timeline: list[TimelineEvent] | None = None
    follow_up: str | None = None
    related_topics: list[str] | None = None
    confidence: str | None = None


class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct: str
    explanation: str


class QuizRequest(BaseModel):
    country: str = "India"
    topic: str = "General Election Process"


class QuizResponse(BaseModel):
    questions: list[QuizQuestion]


class CompareRequest(BaseModel):
    country1: str
    country2: str


class ComparisonAspect(BaseModel):
    aspect: str
    country1: str
    country2: str
    winner: str | None = None   # "country1" | "country2" | "neither"
    reason: str | None = None


class ComparisonResponse(BaseModel):
    aspects: list[ComparisonAspect]
    summary: str


class GlossaryTerm(BaseModel):
    term: str
    definition: str
    example: str | None = None


class FactResponse(BaseModel):
    fact: str


class CountryInfo(BaseModel):
    name: str
    flag: str
    election_system: str


class HealthResponse(BaseModel):
    status: str
    model: str
    version: str
    app_name: str


# ══════════════════════════════════════════════════════════════════════════════
# Gemini Helpers
# ══════════════════════════════════════════════════════════════════════════════

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    reraise=True,
)
def _gemini_sync(contents: list[types.Content]) -> str:
    """
    Synchronous Gemini call with exponential-backoff retry.
    Wraps the blocking SDK call so it can be offloaded to a thread pool.
    """
    return _client.models.generate_content(model=GEMINI_MODEL, contents=contents).text


async def _gemini(contents: list[types.Content]) -> str:
    """Async wrapper — runs the blocking call in FastAPI's default thread pool."""
    return await asyncio.to_thread(_gemini_sync, contents)


async def _gemini_json(prompt: str) -> Any:
    """
    Call Gemini with a JSON-output prompt and parse the result.
    Strips markdown code fences that the model sometimes adds.
    """
    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    raw = await _gemini(contents)
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw.strip(), flags=re.MULTILINE)
    return json.loads(raw.strip())


# ══════════════════════════════════════════════════════════════════════════════
# Response Parser
# ══════════════════════════════════════════════════════════════════════════════

def _parse_chat_response(
    text: str,
) -> tuple[str, list[dict] | None, str | None]:
    """
    Extract structured TIMELINE and FOLLOW_UP blocks from Civvy's raw text.
    Returns (clean_reply, timeline_events_or_None, follow_up_or_None).
    """
    timeline: list[dict] | None = None
    follow_up: str | None = None
    clean = text

    # ── Extract TIMELINE block ────────────────────────────────────────────
    tl_match = re.search(
        r"TIMELINE:\s*\n((?:[^\n]*📅[^\n]*\n?)+)", clean, re.MULTILINE
    )
    if tl_match:
        events: list[dict] = []
        for line in tl_match.group(1).strip().split("\n"):
            line = line.strip()
            if "📅" not in line:
                continue
            line = line.replace("📅", "").strip()
            for sep in [" — ", " – ", " - ", "—", "–"]:
                if sep in line:
                    date_part, event_part = line.split(sep, 1)
                    events.append(
                        {"date": date_part.strip(), "event": event_part.strip()}
                    )
                    break
        if events:
            timeline = events
        clean = re.sub(r"TIMELINE:\s*\n(?:[^\n]*📅[^\n]*\n?)+", "", clean)

    clean = re.sub(r"TIMELINE:\s*", "", clean)

    # ── Extract FOLLOW_UP line ────────────────────────────────────────────
    fu_match = re.search(r"FOLLOW_UP:\s*(.+?)(?:\n|$)", clean)
    if fu_match:
        follow_up = fu_match.group(1).strip()
    clean = re.sub(r"FOLLOW_UP:\s*.+?(?:\n|$)", "", clean)

    clean = re.sub(r"\n{3,}", "\n\n", clean).strip()
    return clean, timeline, follow_up


def _build_gemini_history(
    history: list[dict[str, Any]], country: str, language: str
) -> list[types.Content]:
    """
    Assemble the full Gemini conversation: system persona first, then
    prior turns. The system prompt is re-injected every request so the
    persona stays consistent regardless of conversation length.
    """
    system_prompt = SYSTEM_PROMPT.replace("{country}", country)
    system_ack = SYSTEM_ACK.replace("{country}", country)

    if language and language.lower() != "english":
        system_prompt += (
            f"\n\nIMPORTANT: Always respond in {language} language. "
            f"Keep your explanations clear and simple in {language}."
        )

    gemini_history: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=system_prompt)]),
        types.Content(role="model", parts=[types.Part(text=system_ack)]),
    ]

    for entry in history:
        role = entry.get("role", "user")
        parts = entry.get("parts", [])
        if isinstance(parts, list) and parts:
            gemini_history.append(
                types.Content(role=role, parts=[types.Part(text=str(parts[0]))])
            )

    return gemini_history


# ══════════════════════════════════════════════════════════════════════════════
# Routes
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/health", response_model=HealthResponse, tags=["meta"])
async def health_check() -> HealthResponse:
    """Service liveness check — returns model name and app version."""
    return HealthResponse(
        status="ok", model=GEMINI_MODEL, version=VERSION, app_name=APP_NAME
    )


@app.get("/countries", response_model=list[CountryInfo], tags=["meta"])
async def list_countries() -> list[CountryInfo]:
    """Returns metadata for every supported country."""
    return [
        CountryInfo(
            name=name,
            flag=info["flag"],
            election_system=info["election_system"],
        )
        for name, info in SUPPORTED_COUNTRIES.items()
    ]


@app.post("/chat", response_model=ChatResponse, tags=["ai"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main conversational endpoint. Accepts a user message and prior
    history, calls Gemini with full country + language context, and
    returns a structured response with optional timeline and follow-up.
    """
    t0 = time.monotonic()
    logger.info(
        "CHAT | country=%s | lang=%s | msg_len=%d | turns=%d",
        request.country,
        request.language,
        len(request.message),
        len(request.history),
    )

    contents = _build_gemini_history(
        request.history, request.country, request.language
    ) + [types.Content(role="user", parts=[types.Part(text=request.message)])]

    try:
        raw = await _gemini(contents)
    except Exception as exc:
        logger.error("Gemini chat failed after %d retries: %s", MAX_RETRIES, exc)
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")

    clean, timeline, follow_up = _parse_chat_response(raw)
    logger.info("CHAT OK | %.0f ms", (time.monotonic() - t0) * 1000)

    return ChatResponse(
        reply=clean,
        timeline=[TimelineEvent(**e) for e in timeline] if timeline else None,
        follow_up=follow_up,
    )


@app.post("/quiz", response_model=QuizResponse, tags=["ai"])
async def generate_quiz(request: QuizRequest) -> QuizResponse:
    """
    Generates a 5-question multiple-choice quiz about the given country's
    election process. Returns structured questions with answer options,
    the correct answer letter, and an explanation.
    """
    logger.info("QUIZ | country=%s | topic=%s", request.country, request.topic)

    prompt = f"""You are an election education expert. Generate a 5-question multiple-choice quiz about "{request.topic}" in {request.country}'s election system.

Return ONLY a valid JSON object — no text before or after:
{{
  "questions": [
    {{
      "question": "question text here",
      "options": ["A) first option", "B) second option", "C) third option", "D) fourth option"],
      "correct": "A",
      "explanation": "1-2 sentence explanation of why the answer is correct"
    }}
  ]
}}

Requirements:
- All 5 questions must be specific to {request.country}'s actual laws and election processes
- Each question must have exactly 4 options labelled A), B), C), D)
- The "correct" field contains only the letter: A, B, C, or D
- Questions should vary in difficulty (2 easy, 2 medium, 1 hard)"""

    try:
        data = await _gemini_json(prompt)
        return QuizResponse(
            questions=[QuizQuestion(**q) for q in data.get("questions", [])]
        )
    except Exception as exc:
        logger.error("Quiz generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Quiz generation failed: {exc}")


@app.post("/compare", response_model=ComparisonResponse, tags=["ai"])
async def compare_countries(request: CompareRequest) -> ComparisonResponse:
    """
    Compares two countries' election systems across 6 standardised
    dimensions. Returns a structured table of aspects plus a summary.
    """
    logger.info("COMPARE | %s vs %s", request.country1, request.country2)

    prompt = f"""Compare the election systems of {request.country1} and {request.country2} across exactly these 6 aspects:
1. Voting System
2. Voter Registration
3. Election Frequency
4. Campaign Finance Rules
5. Vote Counting Method
6. Voter Participation Mechanism

Return ONLY a valid JSON object — no text before or after:
{{
  "aspects": [
    {{
      "aspect": "Voting System",
      "country1": "description of {request.country1}'s approach (max 15 words)",
      "country2": "description of {request.country2}'s approach (max 15 words)",
      "winner": "country1 or country2 or neither",
      "reason": "one sentence highlighting the key difference"
    }}
  ],
  "summary": "2-3 sentence balanced comparison of both systems overall"
}}

Be factual and nonpartisan."""

    try:
        data = await _gemini_json(prompt)
        return ComparisonResponse(
            aspects=[ComparisonAspect(**a) for a in data.get("aspects", [])],
            summary=data.get("summary", ""),
        )
    except Exception as exc:
        logger.error("Comparison failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Comparison failed: {exc}")


@app.get("/glossary", response_model=list[GlossaryTerm], tags=["ai"])
async def get_glossary(
    country: str = Query(default="India", description="Country to fetch terms for"),
) -> list[GlossaryTerm]:
    """
    Returns 15 essential election terms for the given country.
    Results are cached in memory after the first call to avoid
    redundant Gemini calls (glossaries rarely change mid-session).
    """
    if country in _glossary_cache:
        logger.info("GLOSSARY | cache hit | country=%s", country)
        return [GlossaryTerm(**t) for t in _glossary_cache[country]]

    logger.info("GLOSSARY | cache miss | country=%s", country)

    prompt = f"""List exactly 15 essential election terms used in {country}'s election system.

Return ONLY a valid JSON array — no text before or after:
[
  {{
    "term": "Term Name",
    "definition": "clear, jargon-free definition in 1-2 sentences",
    "example": "brief real-world example of how this term applies in {country}"
  }}
]

Include terms specific to {country}: key bodies, laws, processes, and unique concepts."""

    try:
        data = await _gemini_json(prompt)
        _glossary_cache[country] = data
        return [GlossaryTerm(**t) for t in data]
    except Exception as exc:
        logger.error("Glossary failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Glossary generation failed: {exc}")


@app.get("/fact", response_model=FactResponse, tags=["ai"])
async def get_fact(
    country: str = Query(default="India", description="Country to fetch a fact for"),
) -> FactResponse:
    """
    Returns one surprising, specific election fact for the given country.
    Not cached — each call returns a fresh, potentially different fact.
    """
    logger.info("FACT | country=%s", country)

    prompt = f"""Give me one surprising, little-known, and specific fact about {country}'s election system.

Rules:
- Maximum 2 sentences total
- Must cite specific numbers, dates, or laws where possible
- Must be genuinely non-obvious — not something every person already knows
- Must be directly about {country}'s election process

Return ONLY a valid JSON object — no text before or after:
{{"fact": "your interesting fact here"}}"""

    try:
        data = await _gemini_json(prompt)
        return FactResponse(fact=data.get("fact", ""))
    except Exception as exc:
        logger.error("Fact generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Fact generation failed: {exc}")


# ─── Static files (mounted after all API routes) ──────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def serve_index() -> FileResponse:
    """Serve the Civvy single-page application."""
    return FileResponse("static/index.html")
