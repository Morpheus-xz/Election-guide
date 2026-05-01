import os
import re
import traceback
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from google import genai
from google.genai import types

from app.prompt import SYSTEM_PROMPT, SYSTEM_ACK

app = FastAPI(title="Election Agent — Civvy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL_ID = "gemini-2.5-flash"


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []
    country: str = "India"


class ChatResponse(BaseModel):
    reply: str
    timeline: Optional[List[Dict[str, str]]] = None
    follow_up: Optional[str] = None


def _parse_response(text: str):
    """Extract TIMELINE and FOLLOW_UP blocks from Gemini's response."""
    timeline = None
    follow_up = None
    clean = text

    # Extract TIMELINE block (lines containing 📅 after the TIMELINE: label)
    tl_match = re.search(
        r'TIMELINE:\s*\n((?:[^\n]*📅[^\n]*\n?)+)',
        clean,
        re.MULTILINE,
    )
    if tl_match:
        events = []
        for line in tl_match.group(1).strip().split('\n'):
            line = line.strip()
            if '📅' not in line:
                continue
            line = line.replace('📅', '').strip()
            for sep in [' — ', ' – ', ' - ', '—', '–']:
                if sep in line:
                    date_part, event_part = line.split(sep, 1)
                    events.append({'date': date_part.strip(), 'event': event_part.strip()})
                    break
        if events:
            timeline = events
        clean = re.sub(r'TIMELINE:\s*\n(?:[^\n]*📅[^\n]*\n?)+', '', clean)

    # Remove any leftover TIMELINE: label
    clean = re.sub(r'TIMELINE:\s*', '', clean)

    # Extract FOLLOW_UP line
    fu_match = re.search(r'FOLLOW_UP:\s*(.+?)(?:\n|$)', clean)
    if fu_match:
        follow_up = fu_match.group(1).strip()
    clean = re.sub(r'FOLLOW_UP:\s*.+?(?:\n|$)', '', clean)

    # Collapse excessive blank lines
    clean = re.sub(r'\n{3,}', '\n\n', clean).strip()

    return clean, timeline, follow_up


def _build_gemini_history(history: List[Dict[str, Any]], country: str) -> list:
    """Always prepend the system prompt so the persona is active every turn."""
    system_prompt = SYSTEM_PROMPT.replace('{country}', country)
    system_ack = SYSTEM_ACK.replace('{country}', country)

    gemini_history = [
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


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        user_message = request.message.strip()
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        country = (request.country or "India").strip()
        gemini_history = _build_gemini_history(request.history, country)

        response = _client.models.generate_content(
            model=MODEL_ID,
            contents=gemini_history + [
                types.Content(role="user", parts=[types.Part(text=user_message)])
            ],
        )

        raw_text = response.text
        clean_text, timeline, follow_up = _parse_response(raw_text)

        return ChatResponse(reply=clean_text, timeline=timeline, follow_up=follow_up)

    except HTTPException:
        raise
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Gemini API error: {str(exc)}",
        )


# Static files must be mounted AFTER API routes
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")
