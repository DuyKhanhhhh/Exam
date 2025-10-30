# models/question.py
from sqlalchemy import Column, Integer, String, Text, UniqueConstraint, Index
from core.db import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    qid = Column(String(64), index=True, nullable=False)   # mã định danh logic
    subject = Column(String(32), index=True, nullable=False)
    text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=True)
    answer = Column(String(8), nullable=True)
    points = Column(Integer, default=1, nullable=False)
    topic = Column(String(128), default="", nullable=False)
    difficulty = Column(String(16), default="medium", nullable=False)

    __table_args__ = (
        UniqueConstraint("subject", "qid", name="uq_question_subject_qid"),
        Index("ix_questions_subject_qid", "subject", "qid"),
    )
