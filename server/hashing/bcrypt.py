from passlib.context import CryptContext
from .base import HashProvider


class BcryptHashProvider(HashProvider):
    def __init__(self, pepper: str = "", cost: int = 12):
        super().__init__(pepper)
        self._context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=cost
        )

    def hash_password(self, password: str) -> str:
        return self._context.hash(password + self.pepper)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._context.verify(plain_password + self.pepper, hashed_password)
