from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from server.database import User


@dataclass
class ProtectionResult:
    allowed: bool
    status_code: Optional[int] = None
    user_msg: Optional[str] = None
    reason: Optional[str] = None

@dataclass
class AuthContext:
    user: User
    captcha_token: Optional[str] = None
    totp_code: Optional[str] = None

class Protection(ABC):
    """Abstract base class for password hashing strategies"""

    @abstractmethod
    def validate_request(self, context: AuthContext) -> ProtectionResult:
        """check if the user is block
        function should NOT change the user (treat User as const)"""
        pass

    @abstractmethod
    def reset(self, user: User) -> None:
        pass

    @abstractmethod
    def record_failure(self, user: User) -> None:
        pass