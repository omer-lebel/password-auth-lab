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
    bcrypt_params: BcryptParams = Field(default_factory=BcryptParams)
    argon2_params: Argon2Params = Field(default_factory=Argon2Params)


# -------------------------- protection --------------------------
class ProtectionConfig(BaseModel):
    class PepperConfig(BaseModel):
        enabled: bool = True
        secret: str = Field(min_length=1)

    pepper: PepperConfig