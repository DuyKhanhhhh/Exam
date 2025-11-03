from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from core.db import SessionLocal
from schemas.user import UserCreate, UserUpdate, UserResp
from repositories import user_repo
from services import user_service
from services.auth_service import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserResp)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return user_service.register(db, payload.code, payload.name, payload.password, payload.email)

@router.get("/", response_model=List[UserResp])
def list_users(db: Session = Depends(get_db)):
    return user_repo.list_users(db)

@router.put("/{user_id}/approve", response_model=UserResp)
def approve_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.approve(db, user_id)

@router.put("/{user_id}/reject", response_model=UserResp)
def reject_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.reject(db, user_id)

@router.put("/{user_id}", response_model=UserResp)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    u = user_repo.update_user(db, user_id, payload.dict(exclude_unset=True))
    if not u:
        raise HTTPException(404, "Không tìm thấy người dùng")
    return u

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    ok = user_repo.delete_user(db, user_id)
    if not ok:
        raise HTTPException(404, "Không tìm thấy người dùng")
    return {"success": True}
@router.post("/", response_model=UserResp, status_code=status.HTTP_201_CREATED)
def create_user_by_admin(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Chỉ quản trị viên mới được tạo tài khoản")

    if user_repo.get_user_by_code(db, payload.code):
        raise HTTPException(400, "Mã người dùng đã tồn tại")

    data = payload.dict()
    data["status"] = "approved"
    data["role"] = payload.role or "student"

    return user_repo.create_user(db, data)