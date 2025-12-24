import requests
class HttpClient:
    def __init__(self, url,captcha_url,group_seed,timeout):
        self.url = url
        self.captcha_url = captcha_url
        self.group_seed = group_seed
        self.timeout = timeout
        self.session = requests.Session()

    def login(self, username, password,captcha_token=None):
        payload = {
            "username": username,
            "password": password
        }
        #Captcha is required
        if captcha_token:
            payload["captcha_token"] = captcha_token
        try:
            response = self.session.post(
                self.url,
                json=payload,
                timeout=self.timeout
            )
            return response

        except requests.exceptions.Timeout:
            print(f"[TIMEOUT] Server timeout for user '{username}'")
            return None

        except requests.exceptions.ConnectionError:
            print("[ERROR] Connection error ,is the server running?")
            return None

        except Exception as e:
            raise(f"[ERROR] Unexpected request error: {e}")
            return None

    def handle_captcha(self, username):
        try:
            payload = {
                "username": username,
                "input_group_seed": self.group_seed
            }
            response = self.session.post(
            f"{self.captcha_url}/{self.group_seed}?username={username}",
            timeout=self.timeout
)

            if response.status_code == 200:
                return response.json().get("captcha_token")
            print(f"[ERROR] Failed captcha request, status={response.status_code}")
            return None
        except Exception as e:
            print(f"[ERROR] captcha request failed for {username}: {e}")
            return None

