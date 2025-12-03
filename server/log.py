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
            "pepper_enable": self.conf.pepper_enable,
            "account_lockout_enable": self.conf.account_lockout_enable,
            "rate_limit_enable": self.conf.rate_limit_enable,

            # Per-request (dynamic) fields
            "username": r["extra"].get("username"),
            "success": r["extra"].get("success"),

            # The message itself becomes failure_reason or success_reason
            "failure_reason": r["message"]
        }

        with open(self.filename, "a") as f:
            f.write(json.dumps(data) + "\n")



def audit(username: str, success: bool, reason: str = "") -> None:
    logger.bind(
        username=username,
        success=success,
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