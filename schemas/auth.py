from pydantic import BaseModel

class LoginReq(BaseModel):
    code: str
    password: str

class LoginResp(BaseModel):
    id: int
    code: str
    name: str
    role: str
