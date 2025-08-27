
# Bugs Found & How They Were Fixed

## 1) Undefined / Misconfigured LLM Client
**Symptom:** `llm = llm` or missing provider caused runtime NameError.  
**Fix:** Centralized provider in `app/analyze.py` with `ANALYZER_PROVIDER` env flag. Supports `crewai`, `openai`, `fallback`.

## 2) Async vs Sync Tool Misuse
**Symptom:** Async PDF tool never awaited; downstream code expected sync.  
**Fix:** Replaced with a **sync** `read_pdf_text` (PyPDF2) and robust exception handling.

## 3) Broken Endpoint Wiring
**Symptom:** `/analyze` saved files but never tracked their job lifecycle; missing DB persistence.  
**Fix:** Added SQLAlchemy models (`users`, `analyses`), created row on enqueue, stored result JSON/status.

## 4) Inefficient / Risky Prompts
**Symptom:** Vague instructions yielded inconsistent outputs and advice-like content.  
**Fix:** JSON-first required keys + concise Markdown; no advice. Deterministic fallback when no LLM key present.

## 5) Missing Queue Mechanics
**Symptom:** Concurrency caused race conditions; jobs blocked API.  
**Fix:** Added **Celery + Redis**. `/analyze` enqueues → worker processes → `/jobs/{id}` polls status.

## 6) Error Handling & Cleanup
**Symptom:** Uploaded files lingered; unhandled exceptions.  
**Fix:** Consistent try/except, DB state transitions (`queued → processing → done/error`), uploads cleaned in worker finally-block.
