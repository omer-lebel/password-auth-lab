from passlib.hash import sha256_crypt
from .base import HashProvider


class Sha256HashProvider(HashProvider):

    def hash_password(self, password: str) -> str:
        return sha256_crypt.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return sha256_crypt.verify(plain_password, hashed_password)