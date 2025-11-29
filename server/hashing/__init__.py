from .base import HashProvider
from .bcrypt import BcryptHashProvider
from .sha256 import Sha256HashProvider
from .argon2 import Argon2HashProvider
from .plain_text import PlainTextProvider


def get_hash_provider(hash_type: str) -> HashProvider:
    providers = {
        "bcrypt": BcryptHashProvider(),
        "sha256": Sha256HashProvider(),
        "argon2": Argon2HashProvider(),
        "debug": PlainTextProvider()
    }
    return providers.get(hash_type, BcryptHashProvider())


__all__ = [
    "HashProvider",
    "BcryptHashProvider",
    "Sha256HashProvider",
    "Argon2HashProvider",
    "PlainTextProvider",
    "get_hash_provider"
]
