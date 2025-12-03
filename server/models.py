from sqlmodel import SQLModel, Field


# model for http body
class UserCredentials(SQLModel):
    username: str
    password: str