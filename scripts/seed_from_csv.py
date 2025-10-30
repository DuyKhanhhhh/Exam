# scripts/seed_from_csv.py
from pathlib import Path
from dotenv import load_dotenv
import csv

from core.db import Base, engine, SessionLocal          # <-- KHÔNG còn app.*
from models.user import User                            # <-- import trực tiếp model

ROOT = Path(__file__).resolve().parents[1]  # thư mục gốc dự án (BE/)

def _open_csv(path: Path):
    for enc in ("utf-8-sig", "utf-8", "cp1258", "latin-1"):
        try:
            return open(path, newline="", encoding=enc)
        except UnicodeDecodeError:
            pass
    return open(path, newline="", encoding="utf-8-sig", errors="ignore")

def seed_users(session):
    p = ROOT / "user.csv"
    if not p.exists():
        print(f"⚠️  Không thấy {p}, bỏ qua seed users.")
        return
    with _open_csv(p) as f:
        r = csv.DictReader(f)
        n_ins = n_upd = 0
        for row in r:
            code = (row.get("code") or "").strip()
            if not code:
                continue
            u = session.query(User).filter(User.code == code).one_or_none()
            if u:
                u.name = (row.get("name") or "").strip()
                u.password = (row.get("password") or "").strip()
                u.role = (row.get("role") or "student").strip().lower()
                n_upd += 1
            else:
                u = User(
                    code=code,
                    name=(row.get("name") or "").strip(),
                    password=(row.get("password") or "").strip(),
                    role=(row.get("role") or "student").strip().lower(),
                )
                session.add(u)
                n_ins += 1
        print(f"✅ Seed users: thêm {n_ins}, cập nhật {n_upd}")

def main():
    load_dotenv()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_users(session)
        session.commit()
        print("🎉 Done seeding.")

if __name__ == "__main__":
    main()
