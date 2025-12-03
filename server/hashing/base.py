from abc import ABC, abstractmethod

class HashProvider(ABC):
    """Abstract base class for password hashing strategies"""
    def __init__(self, pepper: str = ""):
        self.pepper = pepper

    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass