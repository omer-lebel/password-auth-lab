import requests


#=======Parameters==========#
URL = "http://localhost:8080/login"
session = requests.Session()
username = "michael"
password = "Aa123456"

#==========Function==============#
def check_single_login(username: str, password: str):
    """Attempt one login and print the response safely."""
    payload = {
        "username": username,
        "password": password
    }

    print(f"[*] Trying login: user={username}, pass={password}")

    try:
        response = session.post(URL, json=payload, timeout=5)

        print(f"[+] HTTP Status: {response.status_code}")
        print(f"[+] Response Body: {response.text}")

    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out (server did not reply).")

    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to server.")

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

#=========Main============#
def main():
        check_single_login(username,password)

if __name__ == "__main__":
        main()
