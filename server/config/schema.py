from pydantic import BaseModel, Field
from enum import Enum


# -------------------------- Enums --------------------------
class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class HashType(str, Enum):
    BCRYPT = "bcrypt"
    ARGON2 = "argon2"
    SHA256 = "sha256"
    DEBUG = "debug"


# -------------------------- database --------------------------
class DatabaseConfig(BaseModel):
    path: str


# -------------------------- logging --------------------------
class LoggingConfig(BaseModel):
    path: str
    level: LogLevel = LogLevel.INFO


# -------------------------- hashing --------------------------
class HashingConfig(BaseModel):
    class BcryptParams(BaseModel):
        cost: int = Field(ge=4, le=31)

    class Argon2Params(BaseModel):
        time: int = Field(ge=1)
        memory: int = Field(ge=8)
        parallelism: int = Field(ge=1)

    type: HashType
    pepper_enable: bool
    bcrypt_params: BcryptParams = Field(default_factory=BcryptParams)
    argon2_params: Argon2Params = Field(default_factory=Argon2Params)


# -------------------------- protection --------------------------
class AccountLockoutConfig(BaseModel):
    enabled: bool
    max_failed_attempts: int = Field(ge=1)

class RateLimitingConfig(BaseModel):
    enabled: bool
    window_seconds: int = Field(ge=1)
    max_attempt_per_time: int = Field(ge=1)
    initial_lock_second: int = Field(ge=1)

class ProtectionConfig(BaseModel):
    account_lockout: AccountLockoutConfig
    rate_limiting: RateLimitingConfig