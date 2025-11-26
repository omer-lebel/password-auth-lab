import requests

URL = "http://localhost:8000/register"

payload = {
    "username": "tomer",
    "password": "1234"
}

response = requests.post(URL, json=payload)

print("Status Code:", response.status_code)
print("Response:", response.text)
