from __future__ import annotations

import time
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.exam import ExamConfig, ExamSession, ExamSubmission, SubmissionDetail

def upsert_config(db: Session, subject: str, cfg: dict) -> ExamConfig:
    e = db.execute(select(ExamConfig).where(ExamConfig.subject==subject)).scalar_one_or_none()
    if e:
        for k,v in cfg.items():
            setattr(e, k, v)
    else:
        e = ExamConfig(subject=subject, **cfg)
        db.add(e)
    db.commit(); db.refresh(e)
    return e

def get_config(db: Session, subject: str) -> ExamConfig | None:
    return db.execute(select(ExamConfig).where(ExamConfig.subject==subject)).scalar_one_or_none()

def create_session(db: Session, student_code: str, subject: str, version: int | None,
                   total_points: int, questions: list, answer_key: dict) -> int:
    es = ExamSession(
        student_code=student_code, subject=subject, version=version,
        total_points=total_points, created_at=int(time.time()),
        questions=questions, answer_key=answer_key
    )
    db.add(es); db.commit(); db.refresh(es)
    return es.id

def get_session(db: Session, session_id: int) -> ExamSession | None:
    return db.get(ExamSession, session_id)

def create_submission(db: Session, session_id: int, student_code: str,
                      score: int, total: int, answers: dict, details: list[dict]) -> int:
    sub = ExamSubmission(session_id=session_id, student_code=student_code,
                         score=score, total_points=total, answers=answers)
    db.add(sub); db.flush()
    for d in details:
        db.add(SubmissionDetail(
            submission_id=sub.id, question_id=d["id"], chosen=d["chosen"],
            correct=d["correct"], points=d["points"], earned_points=d["earned_points"]
        ))
    db.commit(); db.refresh(sub)
    return sub.id
