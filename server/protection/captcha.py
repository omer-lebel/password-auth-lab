import secrets

from .base import Protection, ProtectionResult, AuthContext
from server.log import logger as log
from server.database import User
from server.config import CaptchaConfig

class CaptchaProtection(Protection):

    def __init__(self, conf: CaptchaConfig):
        self.max_failed_attempts = conf.max_failed_attempts
        self.token_expiry_seconds = 300
        self.tokens: dict[str, str] = {} # username :  token
        log.info(f"Captcha initialized (max_failed_attempts={self.max_failed_attempts})")

    def validate_request(self, context: AuthContext) -> ProtectionResult:
        if not context.user.captcha_required:
            return ProtectionResult(allowed=True)

        username = context.user.username
        input_token = context.captcha_token
        stored_token = self.tokens.pop(username, None)

        if stored_token is None:
            log.debug(f"No captcha token for {username}")
            return ProtectionResult(allowed=False, user_msg = "required captcha", reason="captcha", status_code=403)

        if input_token is None:
            log.debug(f"{username:<10} | didn't provided a captcha token")
            return ProtectionResult(allowed=False, user_msg = "required captcha", reason="captcha", status_code=403)

        if input_token != stored_token:
            log.debug(f"{username:<10} | Invalid captcha token, expected {stored_token}")
            return ProtectionResult(allowed=False, user_msg = "Invalid captcha token", reason="captcha", status_code=403)

        return ProtectionResult(allowed=True)


    def reset(self, user: User) -> None:
        user.captcha_required = False
        user.failed_attempts_captcha_counter = 0

    def record_failure(self, user: User) -> None:
        user.failed_attempts_captcha_counter += 1
        log.debug(f"{user.username:<10} | failed attempts: {user.failed_attempts_captcha_counter}/{self.max_failed_attempts}")

        if user.failed_attempts_captcha_counter >= self.max_failed_attempts:
            user.captcha_required = True
            log.debug( f"{user.username:<10} | Captcha verification ACTIVATED for user '{user.username}'")


    def generate_token(self, username: str) -> str:
        token = secrets.token_urlsafe(16)
        self.tokens[username] = token
        log.info(f"{username} | generated captcha token: {token}'")
        return token