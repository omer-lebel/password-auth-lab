import base64
from pydantic import field_validator, validator
from sqlmodel import SQLModel
from typing import Optional

# schema of http body

class UserRegister(SQLModel):
    username: str
    password: str
    totp_secret: Optional[str] = None


    @field_validator('totp_secret')
    @classmethod
    def validate_base32_secret(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return v
        try:
            base64.b32decode(v, casefold=True)
            return v
        except Exception:
            raise ValueError('TOTP secret must be a valid Base32 string (A-Z, 2-7)')


class UserLogin(SQLModel):
    username: str
    password: str
    captcha_token: Optional[str] = None
    totp_code: Optional[str] = None


