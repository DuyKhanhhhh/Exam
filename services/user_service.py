from sqlalchemy.orm import Session
from models.user import User

def list_users(db: Session):
    return db.query(User).all()

def approve_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.is_approved = True
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True

def create_user(db: Session, code: str, name: str, password: str, role: str = "student"):
    user = User(code=code, name=name, password=password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_code(db: Session, code: str):
    return db.query(User).filter(User.code == code).first()