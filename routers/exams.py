# routers/exams.py
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json, random, time
from models.mixed_exam import MixedExam

from core.db import SessionLocal
from models.exam import (
    ExamConfig, ExamSession, ExamSubmission, SubmissionDetail
)
from models.question import Question
from models.result import Result
from repositories.question_repo import list_by_subject
from schemas.exam import PreviewIn, PublishIn, StartIn, SubmitIn

router = APIRouter(prefix="/exam", tags=["exam"])

# ---------- DB dependency ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- helpers ----------
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def _options_list(q: Question) -> List[str]:
    try:
        return json.loads(q.options_json or "[]")
    except Exception:
        return []

def _answer_letter(q: Question, options: List[str]) -> Optional[str]:
    """
    Trả về chữ cái đáp án đúng tương ứng với danh sách options (đã có thể bị shuffle).
    - Nếu q.answer là A/B/C/...: dùng trực tiếp (nếu còn trong range).
    - Nếu q.answer là text: so khớp với options (case-insensitive).
    """
    ans = (q.answer or "").strip()
    if not ans:
        return None

    up = ans.upper()
    if up in LETTERS:
        idx = LETTERS.index(up)
        return LETTERS[idx] if idx < len(options) else None

    for i, opt in enumerate(options):
        if opt.strip().lower() == ans.lower():
            return LETTERS[i]
    return None


def _build_versions(
    pool: List[Question],
    *,
    n_questions: int,
    n_versions: int,
    seed: Optional[int],
    shuffle_questions: bool,
    shuffle_options: bool,
):
    rng = random.Random(seed if seed is not None else time.time_ns())
    versions = []

    ids = list(range(len(pool)))
    for ver in range(1, n_versions + 1):
        if shuffle_questions:
            rng.shuffle(ids)
        take = ids[:min(n_questions, len(ids))]

        payload = []
        for idx in take:
            q = pool[idx]
            opts = _options_list(q)

            if shuffle_options:
                order = list(range(len(opts)))
                rng.shuffle(order)
                opts = [opts[i] for i in order]

            payload.append({
                "id": q.id,
                "qid": q.qid,
                "subject": q.subject,
                "text": q.text,
                "options": opts,
                "points": q.points,
                "topic": q.topic,
                "difficulty": q.difficulty,
            })

        versions.append({"version": ver, "questions": payload})

    return versions


# ---------- routes ----------
@router.post("/preview")
def preview(payload: PreviewIn, db: Session = Depends(get_db)):
    pool = list_by_subject(db, payload.subject)
    if not pool:
        raise HTTPException(status_code=400, detail="Không có câu hỏi cho môn này")

    versions = _build_versions(
        pool,
        n_questions=payload.n_questions,
        n_versions=payload.n_versions,
        seed=payload.seed,
        shuffle_questions=payload.shuffle_questions,
        shuffle_options=payload.shuffle_options,
    )

    # ✅ Lưu lịch sử các bộ đề đã trộn
    for v in versions:
        mixed = MixedExam(
            subject=payload.subject,
            version=v["version"],
            questions=v["questions"],
        )
        db.add(mixed)
    db.commit()

    # ✅ Trả kết quả cho FE
    return {
        "ok": True,
        "subject": payload.subject,
        "total": len(pool),
        "n_questions": payload.n_questions,
        "n_versions": payload.n_versions,
        "versions": versions,
    }


@router.post("/publish")
def publish(payload: PublishIn, db: Session = Depends(get_db)):
    cfg = db.query(ExamConfig).filter(ExamConfig.subject == payload.subject).one_or_none()
    if cfg is None:
        cfg = ExamConfig(
            subject=payload.subject,
            n_questions=payload.n_questions,
            n_versions=payload.n_versions,
            seed=payload.seed,
            shuffle_questions=1 if payload.shuffle_questions else 0,
            shuffle_options=1 if payload.shuffle_options else 0,
            difficulty_quotas={},
        )
        db.add(cfg)
    else:
        cfg.n_questions = payload.n_questions
        cfg.n_versions = payload.n_versions
        cfg.seed = payload.seed
        cfg.shuffle_questions = 1 if payload.shuffle_questions else 0
        cfg.shuffle_options = 1 if payload.shuffle_options else 0

    db.commit()
    return {"ok": True}


