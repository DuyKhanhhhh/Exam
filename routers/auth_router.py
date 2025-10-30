from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import SessionLocal
from schemas.auth import LoginReq, LoginResp
from schemas.user import UserCreate, UserResp
from services.auth_service import login as login_svc
from services.user_service import create_user, get_user_by_code

router = APIRouter(tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=LoginResp)
def login(payload: LoginReq, db: Session = Depends(get_db)):
    u = login_svc(db, payload.code, payload.password)
    if not u:
        raise HTTPException(status_code=401, detail="Sai mã hoặc mật khẩu hoặc chưa được duyệt")
    return u

@router.post("/register", response_model=UserResp)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_code(db, payload.code):
        raise HTTPException(status_code=400, detail="Mã người dùng đã tồn tại")
    user = create_user(db, payload)
    return user
