
# Financial Document Analyzer — CrewAI + Queue + DB

**What this includes**
- Fixed, working API (FastAPI) and PDF parsing (PyPDF2)
- Inefficient prompts → replaced with **JSON-first** + concise Markdown
- **CrewAI** agent pipeline (toggle via `ANALYZER_PROVIDER`)
- **Celery + Redis** queue for concurrent jobs
- **SQLAlchemy** DB (SQLite by default) persisting users & analyses
- Docker + docker-compose + Postman collection + smoke tests

## Quickstart
```bash
cp .env.sample .env
docker compose up --build -d
# API at http://localhost:8000
```

Local dev:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
docker run -p 6379:6379 redis:7-alpine
celery -A app.celery_app.celery_app worker --loglevel=info
uvicorn app.main:app --reload
```

## API
- `POST /analyze` (multipart: file, query?, user_email?) → returns `{job_id, analysis_id, status}`
- `GET /jobs/{job_id}` → job state/result
- `GET /analyses/{id}` → persisted result
- `GET /health` → sanity check

## Schema
- users(id, email, api_key)
- analyses(id, user_id, file_hash, filename, result_json, status, created_at)

## Analyzer Provider
Set `ANALYZER_PROVIDER=crewai|openai|fallback` in `.env`.


---

## ✅ Assignment Checklist Mapping

- **Deterministic bugs fixed** → See **BUGS.md** and sections below
- **Inefficient prompts fixed** → JSON-first contract + concise Markdown
- **Working code** → FastAPI app with /analyze, /jobs, /analyses, /health
- **README** → Setup, usage, API docs, bug log, prompt rationale
- **Bonus** → Celery + Redis queue, SQLAlchemy DB (SQLite default)
- **CrewAI** → Integrated; toggle via `ANALYZER_PROVIDER=crewai`

---

## 🧩 Architecture (High-Level)

```mermaid
flowchart LR
  U[User / Client] -->|POST /analyze| API[FastAPI API]
  API -->|enqueue| Q[(Redis Queue)]
  W[Celery Worker] --> DB[(SQLite / SQLAlchemy)]
  W --> FS[(Uploads)]
  Q --> W
  W -->|save result| DB
  U -->|GET /jobs/{id}| API
  U -->|GET /analyses/{id}| API --> DB
```

---

## 🧪 Testing & Postman

- Run `pytest -q` for a smoke test.
- Import **postman/FinDocAnalyzer.postman_collection.json** into Postman.
- Example responses are in **/screenshots**.

---

## 💡 Prompt Redesign (Before → After)

**Before (inefficient/vague):**
> "Summarize this financial doc and tell if it's good to invest."

**After (deterministic & safe):**
> Return a **JSON** with keys: `company, period, revenue, operating_income, net_income, ebitda, eps, guidance, cash_flow, highlights[], risks[]` (unknown → null).  
> Then include a **concise Markdown** summary (3–6 bullets). **Do not** give financial advice.

**Why**: Forces a parseable structure, reduces hallucinations, speeds evaluation, stays policy-safe.

---

## 🚀 GitHub Submission (copy-paste)

```bash
# inside the project directory
git init
git add .
git commit -m "feat: CrewAI + Celery + Redis + SQLAlchemy; fixed bugs; deterministic prompts"
# replace the <repo-url> with your new GitHub repo URL
git branch -M main
git remote add origin <repo-url>
git push -u origin main
```

For screenshots on README, see **/screenshots** directory.
