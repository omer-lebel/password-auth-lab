from abc import ABC, abstractmethod
from server.models import User

class Protection(ABC):
    """Abstract base class for password hashing strategies"""

    @abstractmethod
    def validate_request(self, user: User) -> None:
        pass

    @abstractmethod
    def reset(self, user: User) -> None:
        pass

    @abstractmethod
    def record_failure(self, user: User) -> None:
        pass