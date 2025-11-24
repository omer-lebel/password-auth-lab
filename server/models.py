from sqlmodel import SQLModel, Field
from typing import Optional

# db model
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    username: str = Field(index=True, unique=True)
    password: str
    # isBlocked = true/false
    # blockFrom = 21:13
    # blockLevel = [0, 1, 5, 60, forever]
    # passwordType
    # salt - nullable
    # totp
    # failedAttempt + timestamps ?



# model for http body
class UserCredentials(SQLModel):
    username: str
    password: str