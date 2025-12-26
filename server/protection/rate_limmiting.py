import time
from http import HTTPStatus

from server.log import logger as log
from .base import Protection, ProtectionResult, AuthContext
from server.database import User
from server.config import RateLimitingConfig


class RateLimitProtection(Protection):
    def __init__(self, conf: RateLimitingConfig):
        self.window_seconds = conf.window_seconds
        self.max_attempts = conf.max_attempt_per_time
        self.initial_lock_second = conf.initial_lock_second
        log.info(
            f"Rate Limit initialized (window={self.window_seconds}s, max={self.max_attempts}, "
            f"initial_lock={self.initial_lock_second}s)"
        )

    def validate_request(self, context: AuthContext) -> ProtectionResult:
        now = time.time()
        user = context.user
        if user.lockout_until and now < user.lockout_until:
            remaining = user.lockout_until - now
            m = int(remaining // 60)
            s = int(remaining % 60)
            log.debug(f"{user.username:<10} | Rate limit active "
                      f"(remaining time={int(remaining)}s | lockout_count={user.lockout_count})")

            return ProtectionResult(
                allowed=False,
                reason="rate limiting",
                user_msg=f"Rate limited, try again in {m} min {s} sec",
                status_code=HTTPStatus.TOO_MANY_REQUESTS
            )

        return ProtectionResult(allowed=True)


    def record_failure(self, user: User) -> None:
        """
        Update sliding window, then check if exceeded limit
        """
        now = time.time()

        # Update window
        attempts = [ts for ts in user.rate_attempts if now - ts < self.window_seconds]
        attempts.append(now)
        user.rate_attempts = attempts
        log.debug(f"{user.username:<10} | attempts in last {self.window_seconds}s: {len(attempts)}/{self.max_attempts}")

        #  Check if exceeded rate limit
        if len(attempts) >= self.max_attempts:
            lock_time = self.initial_lock_second * (2 ** user.lockout_count)
            user.lockout_until = int(now + lock_time)
            user.lockout_count += 1
            user.rate_attempts = []
            log.debug(f"{user.username:<10} | EXCEEDED rate limit. Locking for {lock_time}s (lockout_count={user.lockout_count})")

    def reset(self, user: User) -> None:
        user.rate_attempts = []
        user.lockout_count = 0
        user.lockout_until = None
