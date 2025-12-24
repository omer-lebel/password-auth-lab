#============== Conifguration =====================#
URL = "http://localhost:8080/login"
CAPTCHA_URL = "http://localhost:8080/admin/generate_token"
GROUP_SEED = 509041496

#============== Attacks To Apply =====================#
APPLY_PASSWORD_SPRAY = False
APPLY_BRUTE_FORCE = True
USER_TO_BRUTE_FORCE = "david"

#============== Files =====================#
USERS_FILE = "users.txt"
PASSWORDS_FILE = "passwords.txt"
LOG_FILE = "log.txt"

#============== Timeout =====================#
MAX_ATTACK_TIME = 7200 #2 hours 
MAX_ATTEMPTS = 50000
REQUEST_TIMEOUT = 5

#============== Servre Status Codes =====================#
SUCCESS_CODE = 200
CAPTCHA_CODE = 403
LOCKED_CODE = 423
TOTP_CODE = 202
