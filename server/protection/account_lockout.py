from .base import Protection, ProtectionResult, AuthContext
from server.log import logger as log
from server.database import User
from server.config import AccountLockoutConfig


class AccountLockoutProtection(Protection):

    def __init__(self, conf: AccountLockoutConfig):
        self.max_failed_attempts = conf.max_failed_attempts
        log.info(f"initialized (max_failed_attempts={self.max_failed_attempts})")

    def validate_request(self, context: AuthContext) -> ProtectionResult:

        if context.user.is_blocked:
            log.debug(f"{context.user.username:<10} | account locked'")
            return ProtectionResult(
                allowed=False,
                user_msg = "Account locked, contact admin to reset your password",
                reason="account locked",
                status_code=403)

        return ProtectionResult(allowed=True)

    def reset(self, user: User) -> None:
        user.is_blocked = False

    def record_failure(self, user: User) -> None:
        user.failed_attempts += 1
        log.debug(f"{user.username:<10} | failed attempts: {user.failed_attempts}/{self.max_failed_attempts}")

        if user.failed_attempts >= self.max_failed_attempts:
            user.is_blocked = True
            log.debug( f"{user.username:<10} | User is now BLOCKED")
