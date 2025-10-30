from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.db import SessionLocal
from services.user_service import list_users, approve_user, delete_user
from schemas.user import UserResp

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[UserResp])
def get_users(db: Session = Depends(get_db)):
    return list_users(db)

@router.put("/{user_id}/approve", status_code=status.HTTP_200_OK)
def approve(user_id: int, db: Session = Depends(get_db)):
    user = approve_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return {"message": f"Đã duyệt người dùng {user.name}"}

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_route(user_id: int, db: Session = Depends(get_db)):
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return {"message": f"Đã xóa user {user_id}"}
