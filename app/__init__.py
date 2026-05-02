"""
Civvy Election Guide — Application Package

This package exposes the FastAPI application instance for use by
uvicorn, test runners, and any future WSGI/ASGI adapters.

Modules:
    main    — FastAPI app, all route handlers, Gemini helpers
    config  — Application-wide constants and supported country data
    prompt  — System prompt templates for Civvy's AI persona
"""
from app.main import app

__all__ = ["app"]
