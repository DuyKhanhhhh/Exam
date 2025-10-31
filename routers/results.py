# routers/results.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from core.db import SessionLocal
from models.exam import ExamSession, ExamSubmission, SubmissionDetail

router = APIRouter(prefix="/results", tags=["results"])

# -------- DB dependency --------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ts_to_iso(ts: Optional[int]) -> Optional[str]:
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(ts).isoformat(timespec="seconds")
    except Exception:
        return None


@router.get("")
def list_results(
    student_code: str = Query("", description="lọc theo mã HS, để trống nếu không"),
    subject: str = Query("", description="lọc theo môn, để trống nếu không"),
    db: Session = Depends(get_db),
):
    """
    Trả về danh sách kết quả các lần nộp bài (ExamSubmission) kèm thông tin phiên (ExamSession).
    FE gọi: GET /results?student_code=S1&subject=math
    """
    q = db.query(ExamSubmission, ExamSession).join(
        ExamSession, ExamSubmission.session_id == ExamSession.id
    )

    if student_code:
        q = q.filter(ExamSubmission.student_code == student_code)
    if subject:
        q = q.filter(ExamSession.subject == subject)

    q = q.order_by(ExamSubmission.submitted_at.desc())
    rows = q.all()

    items = []
    for sub, sess in rows:
        items.append({
            "session_id": sess.id,
            "student_code": sub.student_code,
            "subject": sess.subject,
            "version": sess.version,
            "score": sub.score,
            "total_points": sub.total_points,
            "submitted_at": _ts_to_iso(sub.submitted_at),
        })
    return items


@router.get("/session/{session_id}")
def get_result_detail(session_id: int, db: Session = Depends(get_db)):
    """
    Chi tiết một phiên làm bài: thông tin phiên, điểm số, và các câu đã chọn.
    FE gọi: GET /results/session/<session_id>
    """
    sess = db.get(ExamSession, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên")

    sub = (
        db.query(ExamSubmission)
        .filter(ExamSubmission.session_id == session_id)
        .order_by(ExamSubmission.id.desc())
        .first()
    )
    if not sub:
        # chưa nộp bài nhưng có phiên
        return {
            "session_id": sess.id,
            "student_code": sess.student_code,
            "subject": sess.subject,
            "version": sess.version,
            "score": 0,
            "total_points": sess.total_points,
            "submitted_at": None,
            "answers": {},
            "questions": sess.questions or [],
            "details": [],
        }

    details = (
        db.query(SubmissionDetail)
        .filter(SubmissionDetail.submission_id == sub.id)
        .order_by(SubmissionDetail.id)
        .all()
    )

    return {
        "session_id": sess.id,
        "student_code": sub.student_code,
        "subject": sess.subject,
        "version": sess.version,
        "score": sub.score,
        "total_points": sub.total_points,
        "submitted_at": _ts_to_iso(sub.submitted_at),
        "answers": sub.answers or {},
        "questions": sess.questions or [],
        "details": [
            {
                "qid": d.question_id,
                "chosen": d.chosen,
                "correct": d.correct,
                "points": d.points,
                "earned_points": d.earned_points,
            }
            for d in details
        ],
    }
# routers/results.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from core.db import SessionLocal
from models.exam import ExamSession, ExamSubmission, SubmissionDetail

router = APIRouter(prefix="/results", tags=["results"])

# -------- DB dependency --------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ts_to_iso(ts: Optional[int]) -> Optional[str]:
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(ts).isoformat(timespec="seconds")
    except Exception:
        return None


@router.get("")
def list_results(
    student_code: str = Query("", description="lọc theo mã HS, để trống nếu không"),
    subject: str = Query("", description="lọc theo môn, để trống nếu không"),
    db: Session = Depends(get_db),
):
    """
    Trả về danh sách kết quả các lần nộp bài (ExamSubmission) kèm thông tin phiên (ExamSession).
    FE gọi: GET /results?student_code=S1&subject=math
    """
    q = db.query(ExamSubmission, ExamSession).join(
        ExamSession, ExamSubmission.session_id == ExamSession.id
    )

    if student_code:
        q = q.filter(ExamSubmission.student_code == student_code)
    if subject:
        q = q.filter(ExamSession.subject == subject)

    q = q.order_by(ExamSubmission.submitted_at.desc())
    rows = q.all()

    items = []
    for sub, sess in rows:
        items.append({
            "session_id": sess.id,
            "student_code": sub.student_code,
            "subject": sess.subject,
            "version": sess.version,
            "score": sub.score,
            "total_points": sub.total_points,
            "submitted_at": _ts_to_iso(sub.submitted_at),
        })
    return items


@router.get("/session/{session_id}")
def get_result_detail(session_id: int, db: Session = Depends(get_db)):
    """
    Chi tiết một phiên làm bài: thông tin phiên, điểm số, và các câu đã chọn.
    FE gọi: GET /results/session/<session_id>
    """
    sess = db.get(ExamSession, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên")

    sub = (
        db.query(ExamSubmission)
        .filter(ExamSubmission.session_id == session_id)
        .order_by(ExamSubmission.id.desc())
        .first()
    )
    if not sub:
        # chưa nộp bài nhưng có phiên
        return {
            "session_id": sess.id,
            "student_code": sess.student_code,
            "subject": sess.subject,
            "version": sess.version,
            "score": 0,
            "total_points": sess.total_points,
            "submitted_at": None,
            "answers": {},
            "questions": sess.questions or [],
            "details": [],
        }

    details = (
        db.query(SubmissionDetail)
        .filter(SubmissionDetail.submission_id == sub.id)
        .order_by(SubmissionDetail.id)
        .all()
    )

    return {
        "session_id": sess.id,
        "student_code": sub.student_code,
        "subject": sess.subject,
        "version": sess.version,
        "score": sub.score,
        "total_points": sub.total_points,
        "submitted_at": _ts_to_iso(sub.submitted_at),
        "answers": sub.answers or {},
        "questions": sess.questions or [],
        "details": [
            {
                "qid": d.question_id,
                "chosen": d.chosen,
                "correct": d.correct,
                "points": d.points,
                "earned_points": d.earned_points,
            }
            for d in details
        ],
    }
