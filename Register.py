import json
import logging
import requests
from pathlib import Path

# ============================================================
#                        Configuration
# ============================================================
URL = "http://localhost:8080/register"
USERS_FILE = Path("users.json")
LOG_FILE = "register.log"

# ============================================================
#                        Logging Setup
# ============================================================
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logging.getLogger().addHandler(console)

# ============================================================
#                        Functions
# ============================================================
def load_users(json_path: Path):
    if not json_path.exists():
        logging.error(f"Users file not found: {json_path}")
        raise FileNotFoundError("users.json does not exist")

    with open(json_path, "r") as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("JSON root must be a list of objects")
            return data
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in users file: {e}")
            raise

def register_user(session: requests.Session, username: str, password: str):
    payload = {"username": username, "password": password}

    try:
        response = session.post(URL, json=payload, timeout=10)

        if response.status_code == 201:
            logging.info(f"Registered user: {username}")
        else:
            logging.warning(
                f"Failed for user={username} "
                f"status={response.status_code} response={response.text}"
            )
    except requests.RequestException as e:
        logging.error(f"Network error for user {username}: {e}")

# ============================================================
#                        Main Logic
# ============================================================
def main():
    users = load_users(USERS_FILE)
    session = requests.Session()

    for entry in users:
        username = entry.get("username")
        password = entry.get("password")

        if not username or not password:
            logging.warning(f"Skipping invalid entry: {entry}")
            continue

        register_user(session, username, password)

if __name__ == "__main__":
    main()
