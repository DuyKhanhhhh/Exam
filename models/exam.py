# models/exam.py
import time
from typing import Optional, List, Dict
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.db import Base

class ExamConfig(Base):
    __tablename__ = "exam_configs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject: Mapped[str] = mapped_column(String(16), index=True, unique=True)
    n_questions: Mapped[int] = mapped_column(Integer)
    n_versions: Mapped[int] = mapped_column(Integer, default=1)
    seed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shuffle_questions: Mapped[int] = mapped_column(Integer, default=1)
    shuffle_options: Mapped[int] = mapped_column(Integer, default=1)
    difficulty_quotas: Mapped[Dict] = mapped_column(JSON, default={})  # {"easy":...}

class Upload(Base):
    __tablename__ = "uploads"
    __table_args__ = {"extend_existing": True}
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject: Mapped[str] = mapped_column(String(16), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    csv_text: Mapped[str] = mapped_column(LONGTEXT)
    uploaded_at: Mapped[int] = mapped_column(Integer, default=lambda: int(time.time()))

class ExamSession(Base):
    __tablename__ = "exam_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_code: Mapped[str] = mapped_column(String(32), index=True)
    subject: Mapped[str] = mapped_column(String(16), index=True)
    version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[int] = mapped_column(Integer, default=lambda: int(time.time()))
    questions: Mapped[List] = mapped_column(JSON)   # list câu gửi cho FE
    answer_key: Mapped[Dict] = mapped_column(JSON)  # dùng để chấm điểm

    submissions = relationship("ExamSubmission", back_populates="session")

class ExamSubmission(Base):
    __tablename__ = "exam_submissions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("exam_sessions.id"), index=True)
    student_code: Mapped[str] = mapped_column(String(32), index=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    submitted_at: Mapped[int] = mapped_column(Integer, default=lambda: int(time.time()))
    answers: Mapped[Dict] = mapped_column(JSON)

    session = relationship("ExamSession", back_populates="submissions")

class SubmissionDetail(Base):
    __tablename__ = "submission_details"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("exam_submissions.id"), index=True)
    question_id: Mapped[str] = mapped_column(String(64))
    chosen: Mapped[str] = mapped_column(String(4))
    correct: Mapped[str] = mapped_column(String(4))
    points: Mapped[int] = mapped_column(Integer, default=1)
    earned_points: Mapped[int] = mapped_column(Integer, default=0)
