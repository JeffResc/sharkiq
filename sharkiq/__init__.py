"""Python API for Shark IQ vacuum robots"""

from .ayla_api import get_ayla_api, AylaApi
from .exc import (
    SharkIqError,
    SharkIqAuthExpiringError,
    SharkIqNotAuthedError,
    SharkIqAuthError,
    SharkIqReadOnlyPropertyError,
)
from .sharkiq import OperatingModes, PowerModes,  Properties, SharkIqVacuum

__version__ = '0.0.1'
