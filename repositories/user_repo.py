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
