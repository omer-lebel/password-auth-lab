from sqlmodel import SQLModel, create_engine, Session, Field
from typing import Generator, Optional

DATABASE_URL = "sqlite:///database.db"

engine = create_engine(DATABASE_URL)


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


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session