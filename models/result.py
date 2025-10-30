# models/result.py
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from core.db import Base

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, index=True, nullable=False)
    student_code = Column(String(64), index=True, nullable=False)
    score = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    submitted_at = Column(DateTime)

    __table_args__ = (
        UniqueConstraint("session_id", "student_code", name="uq_result_sid_code"),
    )
