from pydantic_settings import BaseSettings
import json
from .schema import DatabaseConfig, LoggingConfig, HashingConfig, ProtectionConfig


class AppConfig(BaseSettings):
    database: DatabaseConfig
    logging: LoggingConfig
    hashing: HashingConfig
    protection: ProtectionConfig

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
