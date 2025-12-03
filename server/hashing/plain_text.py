from .base import HashProvider


class PlainTextProvider(HashProvider):
    """Debug mode: no encryption"""

    def hash_password(self, password: str) -> str:
        return password

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return plain_password == hashed_password
