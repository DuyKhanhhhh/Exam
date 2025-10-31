from pydantic import BaseModel

class LoginReq(BaseModel):
    code: str
    password: str

class LoginResp(BaseModel):
    code: str
    name: str
    role: str
