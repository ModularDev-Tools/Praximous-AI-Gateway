# core/enums.py
from enum import Enum

class LicenseTier(Enum):
    COMMUNITY = "community"
    PRO = "pro"
    ENTERPRISE = "enterprise"