from passlib.context import CryptContext
from .base import HashProvider
from server.log import logger as log

class Argon2HashProvider(HashProvider):
    def __init__(self, pepper: str = "", time: int = 1, memory: int = 65536, parallelism=1):
        # 65536 KB = 64 MB
        super().__init__(pepper)
        self._context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__memory_cost=memory,
            argon2__time_cost=time,
            argon2__parallelism=parallelism
        )
        log.info(f'Argon2 initialized with time:{time}, memory:{memory}, parallelism:{parallelism}')

    def hash_password(self, password: str) -> str:
        return self._context.hash(password + self.pepper)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._context.verify(plain_password + self.pepper, hashed_password)
