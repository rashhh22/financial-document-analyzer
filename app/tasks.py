import json, hashlib, os
from sqlalchemy.orm import Session
from .celery_app import celery_app
from .tools import read_pdf_text
from .analyze import analyze_text
from .database import SessionLocal
from . import models

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

@celery_app.task(name="analyze_pdf_task")
def analyze_pdf_task(analysis_id: int, file_path: str, query: str | None, user_email: str | None):
    db: Session = SessionLocal()
    try:
        user_id = None
        if user_email:
            user = db.query(models.User).filter(models.User.email == user_email).one_or_none()
            if not user:
                user = models.User(email=user_email, api_key=None)
                db.add(user); db.commit(); db.refresh(user)
            user_id = user.id

        row = db.query(models.Analysis).get(analysis_id)
        if not row: return {"error": "analysis row missing"}
        row.status = "processing"; 
        if user_id and not row.user_id: row.user_id = user_id
        db.commit()

        file_hash = _sha256_file(file_path); row.file_hash = file_hash; db.commit()

        text = read_pdf_text(file_path)
        result = analyze_text(text, query)
        payload = {"json": result.get("json"), "markdown": result.get("markdown"),
                   "meta": {"file_hash": file_hash, "filename": row.filename, "query": query}}
        row.result_json = json.dumps(payload, ensure_ascii=False); row.status = "done"; db.commit()
        return {"status": "done", "analysis_id": analysis_id}
    except Exception as e:
        try:
            row = db.query(models.Analysis).get(analysis_id)
            if row:
                row.status = "error"; row.result_json = json.dumps({"error": str(e)}); db.commit()
        except Exception: pass
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
        try:
            if os.path.exists(file_path): os.remove(file_path)
        except Exception: pass
