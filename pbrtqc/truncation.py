from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np


@dataclass(frozen=True)
class TruncationLimits:
    """Defines physiological and statistical boundary limits for PBRTQC."""
    param_name: str
    lower_limit: float
    upper_limit: float


class TruncationFilter:
    """
    Sanitizes raw patient result streams by discarding extreme pathological
    or preanalytically compromised values before calculating moving averages.
    """

    # Standard Clinical Truncation Limits (Adult cohort baseline)
    DEFAULT_LIMITS = {
        "MCV": TruncationLimits("MCV", lower_limit=60.0, upper_limit=120.0),
        "MCH": TruncationLimits("MCH", lower_limit=20.0, upper_limit=40.0),
        "MCHC": TruncationLimits("MCHC", lower_limit=280.0, upper_limit=380.0),
        "POTASSIUM": TruncationLimits("POTASSIUM", lower_limit=2.5, upper_limit=7.0),
        "SODIUM": TruncationLimits("SODIUM", lower_limit=115.0, upper_limit=160.0),
        "GLUCOSE": TruncationLimits("GLUCOSE", lower_limit=50.0, upper_limit=300.0),
    }

    def __init__(self, limits: Optional[TruncationLimits] = None):
        self.limits = limits

    def filter_value(self, value: float) -> bool:
        """Returns True if the value is within acceptable truncation limits."""
        if self.limits is None:
            return True
        if np.isnan(value):
            return False
        return self.limits.lower_limit <= value <= self.limits.upper_limit

    def filter_batch(self, values: List[float]) -> List[float]:
        """Filters a list of values, discarding out-of-boundary outliers."""
        if self.limits is None:
            return [v for v in values if not np.isnan(v)]
        return [v for v in values if self.filter_value(v)]
