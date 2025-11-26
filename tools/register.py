import requests

URL = "http://localhost:8000/register"
with open("users.txt") as f:
    for line in f.readlines():
        username, password = line.strip().split(":")
        payload = {
            "username": username,
            "password": password
        }

        response = requests.post(URL, json=payload)

        print("Status Code:", response.status_code)
        print("Response:", response.text)
