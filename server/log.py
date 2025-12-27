from pathlib import Path

from loguru import logger
from dataclasses import dataclass
import json
import sys

from server.config import LogLevel

AUDIT_FILE: str = "attempt.jsonl"

@dataclass
class AuditConfig:
    hash_type: str
    pepper_enable: bool
    account_lockout_enable: bool
    rate_limit_enable: bool
    captcha_enable: bool
    totp_enable: bool


class AuditJsonSink:
    def __init__(self,conf: AuditConfig, output_dir: Path):
        self.conf = conf
        file_path = output_dir / "attempt.jsonl"
        self._file = open(file_path, "a", encoding="utf-8", buffering=1)

    def __call__(self, msg):
        r = msg.record

        data = {
            "timestamp": r["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],

            # Global config
            "hash_type": self.conf.hash_type,
            "pepper": self.conf.pepper_enable,
            "account_lockout": self.conf.account_lockout_enable,
            "rate_limit": self.conf.rate_limit_enable,
            "captcha": self.conf.captcha_enable,
            "totp": self.conf.totp_enable,

            # per-request fields (dynamic)
            "username": r["extra"].get("username"),
            "password_score": r["extra"].get("password_score"),
            "success": r["extra"].get("success"),
            "failure_reason": r["message"],

            # server metrics from middleware
            "latency_ms": r["extra"].get("latency_ms"),
            "cpu_usage_ms": r["extra"].get("cpu_usage_ms"),
            "memory_delta_mb": r["extra"].get("memory_delta_mb"),
        }
        self._file.write(json.dumps(data) + "\n")

        def __del__(self):
            if hasattr(self, "_file") and not self._file.closed:
                self._file.close()


def audit(username: str, password_score: str, success: bool, reason: str, latency_ms: float,
          cpu_usage_ms: float, memory_delta_mb: float) -> None:
    logger.bind(
        username=username,
        password_score = password_score,
        success=success,
        latency_ms=latency_ms,
        cpu_usage_ms=cpu_usage_ms,
        memory_delta_mb=memory_delta_mb
    ).log("AUDIT", reason)

def setup_logger(audit_config : AuditConfig, log_level: LogLevel, output_dir: Path) :
    logger.remove()

    # Console for developers only
    logger.add(
        sys.stderr,
        level=log_level,
        format=(
            "<level>{level:<5}</level> | "
            "<level>{time:HH:mm:ss}</level> | "
            "<magenta>{module:<15}</magenta> | "
            "<level>{message}</level>"
        )  )

    # Register custom level
    logger.level("AUDIT", no=45, color="<YELLOW>")
    sink = AuditJsonSink(conf=audit_config, output_dir=output_dir)
    logger.add(sink, level="AUDIT")
    return logger


# Attach the method to logger object
logger.audit = audit

def get_logger():
    return logger
