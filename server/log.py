import loguru
from loguru import logger
import json
import sys

class AuditConfig:
    hash_type: str = "sha256"
    pepper_enable: bool = False
    rate_limit_enable: bool = False
    account_lockout_enable: bool = False


class AuditJsonSink:
    def __init__(self, filename: str):
        self.filename = filename

    def __call__(self, msg):
        r = msg.record

        data = {
            "timestamp": r["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],

            # Global config
            "hash_type": AuditConfig.hash_type,
            "pepper_enable": AuditConfig.pepper_enable,
            "rate_limit_enable": AuditConfig.rate_limit_enable,
            "account_lockout_enable": AuditConfig.account_lockout_enable,

            # Per-request (dynamic) fields
            "ip": r["extra"].get("ip"),
            "username": r["extra"].get("username"),
            "attempt_count": r["extra"].get("attempt_count"),
            "success": r["extra"].get("success"),

            # The message itself becomes failure_reason or success_reason
            "failure_reason": r["message"]
        }

        with open(self.filename, "a") as f:
            f.write(json.dumps(data) + "\n")



def audit(ip: str, username: str, attempt_count: int, success: bool, reason: str = "") -> None:
    logger.bind(
        ip=ip,
        username=username,
        success=success,
        attempt_count=attempt_count
    ).log("AUDIT", reason)


def setup_logger(audit_filename: str = "attempt.jsonl"):
    logger.remove()

    # Console for developers only
    logger.add(
        sys.stderr,
        level="DEBUG",
        format="<level>{level:<8}</level> <green>{time:HH:mm:ss}</green> | <level>{message}</level>"
    )

    # Register custom level
    logger.level("AUDIT", no=45, color="<YELLOW>")
    logger.add(AuditJsonSink(audit_filename), level="AUDIT")
    return logger


# Attach the method to logger object
logger.audit = audit

def get_logger():
    return logger