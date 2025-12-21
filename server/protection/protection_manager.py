from typing import List
from server.config.setting import ProtectionConfig
from server.database import User
from .base import Protection, ProtectionResult, AuthContext
from .rate_limmiting import RateLimitProtection
from .account_lockout import AccountLockoutProtection
from .capcha import CaptchaProtection
from .totp import TOTPProtection


class ProtectionManager:
    def __init__(self, conf: ProtectionConfig, group_seed: int):
        self.protections: List[Protection] = []
        self.group_seed = group_seed
        self.captcha = None
        self.totp = None

        if conf.account_lockout.enabled:
            self.protections.append(AccountLockoutProtection(conf.account_lockout))

        if conf.rate_limiting.enabled:
            self.protections.append(RateLimitProtection(conf.rate_limiting))

        if conf.captcha.enabled:
            self.captcha = CaptchaProtection(conf.captcha)
            self.protections.append(self.captcha)

        if conf.totp.enabled:
            self.totp = TOTPProtection(conf.totp)
            self.protections.append(self.totp)

    def validate_request(self, user: User, captcha_token: str, totp_code: str) -> ProtectionResult:
        context = AuthContext(user=user,captcha_token=captcha_token, totp_code=totp_code)
        for protection in self.protections:
            results = protection.validate_request(context)
            if not results.allowed:
                return results
        return ProtectionResult(allowed=True)


    def reset(self, user: User):
        for protection in self.protections:
            protection.reset(user)


    def record_failure(self, user: User):
        for protection in self.protections:
            protection.record_failure(user)


    def generate_captcha_token(self, username: str) -> str:
        if self.captcha is None:
            raise Exception("No captcha available")
        return self.captcha.generate_token(username)


    def verify_totp(self, totp_secret, totp_code):
        if self.totp is None:
            return True
        return self.totp.verify(totp_secret, totp_code)

