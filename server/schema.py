import pyotp
from pydantic import field_validator
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


@field_validator('totp_secret')
def validate_base32_secret(cls, v):
    if v is None or v == "":
        return v
    try:
        pyotp.TOTP(v)
        return v
    except Exception:
        raise ValueError('TOTP secret must be a valid Base32 string (A-Z, 2-7)')