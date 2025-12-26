#============== Conifguration =====================#
from http import HTTPStatus

URL = "http://localhost:8080/login"
CAPTCHA_URL = "http://localhost:8080/admin/generate_token"
GROUP_SEED = 509041496

#============== Attacks To Apply =====================#
USER_TO_BRUTE_FORCE = "omer"

#============== Files =====================#
USERS_FILE = "users.txt"
PASSWORDS_FILE = "passwords.txt"
LOG_FILE = "log.txt"

#============== Timeout =====================#
MAX_ATTACK_TIME = 7200 #2 hours 
MAX_ATTEMPTS = 50000
REQUEST_TIMEOUT = 5

#============== Servre Status Codes =====================#
SUCCESS_CODE = HTTPStatus.OK #200
CAPTCHA_CODE = HTTPStatus.PRECONDITION_REQUIRED #428
LOCKED_CODE = HTTPStatus.LOCKED # 423
TOTP_CODE = HTTPStatus.ACCEPTED #202
