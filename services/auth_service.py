from sqlalchemy.orm import Session
from models.user import User

def login(db: Session, code: str, password: str):
    user = db.query(User).filter(User.code == code, User.password == password).first()
    if user and user.is_approved:
        return {
            "id": user.id,
            "code": user.code,
            "name": user.name,
            "role": user.role
        }
    return None
