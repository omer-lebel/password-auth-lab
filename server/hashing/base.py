from abc import ABC, abstractmethod

class HashProvider(ABC):
    """Abstract base class for password hashing strategies"""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass