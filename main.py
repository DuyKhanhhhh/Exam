from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pathlib import Path
import tempfile

from core.db import SessionLocal, Base, engine
from services.auth_service import login as auth_login
from repositories.question_repo import upsert_questions_from_csv
from models.exam import Upload as UploadModel
from pydantic import BaseModel
from routers import exams as exams_router, exams
from routers import results as results_router
from routers import upload
from routers import user_router


app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ensured.")

# -------- Include routers --------
app.include_router(exams_router.router)
app.include_router(results_router.router)
app.include_router(upload.router)
app.include_router(exams.router)
app.include_router(user_router.router)

# -------- CORS --------
origins = [
    "http://localhost:5173", "http://127.0.0.1:5173",
    "http://localhost:3000", "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- DB dependency --------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- Schemas & routes --------
class LoginIn(BaseModel):
    code: str
    password: str

@app.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    u = auth_login(db, payload.code, payload.password)
    if not u:
        raise HTTPException(status_code=401, detail="Sai mã hoặc mật khẩu")
    return u

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/upload")
async def upload_bank(
    file: UploadFile = File(...),
    subject: str = Form("math"),
    db: Session = Depends(get_db),
):
    suffix = Path(file.filename).suffix or ".csv"
    content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        created, updated = upsert_questions_from_csv(db, str(tmp_path), subject)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV lỗi: {e}")
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass

    try:
        log = UploadModel(
            subject=subject,
            filename=file.filename,
            csv_text=content.decode("utf-8", errors="ignore"),
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

    return {
        "ok": True,
        "subject": subject,
        "saved": created,
        "updated": updated,
        "count": created + updated,
    }
