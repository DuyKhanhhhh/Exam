from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories import user_repo

def register(db: Session, code, name, password, email=None):
    if user_repo.get_user_by_code(db, code):
        raise HTTPException(400, "Mã đăng nhập đã tồn tại")

    data = {
        "code": code,
        "name": name,
        "email": email,
        "password": password,
        "role": "student",
        "status": "pending",
    }
    return user_repo.create_user(db, data)

def approve(db: Session, user_id: int):
    u = user_repo.update_user(db, user_id, {"status": "approved"})
    if not u:
        raise HTTPException(404, "Không tìm thấy người dùng")
    return u

def reject(db: Session, user_id: int):
    u = user_repo.update_user(db, user_id, {"status": "rejected"})
    if not u:
        raise HTTPException(404, "Không tìm thấy người dùng")
    return u
