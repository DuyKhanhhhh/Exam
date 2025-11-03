from fastapi import Depends
from sqlalchemy.orm import Session
from models.user import User
from repositories import user_repo
from core.db import get_db as get_db_dep

def login(db: Session, code: str, password: str):
    user = db.query(User).filter(User.code == code, User.password == password).first()
    if not user:
        return None
    if user.status != "approved":
        return None
    return {
        "id": user.id,
        "code": user.code,
        "name": user.name,
        "role": user.role,
        "status": user.status,
    }
def get_current_user(
    db: Session = Depends(get_db_dep),
):
    from fastapi import Request
    def real_get_current_user(request: Request, db: Session = Depends(get_db_dep)):
        user_id = request.session.get("user_id")
        if not user_id:
            return None
        user = user_repo.get_user(db, user_id)
        return user
    return real_get_current_user