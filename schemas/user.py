from pydantic import BaseModel

class UserBase(BaseModel):
    code: str
    name: str
    role: str

class UserCreate(UserBase):
    password: str

class UserResp(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_approved: bool

    class Config:
        orm_mode = True
