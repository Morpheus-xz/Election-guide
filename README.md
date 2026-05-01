# Civvy — AI Election Guide

An AI-powered, multi-country election education assistant built for **Google Prompt Wars 2026**.  
Ask anything about election processes, take quizzes, compare countries, and explore glossaries — all in your language.

## Features

- **Multi-turn Chat** — Conversational AI (Gemini 2.5 Flash) with full history and country-aware system prompt
- **8 Languages** — English, Hindi, Tamil, Telugu, Bengali, Marathi, Spanish, French
- **6 Countries** — India, United States, United Kingdom, Australia, Canada, and a general "Other" mode
- **Quiz Mode** — 5-question adaptive MCQ quiz with explanations
- **Country Comparison** — Side-by-side table across 6 electoral dimensions
- **Election Glossary** — 15 country-specific terms with definitions and examples (cached per session)
- **Did You Know** — Surprising election facts refreshed on demand
- **Visual Timeline** — Structured TIMELINE blocks extracted from AI responses
- **Dark Mode** — Persistent via localStorage
- **Voice Input** — Web Speech API with language-mapped recognition
- **Share Card** — Download any AI answer as a PNG card

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Pydantic v2 |
| AI | Google Gemini 2.5 Flash (`google-genai` SDK) |
| Retry | Tenacity (exponential backoff, 3 attempts) |
| Frontend | Vanilla JS, HTML5, CSS3 (custom properties) |
| Deployment | Google Cloud Run (serverless) |
| Secrets | Google Secret Manager |
| CI/CD | Google Cloud Build |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service liveness + model info |
| GET | `/countries` | Supported country metadata |
| POST | `/chat` | Main conversational endpoint |
| POST | `/quiz` | Generate 5-question MCQ quiz |
| POST | `/compare` | Compare two countries across 6 dimensions |
| GET | `/glossary?country=` | 15 election terms (cached) |
| GET | `/fact?country=` | One surprising election fact |

## Local Development

```bash
# 1. Clone
git clone https://github.com/Morpheus-xz/Election-guide.git
cd Election-guide

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
export GEMINI_API_KEY=your_key_here

# 4. Run
uvicorn app.main:app --reload --port 8080
```

Open [http://localhost:8080](http://localhost:8080)

## Deploy to Cloud Run

```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Store API key in Secret Manager
echo -n "YOUR_GEMINI_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Build and deploy
gcloud builds submit --config cloudbuild.yaml
```

## Project Structure

```
.
├── app/
│   ├── config.py      # Constants, supported countries/languages
│   ├── main.py        # FastAPI app, Gemini helpers, all endpoints
│   └── prompt.py      # System prompt with {country} placeholder
├── static/
│   ├── index.html     # Single-page app shell
│   ├── style.css      # CSS custom properties, dark mode, animations
│   └── script.js      # All UI logic, API calls, quiz/compare/glossary
├── Dockerfile
├── cloudbuild.yaml
└── requirements.txt
```

## License

Educational use. Nonpartisan and unaffiliated with any government or political body.
