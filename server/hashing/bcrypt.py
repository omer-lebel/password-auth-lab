from passlib.context import CryptContext
from .base import HashProvider


class BcryptHashProvider(HashProvider):
    def __init__(self, cost: int = 12):
        self._context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=cost
        )

    def hash_password(self, password: str) -> str:
        return self._context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._context.verify(plain_password, hashed_password)
