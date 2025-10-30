# repositories/result_repo.py

from pathlib import Path
import csv, io, datetime
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session

from models.result import Result  # đảm bảo models/__init__.py export Result

REQUIRED_COLS = ["session_id", "student_code", "score", "total_points", "submitted_at"]

def _parse_dt(s: str) -> datetime.datetime:
    s = (s or "").strip()
    # ưu tiên ISO
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        pass
    # fallback: try common formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except Exception:
            continue
    # cuối cùng: now
    return datetime.datetime.utcnow()

def _read_csv(path: Path) -> List[Dict[str, str]]:
    raw = path.read_bytes()
    text = None
    for enc in ("utf-8-sig", "utf-8"):
        try:
            text = raw.decode(enc); break
        except UnicodeDecodeError:
            pass
    if text is None:
        text = raw.decode("cp1258", errors="replace")
    f = io.StringIO(text)
    reader = csv.DictReader(f)
    rows = []
    for r in reader:
        rows.append({k.strip(): (v or "").strip() for k, v in r.items()})
    return rows


def upsert_results_from_csv(session: Session, csv_path: Path) -> Tuple[int, int]:
    """
    Upsert theo (session_id, student_code)
    """
    rows = _read_csv(csv_path)
    created = updated = 0

    for r in rows:
        sid = int(r.get("session_id") or 0)
        code = r.get("student_code") or ""
        if not sid or not code:
            continue

        res = (session.query(Result)
               .filter(Result.session_id == sid, Result.student_code == code)
               .one_or_none())
        if res is None:
            res = Result(
                session_id=sid,
                student_code=code,
                score=int(r.get("score") or 0),
                total_points=int(r.get("total_points") or 0),
                submitted_at=_parse_dt(r.get("submitted_at") or ""),
            )
            session.add(res)
            created += 1
        else:
            res.score = int(r.get("score") or 0)
            res.total_points = int(r.get("total_points") or 0)
            res.submitted_at = _parse_dt(r.get("submitted_at") or "")
            updated += 1

    session.commit()
    return created, updated
