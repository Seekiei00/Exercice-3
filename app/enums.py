from enum import Enum


class Role(str, Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    MANAGER = "manager"


class QualityStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
