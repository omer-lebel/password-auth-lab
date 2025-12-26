from enum import Enum

class StopReason(Enum):
    NONE = "running"
    TIME_EXPIRED = "max_time_reached"
    MAX_ATTEMPTS = "max_attempts_reached"
