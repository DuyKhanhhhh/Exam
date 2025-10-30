from pydantic import BaseModel
from typing import Optional

class UploadBase(BaseModel):
    subject: str
    filename: str
    csv_text: str

class UploadCreate(UploadBase):
    pass

class UploadUpdate(BaseModel):
    subject: Optional[str] = None
    filename: Optional[str] = None
    csv_text: Optional[str] = None

class UploadOut(UploadBase):
    id: int
    uploaded_at: int

    class Config:
        orm_mode = True
