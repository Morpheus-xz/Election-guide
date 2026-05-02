# Civvy — AI Election Guide

> Built for **Google Prompt Wars 2026** · Powered by **Google Gemini 2.5 Flash**

An AI-powered, multi-country election education assistant.  
Ask anything about elections, take quizzes, compare countries, and explore 
glossaries — all in your language.

## 🔴 Live Demo
**[https://election-agent-3xsadc55rq-uc.a.run.app](https://election-agent-3xsadc55rq-uc.a.run.app)**

## 🎯 Challenge Vertical
**Civic Education Assistant** — Helps users understand election processes, 
timelines, and voting steps in an interactive, easy-to-follow way.

## ✨ Features

| Feature | Description |
|---------|-------------|
| Multi-turn Chat | Gemini 2.5 Flash with full conversation history + country-aware persona |
| 6 Countries | India, USA, UK, Australia, Canada, Other |
| 8 Languages | English, Hindi, Tamil, Telugu, Bengali, Marathi, Spanish, French |
| Quiz Mode | 5-question adaptive MCQ with explanations |
| Country Comparison | Side-by-side table across 6 electoral dimensions |
| Election Glossary | 15 country-specific terms, cached in memory per session |
| Visual Timelines | TIMELINE blocks extracted from AI responses → interactive UI |
| Translation | Real-time translation via Google Cloud Translation API v2 |
| Dark Mode | Persistent preference via localStorage |
| Voice Input | Web Speech API with language-mapped speech recognition |
| Share Cards | Download any AI answer as a PNG card |
| Accessibility | WCAG 2.1 AA — ARIA labels, keyboard nav, skip links, reduced motion |

## ☁️ Google Services

| Service | Purpose |
|---------|---------|
| **Gemini 2.5 Flash** | Core AI — chat, quiz, comparisons, glossary, election facts |
| **Google Cloud Run** | Serverless deployment — auto-scaling, HTTPS, min-instances=1 |
| **Google Secret Manager** | Secure API key injection — `GEMINI_API_KEY` at runtime |
| **Google Cloud Build** | 6-step CI/CD — build, push (SHA+latest), deploy, log, health-check |
| **Google Cloud Logging** | Structured request logs — every API call logged to GCP |
| **Google Cloud Translation API** | POST /translate — real-time translation into 8 languages |
| **Google Container Registry** | Docker image storage with immutable SHA tags |
| **Google Fonts** | Playfair Display, Source Sans 3, Noto scripts for regional languages |

## 🔒 Security

- **OWASP headers** on every response: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`, `Strict-Transport-Security`, `Referrer-Policy`, `Permissions-Policy`
- **Rate limiting**: 30 requests/minute per IP on `/chat` (slowapi)
- **Input validation**: Pydantic rejects empty, blank, and oversized messages
- **Exponential backoff**: Tenacity retries Gemini calls up to 3 times
- **Non-root container**: Dockerfile runs as `appuser`, not root
- **No secrets in code**: All keys via Secret Manager environment injection
- **XSS protection**: `renderMarkdown()` HTML-encodes `&`, `<`, `>` before rendering

## ⚡ Efficiency

- Async throughout — all Gemini calls via `asyncio.to_thread()`, non-blocking
- Glossary caching — in-memory per country, zero redundant Gemini calls
- Singleton Gemini client — initialized once at module load, reused across requests
- History trimming — only last 20 turns sent to Gemini (MAX_HISTORY_TURNS)
- Docker layer caching — `requirements.txt` copied before source

## 🧪 Testing

```bash
# Run all 86 tests (no API key needed — all Gemini calls mocked)
GEMINI_API_KEY=test-key pytest tests/ -v

# With coverage
GEMINI_API_KEY=test-key pytest tests/ --cov=app --cov-report=term-missing
```

| Test File | Coverage |
|-----------|----------|
| `test_health.py` | `/health`, `/countries` endpoints |
| `test_chat.py` | Happy path, validation, edge cases, error handling, Unicode |
| `test_parser.py` | Timeline/follow-up extraction, reply cleaning |
| `test_models.py` | All Pydantic models and field validators |
| `test_glossary_quiz.py` | `/quiz`, `/compare`, `/glossary`, `/fact`, caching |
| `test_config.py` | Configuration constants |
| `test_security.py` | Security headers, `/translate` validation |

## ♿ Accessibility

- WCAG 2.1 AA compliant
- `role="log"` + `aria-live="polite"` on chat window
- All interactive elements have `aria-label`
- Skip navigation link at top of page
- Full keyboard navigation — Tab, Enter, Escape, focus trapping in modals
- `prefers-reduced-motion` media query respected
- Noto fonts loaded for Devanagari, Tamil, Telugu, Bengali scripts

## 🏗️ Architecture

```
Browser (HTML/CSS/JS)
│
▼
Google Cloud Run (FastAPI / Python 3.11)
│
┌────┴─────────────────────┐
▼                          ▼
Gemini 2.5 Flash     Google Cloud Translation
(chat/quiz/compare)  (POST /translate)
│
┌────┴────────────────┐
▼                     ▼
Secret Manager    Cloud Logging
(API keys)       (request logs)
```

## 🚀 Local Development

```bash
git clone https://github.com/Morpheus-xz/Election-guide.git
cd Election-guide
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
uvicorn app.main:app --reload --port 8080
# Open http://localhost:8080
```

## ☁️ Deploy to Cloud Run

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable all required Google APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  containerregistry.googleapis.com \
  translate.googleapis.com \
  logging.googleapis.com

# Store Gemini API key securely in Secret Manager
echo -n "YOUR_GEMINI_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Grant Cloud Run access to Translation API
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) \
  --format='value(projectNumber)')
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudtranslate.user"

# Build and deploy via 6-step Cloud Build pipeline
# Pass COMMIT_SHA for immutable image tagging
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=COMMIT_SHA=$(git rev-parse HEAD)
```

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service liveness, model info, version |
| GET | `/countries` | Supported country metadata |
| POST | `/chat` | Main conversational AI endpoint (30 req/min rate limited) |
| POST | `/quiz` | Generate 5-question MCQ quiz |
| POST | `/compare` | Compare two countries across 6 dimensions |
| GET | `/glossary?country=` | 15 election terms (cached per country) |
| GET | `/fact?country=` | One surprising election fact |
| POST | `/translate` | Translate text via Google Cloud Translation API |

## 📁 Project Structure

```
.
├── app/
│   ├── __init__.py         # Package export (exposes app instance)
│   ├── config.py           # All constants, supported countries/languages
│   ├── main.py             # FastAPI app, Gemini helpers, all endpoints
│   └── prompt.py           # Civvy system prompt with {country} placeholder
├── tests/
│   ├── conftest.py         # Shared fixtures, mocked Gemini calls
│   ├── test_health.py      # /health and /countries
│   ├── test_chat.py        # /chat — all paths, validation, edge cases
│   ├── test_parser.py      # Response parser unit tests
│   ├── test_models.py      # Pydantic model validation
│   ├── test_glossary_quiz.py # /quiz, /compare, /glossary, /fact
│   ├── test_config.py      # Configuration constants
│   └── test_security.py    # Security headers, /translate validation
├── static/
│   ├── index.html          # Accessible single-page app
│   ├── style.css           # CSS custom properties, dark mode, animations
│   └── script.js           # UI logic, API calls, quiz/compare/glossary
├── Dockerfile              # Non-root user, HEALTHCHECK, layer caching
├── cloudbuild.yaml         # 6-step build + deploy + log + health check
├── pytest.ini              # Test runner configuration
├── Makefile                # make test, make lint, make run
└── README.md
```

## 📄 License
Educational use only. Nonpartisan and unaffiliated with any government.
