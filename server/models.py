from sqlmodel import SQLModel, Field
from typing import Optional

# model for http body
class UserCredentials(SQLModel):
    username: str
    password: str

# model for db
class User(SQLModel, table=True):
    # Identity
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    username: str = Field(index=True, unique=True)
    password: str

    # account lockout + captcha
    failed_attempts: int = 0
    is_blocked: bool = False

    # rate limiting
    rate_attempts: str = "[]"
    lockout_until: Optional[int] = None
    lockout_count: int = 0

    # captcha
    captcha_required: bool = False

    # totp
    totp_secret: Optional[str] = None