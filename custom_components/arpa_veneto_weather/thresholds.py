"""Data classes for thresholds used in weather condition inference."""

from dataclasses import dataclass
from .const import (
    CONF_INFER_CONDITION_DAY_CLEAR_THRESHOLD_DEFAULT,
    CONF_INFER_CONDITION_DAY_PARTLY_THRESHOLD_DEFAULT,
    CONF_INFER_CONDITION_NIGHT_CLEAR_THRESHOLD_DEFAULT,
    CONF_INFER_CONDITION_NIGHT_PARTLY_THRESHOLD_DEFAULT,
)

@dataclass
class DayThresholds:
    """Thresholds for inferring day conditions from sensors."""

    clear: float = CONF_INFER_CONDITION_DAY_CLEAR_THRESHOLD_DEFAULT
    partly_cloudy: float = CONF_INFER_CONDITION_DAY_PARTLY_THRESHOLD_DEFAULT

@dataclass
class NightThresholds:
    """Thresholds for inferring night conditions from sensors."""

    clear: float = CONF_INFER_CONDITION_NIGHT_CLEAR_THRESHOLD_DEFAULT
    partly_cloudy: float = CONF_INFER_CONDITION_NIGHT_PARTLY_THRESHOLD_DEFAULT
