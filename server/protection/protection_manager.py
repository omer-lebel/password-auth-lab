from typing import List
from server.config.setting import ProtectionConfig
from server.database import User
from .base import Protection, ProtectionResult, AuthContext
from .rate_limmiting import RateLimitProtection
from .account_lockout import AccountLockoutProtection
from .capcha import CaptchaProtection


class ProtectionManager:
    def __init__(self, conf: ProtectionConfig, group_seed: int):
        self.protections: List[Protection] = []
        self.group_seed = group_seed
        self.captcha = None

        if conf.account_lockout.enabled:
            self.protections.append(AccountLockoutProtection(conf.account_lockout))

        if conf.rate_limiting.enabled:
            self.protections.append(RateLimitProtection(conf.rate_limiting))

        if conf.captcha.enabled:
            self.captcha = CaptchaProtection(conf.captcha)
            self.protections.append(self.captcha)


    def validate_request(self, user: User, captcha_token: str) -> ProtectionResult:
        context = AuthContext(user=user,captcha_token=captcha_token)
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

