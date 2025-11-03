from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from models.user import User

def get_by_code(db: Session, code: str) -> User | None:
    return db.execute(select(User).where(User.code==code)).scalar_one_or_none()

def upsert_from_csv(db: Session, rows: list[dict]):
    # rows: [{"code","name","password","role"}, ...]
    for r in rows:
        u = get_by_code(db, r["code"])
        if u:
            u.name = r["name"]; u.password = r["password"]; u.role = r["role"]
        else:
            db.add(User(code=r["code"], name=r["name"], password=r["password"], role=r["role"]))
    db.commit()
def list_users(db: Session):
    return db.query(User).all()

def get_user_by_code(db: Session, code: str):
    return db.query(User).filter(User.code == code).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, data: dict):
    u = User(**data)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def update_user(db: Session, user_id: int, data: dict):
    u = get_user(db, user_id)
    if not u:
        return None
    for k, v in data.items():
        setattr(u, k, v)
    db.commit()
    db.refresh(u)
    return u

def delete_user(db: Session, user_id: int):
    u = get_user(db, user_id)
    if not u:
        return False
    db.delete(u)
    db.commit()
    return True