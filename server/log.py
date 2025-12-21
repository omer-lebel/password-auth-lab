from loguru import logger
from dataclasses import dataclass
import json
import sys

@dataclass
class AuditConfig:
    hash_type: str
    pepper_enable: bool
    account_lockout_enable: bool
    rate_limit_enable: bool
    captcha_enable: bool
    totp_enable: bool


class AuditJsonSink:
    def __init__(self, filename: str, conf: AuditConfig):
        self.filename = filename
        self.conf = conf

    def __call__(self, msg):
        r = msg.record

        data = {
            "timestamp": r["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],


            # Global config
            "hash_type": self.conf.hash_type,
            "pepper": self.conf.pepper_enable,
            "account_lockout": self.conf.account_lockout_enable,
            "rate_limit": self.conf.rate_limit_enable,

            # Per-request (dynamic) fields
            "username": r["extra"].get("username"),
            "success": r["extra"].get("success"),
            "failure_reason": r["message"],

            # Metrics from middleware
            "latency_ms": r["extra"].get("latency_ms"),
            "cpu_usage_ms": r["extra"].get("cpu_usage_ms"),
            "memory_delta_mb": r["extra"].get("memory_delta_mb"),
        }

        with open(self.filename, "a") as f:
            f.write(json.dumps(data) + "\n")



def audit(username: str, success: bool, reason: str = "", latency_ms: float = 0.0,
          cpu_usage_ms: float = 0.0, memory_delta_mb: float = 0.0) -> None:
    logger.bind(
        username=username,
        success=success,
        latency_ms=latency_ms,
        cpu_usage_ms=cpu_usage_ms,
        memory_delta_mb=memory_delta_mb
    ).log("AUDIT", reason)

def setup_logger(audit_config : AuditConfig, audit_filename: str = "attempt.jsonl"):
    logger.remove()

    # Console for developers only
    logger.add(
        sys.stderr,
        level="DEBUG",
        format="<level>{level:<8}</level> <green>{time:HH:mm:ss}</green> | <level>{message}</level>"
    )

    # Register custom level
    logger.level("AUDIT", no=45, color="<YELLOW>")
    logger.add(AuditJsonSink(audit_filename, audit_config), level="AUDIT")
    return logger


# Attach the method to logger object
logger.audit = audit

def get_logger():
    return logger