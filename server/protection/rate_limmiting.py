import time
import json

from server.log import logger as log
from .base import Protection, ProtectionResult
from server.models import User
from server.config.schema import RateLimitingConfig


class RateLimitProtection(Protection):
    def __init__(self, conf: RateLimitingConfig):
        self.window_seconds = conf.window_seconds
        self.max_attempts = conf.max_attempt_per_time
        self.initial_lock_second = conf.initial_lock_second

    def validate_request(self, user: User) -> ProtectionResult:
        now = time.time()
        if user.lockout_until and now < user.lockout_until:
            remaining = user.lockout_until - now
            m = remaining // 60
            s = remaining % 60
            return ProtectionResult(
                allowed=False,
                reason= "rate limiting",
                user_msg = f"Rate limited, try again in {m}m :{s}s",
                status_code=429
            )
        return ProtectionResult(allowed=True)

    def record_failure(self, user: User) -> None:
        """
        Update sliding window, then check if exceeded limit
        """
        now = time.time()

        # Update window
        attempts = self.get_rate_attempts(user.rate_attempts_json)
        attempts = [ts for ts in attempts if now - ts < self.window_seconds]
        attempts.append(now)
        self.set_rate_attempts(user, attempts)

        #  Check if exceeded rate limit
        if len(attempts) > self.max_attempts:
            lock_time = self.initial_lock_second * (2 ** user.lockout_count)
            user.lockout_until = int(now + lock_time)
            user.lockout_count += 1
            self.set_rate_attempts(user, [])

    def reset(self, user: User) -> None:
        self.set_rate_attempts(user, [])
        user.lockout_count = 0
        user.lockout_until = None

    @staticmethod
    def get_rate_attempts(rate_attempts_str: str) -> list[float]:
        try:
            return json.loads(rate_attempts_str)
        except json.decoder.JSONDecodeError:
            return []

    @staticmethod
    def set_rate_attempts(user, attempts):
        user.rate_attempts_json = json.dumps(attempts)
