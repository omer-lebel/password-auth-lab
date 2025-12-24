from enum import Enum

class LoginResult(Enum):
    SUCCESS = "success"              # password + all checks passed
    PARTIAL_SUCCESS = "totp_required"  # password correct, TOTP missing/invalid
    FAILED = "failed"                # wrong credentials
    LOCKED = "locked"                # account locked
    STOP = "stop"
