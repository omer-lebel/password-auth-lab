from pydantic_settings import BaseSettings
import json
from server.config.setting import LogLevel, HashingConfig, ProtectionConfig


class AppConfig(BaseSettings):
    group_seed: int
    log_level: LogLevel
    hashing: HashingConfig
    protection: ProtectionConfig

    PEPPER: str | None = None
    class Config:
        env_file = "server/.env"

    @classmethod
    def from_json(cls, file_path: str) -> "AppConfig":
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error parsing config: {str(e)}")