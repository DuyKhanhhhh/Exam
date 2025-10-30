import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db
from models.user import User
from pydantic import BaseModel
from typing import List
router = APIRouter(prefix="/users", tags=["users"])

# ====== SCHEMAS ======
class UserCreate(BaseModel):
    code: str
    name: str
    password: str
    role: str = "student"

class UserOut(BaseModel):
    id: int
    code: str
    name: str
    role: str
    is_approved: bool
    created_at: int

    class Config:
        orm_mode = True


# ====== API: Đăng ký tài khoản ======
@router.post("/register", response_model=UserOut)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    exist = db.query(User).filter(User.code == data.code).first()
    if exist:
        raise HTTPException(status_code=400, detail="Mã người dùng đã tồn tại")

    user = User(
        code=data.code,
        name=data.name,
        password=data.password,  # Có thể mã hóa sau
        role=data.role,
        created_at=int(time.time()),
        is_approved=False,  # phải được admin duyệt
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ====== API: Lấy danh sách người dùng (Admin) ======
@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# ====== API: Duyệt tài khoản ======
@router.put("/{user_id}/approve", response_model=UserOut)
def approve_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    user.is_approved = True
    db.commit()
    db.refresh(user)
    return user


# ====== API: Xóa tài khoản ======
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    db.delete(user)
    db.commit()
    return {"ok": True}
