from .base import Protection, ProtectionResult
from server.log import logger as log
from server.models import User
from server.config.schema import AccountLockoutConfig


class AccountLockoutProtection(Protection):

    def __init__(self, conf: AccountLockoutConfig):
        self.max_failed_attempts = conf.max_failed_attempts

    def validate_request(self, user: User) -> ProtectionResult:

        if user.is_blocked:
            return ProtectionResult(
                allowed=False,
                user_msg = "Account locked, contact admin to reset your password",
                reason="account locked",
                status_code=403)

        return ProtectionResult(allowed=True)

    def reset(self, user: User) -> None:
        user.is_blocked = False

    def record_failure(self, user):
        user.failed_attempts += 1
        if user.failed_attempts >= self.max_failed_attempts:
            user.is_blocked = True
