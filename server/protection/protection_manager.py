from typing import List
from server.config.schema import ProtectionConfig
from server.models import User
from .base import Protection, ProtectionResult
from .rate_limmiting import RateLimitProtection
from .account_lockout import AccountLockoutProtection



class ProtectionManager:
    def __init__(self, conf: ProtectionConfig):
        self.protections: List[Protection] = []

        if conf.account_lockout.enabled:
            self.protections.append(AccountLockoutProtection(conf.account_lockout))

        if conf.rate_limiting.enabled:
            self.protections.append(RateLimitProtection(conf.rate_limiting))


    def validate_request(self, user: User) -> ProtectionResult:
        results = []
        for p in self.protections:
            results.append(p.validate_request(user))

        # find the first failing result
        fail = next((r for r in results if not r.allowed), None)
        if fail:
            return fail
        return ProtectionResult(allowed=True)


    def reset(self, user: User):
        for protection in self.protections:
            protection.reset(user)


    def record_failure(self, user: User):
        for protection in self.protections:
            protection.record_failure(user)