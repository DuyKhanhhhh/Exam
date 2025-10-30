# repositories/question_repo.py
from __future__ import annotations

import csv, json, hashlib
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.question import Question

def _split_options(opt_str: str):
    if not opt_str:
        return []
    return [x.strip() for x in opt_str.split("||") if x.strip()]

def _make_qid(subject: str, csv_id: str | None, text: str) -> str:
    """
    Ưu tiên lấy từ CSV cột 'id' (nếu có).
    Nếu không có, tạo qid ổn định từ subject+text (hash ngắn).
    """
    if csv_id and str(csv_id).strip():
        return str(csv_id).strip()
    h = hashlib.md5((subject + "||" + (text or "")).encode("utf-8")).hexdigest()
    return "Q" + h[:12]  # gọn, ổn định

def upsert_questions_from_csv(session, csv_path: str, subject: str):
    """
    CSV cột: id (tùy chọn), question, options, answer, points, topic, difficulty (tùy chọn)
    Upsert theo (subject, qid).
    """
    created = updated = 0

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            text = (r.get("question") or "").strip()
            if not text:
                continue

            qid    = _make_qid(subject, r.get("id"), text)
            options = _split_options(r.get("options") or "")
            answer  = (r.get("answer") or "").strip().upper()
            points  = int(r.get("points") or 1)
            topic   = (r.get("topic") or "").strip()
            diff    = (r.get("difficulty") or "medium").strip().lower()

            stmt = select(Question).where(
                Question.subject == subject,
                Question.qid == qid
            )
            obj = session.execute(stmt).scalar_one_or_none()

            if obj is None:
                obj = Question(
                    qid=qid,
                    subject=subject,
                    text=text,
                    options_json=json.dumps(options, ensure_ascii=False),
                    answer=answer,
                    points=points,
                    topic=topic,
                    difficulty=diff,
                )
                session.add(obj)
                created += 1
            else:
                obj.text         = text
                obj.options_json = json.dumps(options, ensure_ascii=False)
                obj.answer       = answer
                obj.points       = points
                obj.topic        = topic
                obj.difficulty   = diff
                updated += 1

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    return created, updated

def list_by_subject(session, subject: str):
    return session.scalars(
        select(Question).where(Question.subject == subject).order_by(Question.id)
    ).all()
