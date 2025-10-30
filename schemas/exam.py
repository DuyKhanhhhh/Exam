# schemas/exam.py
from typing import Optional, Dict
from pydantic import BaseModel, Field


class PreviewIn(BaseModel):
    n_questions: int = Field(..., ge=1)
    n_versions: int = Field(1, ge=1)
    seed: Optional[int] = None
    bank_path: Optional[str] = None  # để tương thích FE, không dùng ở BE này
    subject: str = "math"
    shuffle_questions: bool = True
    shuffle_options: bool = True


class PublishIn(BaseModel):
    n_questions: int
    n_versions: int = 1
    seed: Optional[int] = None
    shuffle_questions: bool = True
    shuffle_options: bool = True
    subject: str = "math"


class StartIn(BaseModel):
    student_code: str
    subject: str = "math"


class SubmitIn(BaseModel):
    session_id: int
    # {qid: "A"/"B"/...}
    answers: Dict[str, str]
