import os, json, tempfile
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .database import get_db, init_db
from .models import Analysis
from .tasks import analyze_pdf_task

app = FastAPI(title="Financial Document Analyzer (CrewAI + Queue + DB)")

@app.on_event("startup")
def _startup(): init_db()

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...), query: Optional[str] = Form(None),
                           user_email: Optional[str] = Form(None), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="uploads") as tmp:
        content = await file.read(); tmp.write(content); tmp_path = tmp.name
    row = Analysis(filename=file.filename, status="queued"); db.add(row); db.commit(); db.refresh(row)
    task = analyze_pdf_task.delay(row.id, tmp_path, query, user_email)
    return {"job_id": task.id, "analysis_id": row.id, "status": "queued"}

@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    from celery.result import AsyncResult
    res = AsyncResult(job_id); data = {"id": job_id, "state": res.state}
    if res.successful(): data["result"] = res.result
    elif res.failed(): data["error"] = str(res.result)
    return data

@app.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    row = db.query(Analysis).get(analysis_id)
    if not row: raise HTTPException(status_code=404, detail="Not found")
    return JSONResponse({
        "id": row.id, "status": row.status, "filename": row.filename,
        "file_hash": row.file_hash, "created_at": row.created_at.isoformat(),
        "result": json.loads(row.result_json) if row.result_json else None
    })
