from typing import Optional

from .base import HashProvider
from .bcrypt import BcryptHashProvider
from .argon2 import Argon2HashProvider
from .sha256 import Sha256HashProvider
from .plain_text import PlainTextProvider
from server.log import logger as log
from server.config.schema import HashingConfig, HashType


class HashProviderFactory:
    def __init__(self, conf: HashingConfig, pepper: Optional[str]):
        if conf.pepper_enable:
            if pepper is None or pepper == "":
                raise RuntimeError("PEPPER environment variable is not set")
            log.info(f"PEPPER environment variable: {pepper}")

        self.conf = conf
        self.pepper = pepper

    def create(self) -> HashProvider:
        providers = {
            HashType.BCRYPT: self._create_bcrypt,
            HashType.ARGON2: self._create_argon2,
            HashType.SHA256: self._create_sha256,
            HashType.DEBUG: self._create_plain,
        }

        builder = providers.get(self.conf.type)
        if not builder:
            raise ValueError(f"Unknown hash type: {self.conf.type}")
        log.info(f"Building hash provider: {self.conf.type}")
        return builder()

    def _create_bcrypt(self) -> HashProvider:
        return BcryptHashProvider(
            self.pepper,
            cost=self.conf.bcrypt_params.cost,
        )

    def _create_argon2(self) -> HashProvider:
        return Argon2HashProvider(
            self.pepper,
            time=self.conf.argon2_params.time,
            memory=self.conf.argon2_params.memory,
            parallelism=self.conf.argon2_params.parallelism,
        )

    def _create_sha256(self) -> HashProvider:
        return Sha256HashProvider(self.pepper)

    def _create_plain(self) -> HashProvider:
        return PlainTextProvider(self.pepper)