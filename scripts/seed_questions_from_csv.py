# scripts/seed_questions_from_csv.py
from pathlib import Path
from dotenv import load_dotenv
from core.db import Base, engine, SessionLocal
from models.question import Question  # Quan trọng: import để Base biết model
from repositories.question_repo import upsert_questions_from_csv
import argparse


def main():
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=str(Path("questions_math.csv")))
    parser.add_argument("--subject", default="math")
    args = parser.parse_args()

    # Tạo bảng nếu chưa có
    Base.metadata.create_all(bind=engine, tables=[Question.__table__])

    with SessionLocal() as session:
        created, updated = upsert_questions_from_csv(session, args.file, args.subject)
        print(f"✅ Seed questions: thêm {created}, cập nhật {updated}")
        print("➡ file =", args.file, "subject =", args.subject)


if __name__ == "__main__":
    main()
S