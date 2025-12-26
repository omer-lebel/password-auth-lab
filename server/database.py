from datetime import datetime
from pathlib import Path
from sqlmodel import SQLModel, Session, Field, create_engine, JSON
from typing import Generator, Optional, List


class DatabaseManager:
    def __init__(self):
        self.engine = None

    def initialize(self, output_dir: Path):
        db_path = output_dir / "database.db"
        database_url = f"sqlite:///{db_path.absolute().as_posix()}"

        self.engine = create_engine(database_url, echo=False)
        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        if not self.engine:
            raise RuntimeError("Database must be initialized before getting a session.")

        with Session(self.engine) as session:
            yield session


# -------------------- table model --------------------
class User(SQLModel, table=True):
    # Identity
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    username: str = Field(index=True, unique=True)
    password: str
    password_score: str

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
    pending_totp: Optional[bool] = Field(default=False)
    totp_session_expiry: Optional[datetime] = Field(default=None)


db_manager = DatabaseManager()