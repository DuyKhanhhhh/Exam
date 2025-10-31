# models/user.py
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from core.db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    password: Mapped[str] = mapped_column(String(128))  # theo hệ thống cũ
    role: Mapped[str] = mapped_column(String(16))       # "teacher" | "student"
