import time
import pyotp

from .base import Protection, ProtectionResult, AuthContext
from server.log import logger as log
from server.database import User
from server.config import TOTPConfig


class TOTPProtection(Protection):
    STEP_SIZE = 30

    def __init__(self, conf: TOTPConfig):
        drift_steps = conf.max_drift_seconds // self.STEP_SIZE
        self.offest = list(range(-drift_steps, drift_steps + 1))
        log.info(f"TOTP initialized")

    def validate_request(self, context: AuthContext) -> ProtectionResult:
        # only validate that totp code was provided
        if context.user.totp_secret and not context.totp_code:
            return ProtectionResult(
                allowed=False,
                reason="totp",
                user_msg="This account requires a TOTP code. Please provide it.",
                status_code=401
            )
        return ProtectionResult(allowed=True)


    def reset(self, user: User) -> None:
        pass

    def record_failure(self, user: User) -> None:
        pass


    def verify(self, secret: str, input_code: str):
        if not secret or not input_code:
            return False

        totp_engine = pyotp.TOTP(secret)
        now = int(time.time())

        for offset in self.offest:
            drift = offset * self.STEP_SIZE
            log.debug(f"check TOTP with offset: {offset}, drift: {drift}")
            if totp_engine.at(now + drift) == input_code:
                log.info(f"TOTP match found with clock drift of {drift} seconds from now")
                return True
        return False