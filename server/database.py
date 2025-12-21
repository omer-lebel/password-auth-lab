from sqlmodel import SQLModel, Session, Field, create_engine, JSON
from typing import Generator, Optional, List

DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)

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
    rate_attempts: List[float] = Field(default_factory=list, sa_type=JSON)
    lockout_until: Optional[int] = None
    lockout_count: int = 0

    # captcha
    captcha_required: bool = False
    failed_attempts_captcha_counter: int = 0
    # totp
    totp_secret: Optional[str] = None


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session