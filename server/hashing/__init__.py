from .base import HashProvider
from .bcrypt import BcryptHashProvider
from .sha256 import Sha256HashProvider
from .argon2 import Argon2HashProvider
from .plain_text import PlainTextProvider
from server.config.schema import HashingConfig, HashType


def get_hash_provider(conf: HashingConfig) -> HashProvider:

    providers = {
        HashType.BCRYPT: lambda: BcryptHashProvider(
            cost=conf.bcrypt_params.cost
        ),
        HashType.ARGON2: lambda: Argon2HashProvider(
            time=conf.argon2_params.time,
            memory=conf.argon2_params.memory,
            parallelism=conf.argon2_params.parallelism
        ),
        HashType.SHA256: lambda: Sha256HashProvider(),
        HashType.DEBUG: lambda: PlainTextProvider()
    }

    hasher = providers.get(conf.type)
    if not hasher:
        raise ValueError(f"Unknown hash type: {conf.type}")

    return hasher()

__all__ = [
    "HashProvider",
    "get_hash_provider"
]
