from fastapi import HTTPException
from .base import Protection
from server.models import User


class AccountLockoutProtection(Protection):

    def __init__(self, max_attempts: int = 5, window_seconds=60):
        self.max_attempts = max_attempts

    def validate_request(self, user: User) -> None:

        if user.is_blocked:
            raise HTTPException(
                status_code=403,
                detail=f"Account locked. contact admin.")

    def reset(self, user: User) -> None:
        user.is_blocked = False

    def record_failure(self, user):
        user.failed_attempts += 1
        if user.failed_attempts >= self.max_attempts:
            user.is_blocked = True
