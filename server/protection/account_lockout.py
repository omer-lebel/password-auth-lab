from .base import Protection, ProtectionResult, AuthContext
from server.log import logger as log
from server.models import User
from server.config.schema import AccountLockoutConfig


class AccountLockoutProtection(Protection):

    def __init__(self, conf: AccountLockoutConfig):
        self.max_failed_attempts = conf.max_failed_attempts
        log.info(f"Account Lockout initialized (max_failed_attempts={self.max_failed_attempts})")

    def validate_request(self, context: AuthContext) -> ProtectionResult:

        if context.user.is_blocked:
            log.debug(f"Account lockout active for user '{context.user.username}'")
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
        log.debug(f"failed attempts: {user.failed_attempts}/{self.max_failed_attempts}")

        if user.failed_attempts >= self.max_failed_attempts:
            user.is_blocked = True
            log.debug( f"User '{user.username}' is now BLOCKED")
