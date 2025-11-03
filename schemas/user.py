from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    code: str
    name: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "student"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None

class UserResp(BaseModel):
    id: int
    code: str
    name: str
    email: Optional[str]
    role: str
    status: str

    class Config:
        orm_mode = True
