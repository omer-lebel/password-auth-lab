from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from server.models import User


@dataclass
class ProtectionResult:
    allowed: bool
    status_code: Optional[int] = None
    user_msg: Optional[str] = None
    reason: Optional[str] = None


class Protection(ABC):
    """Abstract base class for password hashing strategies"""

    @abstractmethod
    def validate_request(self, user: User) -> ProtectionResult:
        """check if the user is block
        function should NOT change the user (treat User as const)"""
        pass

    @abstractmethod
    def reset(self, user: User) -> None:
        pass

    @abstractmethod
    def record_failure(self, user: User) -> None:
        pass