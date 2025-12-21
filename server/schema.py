from sqlmodel import SQLModel
from typing import Optional

# schema of http body

class UserRegister(SQLModel):
    username: str
    password: str
    totp_secret: Optional[str] = None

class UserLogin(SQLModel):
    username: str
    password: str
    captcha_token: Optional[str] = None
    totp_code: Optional[str] = None