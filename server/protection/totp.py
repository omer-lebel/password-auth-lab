import base64
from datetime import datetime, timedelta
import pyotp
import time

from .base import Protection, ProtectionResult, AuthContext
from server.log import logger as log
from server.database import User
from server.config import TOTPConfig


class TOTPProtection(Protection):
    STEP_SIZE = 30

    def __init__(self, conf: TOTPConfig):
        drift_steps = conf.max_drift_seconds // self.STEP_SIZE
        self.offest = list(range(-drift_steps, drift_steps + 1))
        self.pending_totp_time = conf.pending_totp_minutes
        log.info(f"TOTP initialized")

    def init_pending_session(self, user: User) -> None:
        user.pending_totp = True
        user.totp_session_expiry = datetime.now() + timedelta(minutes=self.pending_totp_time)

    def validate_request(self, context: AuthContext) -> ProtectionResult:
        username = context.user.username

        if not context.user.totp_secret:
            log.debug(f"{username:<10} | TOTP requested, but user haven't register with totp")
            return ProtectionResult(allowed=False,
                                    status_code= 403,
                                    reason='unauthorized totp attempt',
                                    user_msg="Access denied")

        if not context.user.pending_totp:
            log.debug(f"{username:<10} | TOTP requested, but user haven't log with his password")
            return ProtectionResult(allowed=False,
                                    status_code= 401,
                                    reason='unauthorized totp attempt',
                                    user_msg="Access denied")

        if context.user.totp_session_expiry and datetime.now() > context.user.totp_session_expiry:
            context.user.pending_totp = False
            log.debug(f"{username:<10} | TOTP requested, but session expired")
            return ProtectionResult(
                allowed=False,
                status_code=401,
                reason='totp session expired',
                user_msg="Your session has expired. Please log in again with your password."
            )

        return ProtectionResult(allowed=True)


    def reset(self, user: User) -> None:
        user.pending_totp = False


    def record_failure(self, user: User) -> None:
        pass


    def verify_code(self, username: str, totp_secret: str, input_code: str) -> bool:
        totp_engine = pyotp.TOTP(totp_secret)
        now = int(time.time())

        for offset in self.offest:
            drift = offset * self.STEP_SIZE
            log.debug(f"{username:<10} | check TOTP with offset: {offset}, drift: {drift}")
            if totp_engine.at(now + drift) == input_code:
                log.info(f"{username:<10} | TOTP match found with clock drift of {drift} seconds from now")
                return True

        return False

    @staticmethod
    def is_valid_secret(totp_secret: str) -> bool:
        try:
            base64.b32decode(totp_secret, casefold=True)
            return True
        except ValueError:
            return False