@router.post("/start")
def start_exam(payload: StartIn, db: Session = Depends(get_db)):
    cfg = db.query(ExamConfig).filter(ExamConfig.subject == payload.subject).one_or_none()
    if not cfg:
        raise HTTPException(status_code=400, detail="Chưa publish cấu hình đề cho môn này")

    pool = list_by_subject(db, payload.subject)
    if not pool:
        raise HTTPException(status_code=400, detail="Không có câu hỏi cho môn này")

    versions = _build_versions(
        pool,
        n_questions=cfg.n_questions,
        n_versions=1,
        seed=cfg.seed,
        shuffle_questions=bool(cfg.shuffle_questions),
        shuffle_options=bool(cfg.shuffle_options),
    )
    ver = versions[0]

    # tạo answer_key theo options đã trộn
    answer_key: Dict[str, str] = {}
    # map id -> object gốc
    by_id = {q.id: q for q in pool}
    for q in ver["questions"]:
        obj = by_id.get(q["id"])
        if not obj:
            continue
        ans = _answer_letter(obj, q["options"])
        if ans:
            answer_key[q["qid"]] = ans

    session = ExamSession(
        student_code=payload.student_code,
        subject=payload.subject,
        version=1,
        total_points=sum(q["points"] for q in ver["questions"]),
        questions=ver["questions"],
        answer_key=answer_key,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "subject": payload.subject,
        "version": 1,
        "questions": ver["questions"],
        "total_points": session.total_points,
    }


@router.post("/submit")
def submit(payload: SubmitIn, db: Session = Depends(get_db)):
    sess = db.get(ExamSession, payload.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên làm bài")

    answers = payload.answers or {}
    score = 0
    details: List[SubmissionDetail] = []

    ans_key: Dict[str, str] = sess.answer_key or {}
    qmap = {q["qid"]: q for q in (sess.questions or [])}

    for qid, q in qmap.items():
        correct = ans_key.get(qid)
        chosen = answers.get(qid)
        pts = q.get("points", 1)
        earned = pts if correct and chosen and correct.upper() == chosen.upper() else 0
        score += earned
        details.append(SubmissionDetail(
            submission_id=0,
            question_id=qid,
            chosen=chosen or "",
            correct=correct or "",
            points=pts,
            earned_points=earned
        ))

    sub = ExamSubmission(
        session_id=sess.id,
        student_code=sess.student_code,
        score=score,
        total_points=sess.total_points,
        answers=answers,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    # lưu detail
    for d in details:
        d.submission_id = sub.id
        db.add(d)
    db.commit()

    # ✅ upsert sang bảng Result (tuỳ chọn)
    from datetime import datetime
    res = (
        db.query(Result)
        .filter(Result.session_id == sess.id, Result.student_code == sess.student_code)
        .one_or_none()
    )
    if res is None:
        res = Result(
            session_id=sess.id,
            student_code=sess.student_code,
            score=score,
            total_points=sess.total_points,
            submitted_at=datetime.utcnow(),
        )
        db.add(res)
    else:
        res.score = score
        res.total_points = sess.total_points
        res.submitted_at = datetime.utcnow()
    db.commit()

    return {
        "session_id": sess.id,
        "student_code": sub.student_code,
        "score": sub.score,
        "total_points": sub.total_points,
        "details_count": len(details),
    }
@router.get("/mixed-history")
def list_mixed_history(limit: int = 50, db: Session = Depends(get_db)):
    exams = db.query(MixedExam).order_by(MixedExam.created_at.desc()).limit(limit).all()
    return [
        {
            "id": e.id,
            "subject": e.subject,
            "version": e.version,
            "questions_count": len(e.questions or []),
            "created_at": e.created_at,
        }
        for e in exams
    ]

@router.get("/mixed-history/{exam_id}")
def get_mixed_exam_detail(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(MixedExam).filter(MixedExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Không tìm thấy bộ đề")
    return {
        "id": exam.id,
        "subject": exam.subject,
        "version": exam.version,
        "questions": exam.questions,
        "created_at": exam.created_at,
    }


@router.delete("/mixed-history/{exam_id}")
def delete_mixed_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(MixedExam).filter(MixedExam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Không tìm thấy bộ đề")
    db.delete(exam)
    db.commit()
    return {"ok": True, "message": f"Đã xóa bộ đề {exam.subject} - Đề {exam.version}"}