# scripts/seed_results_from_csv.py
from pathlib import Path
from dotenv import load_dotenv

from core.db import Base, engine, SessionLocal
from repositories.result_repo import upsert_results_from_csv

DEFAULTS = [
    Path("results.csv"),
    Path("data/results.csv"),
]

def main():
    load_dotenv()
    Base.metadata.create_all(bind=engine)

    csv_path = next((p for p in DEFAULTS if p.exists()), None)
    if csv_path is None:
        raise SystemExit("❌ Không tìm thấy file kết quả results.csv.")

    print(f"DB seeding Results: file={csv_path}")

    with SessionLocal() as session:
        created, updated = upsert_results_from_csv(session, csv_path)

    print(f"✅ Seed results: thêm {created}, cập nhật {updated}")

if __name__ == "__main__":
    main()
