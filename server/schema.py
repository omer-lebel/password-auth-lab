from sqlmodel import SQLModel, Field
from typing import Optional

# schema of http body
class UserRegister(SQLModel):
    username: str = Field(min_length=3, max_length=20, description="Username must be 3-20 chars")
    password: str = Field(min_length=3, max_length=20, description="Password must be 3-20 chars")
    totp_secret: Optional[str] = Field(default=None,min_length=32, max_length=32,
                                       description='use pyotp.random_base32() to generate totp secret')


class UserLogin(SQLModel):
    username: str
    password: str
    captcha_token: Optional[str] = None

class TotpLogin(SQLModel):
    username: str
    totp_code: str = Field(min_length=6, max_length=6, schema_extra={"pattern": "^[0-9]+$"})

class GetCaptcha(SQLModel):
    username: str
    group_seed: int