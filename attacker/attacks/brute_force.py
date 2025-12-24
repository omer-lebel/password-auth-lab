# ============================================================
#                        Imports
# ============================================================
from attacks.base_attack import BaseAttack
from core.LoginResult import LoginResult


# ============================================================
#                   Brute Force Attack Class
# ============================================================
class BruteForceAttack(BaseAttack):
    """
    Implements a brute-force attack against a single user.
    Inherits common attack logic from BaseAttack.
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
        max_attempts,
        user,
        passwords
    ):
        super().__init__(
            client,
            timer,
            success_code,
            lockout_code,
            captcha_code,
            totp_code,
            max_time,
            max_attempts
        )
        self.user = user
        self.passwords = passwords


    # ========================================================
    #                   Attack Execution Logic
    # ========================================================
    def run(self):
        """
        Executes the brute-force attack by iterating over
        a list of passwords for a single target user.
        """

        for password in self.passwords:

            # ------------------------------------------------
            # Check if attack should stop (time / attempts)
            # ------------------------------------------------
            expired, reason = self.attack_expired()
            if expired:
                print(f"[!] Attack stopped: {reason.value}")
                break

            # ------------------------------------------------
            # Attempt login
            # ------------------------------------------------
            result = self.attempt_login(self.user, password)
            self.attempts += 1

            # ------------------------------------------------
            # Handle login result
            # ------------------------------------------------
            if result == LoginResult.SUCCESS:
                print("[!] Attack succeeded")
                break

            if result == LoginResult.PARTIAL_SUCCESS:
                print("[!] Password correct, TOTP required")
                break

            if result == LoginResult.LOCKED:
                print(f"[!] Attack stopped: {self.user.username} is locked out")
                break
