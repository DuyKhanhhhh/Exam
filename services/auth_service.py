from sqlalchemy.orm import Session
from repositories.user_repo import get_by_code

def login(db: Session, code: str, password: str):
    u = get_by_code(db, code)
    if not u or u.password != password:
        return None
    return {"code": u.code, "name": u.name, "role": u.role}
