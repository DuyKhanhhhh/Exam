from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import SessionLocal
from schemas.auth import LoginReq, LoginResp
from services.auth_service import login as login_svc

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/login", response_model=LoginResp)
def login(payload: LoginReq, db: Session = Depends(get_db)):
    u = login_svc(db, payload.code, payload.password)
    if not u: raise HTTPException(401, "Sai mã hoặc mật khẩu")
    return u
