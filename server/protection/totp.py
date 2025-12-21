import time

import pyotp

from .base import Protection, ProtectionResult, AuthContext
from server.log import logger as log
from server.database import User
from server.config.setting import TOTPConfig


class TOTPProtection(Protection):

    def __init__(self, conf: TOTPConfig):
        self.offest = [-1, 0, 1]
        log.info(f"TOTP initialized")

    def validate_request(self, context: AuthContext) -> ProtectionResult:
        # only validate that totp code was provided
        if context.user.totp_sercret and not context.totp_code:
            return ProtectionResult(
                allowed=False,
                reason="TOTP code missing",
                user_msg="This account requires a TOTP code. Please provide it.",
                status_code=401
            )
        return ProtectionResult(allowed=True)


    def reset(self, user: User) -> None:
        pass

    def record_failure(self, user: User) -> None:
        pass


    def verify(self, secret: str, input_code: str):
        if not secret:
            return False

        totp = pyotp.TOTP(secret)
        now = int(time.time())

        for offset in self.offest:
            check_time = now + (offset * 30)
            expected_code = totp.at(check_time)
            if expected_code == input_code:
                return True

        return False