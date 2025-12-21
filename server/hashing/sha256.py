import hashlib
import hmac
import secrets

from .base import HashProvider
from server.log import logger as log

class Sha256HashProvider(HashProvider):
    def __init__(self, pepper: str = ""):
        super().__init__(pepper)
        self.salt_length = 16
        log.info(f'Sha256 initialized with salt length:{self.salt_length}')


    def hash_password(self, password: str) -> str:
        salt = secrets.token_hex(self.salt_length)
        combined = (password + salt + self.pepper).encode('utf-8')
        hash_value = hashlib.sha256(combined).hexdigest()

        # '$' is not a hex character, therefore it is guaranteed to be a unique separator
        return f"{salt}${hash_value}"


    def verify_password(self, plain_password: str, stored_password: str) -> bool:

        # extract salt
        if "$" not in stored_password:
            return False
        salt, stored_hash = stored_password.split("$", 1)

        # calc the hash
        combined = (plain_password + salt + self.pepper).encode('utf-8')
        new_hash = hashlib.sha256(combined).hexdigest()

        # compare using the constant-time comparison to prevent timing attacks
        return hmac.compare_digest(new_hash, stored_hash)