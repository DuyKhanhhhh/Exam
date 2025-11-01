from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from core.db import Base

class MixedExam(Base):
    __tablename__ = "mixed_exams"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False)
    questions = Column(JSON)       # lưu danh sách câu hỏi (JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
