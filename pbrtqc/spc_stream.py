from dataclasses import dataclass
from typing import Optional
import numpy as np
from pbrtqc.truncation import TruncationFilter, TruncationLimits


@dataclass
class SPCAlarm:
    sample_index: int
    param_name: str
    algorithm: str
    metric_value: float
    threshold: float
    direction: str  # 'HIGH' or 'LOW'


class EWMAStreamGuard:
    """
    Exponentially Weighted Moving Average (EWMA) for continuous clinical telemetry.
    Ideal for detecting moderate shifts in high-throughput biochemistry parameters.
    """

    def __init__(
        self,
        param_name: str,
        target_mean: float,
        target_sd: float,
        lambda_param: float = 0.1,
        control_limit_sigma: float = 3.0,
        truncation_limits: Optional[TruncationLimits] = None,
    ):
        self.param_name = param_name
        self.target_mean = target_mean
        self.target_sd = target_sd
        self.lambda_param = lambda_param
        self.control_limit_sigma = control_limit_sigma
        self.truncation_filter = TruncationFilter(
            truncation_limits or TruncationFilter.DEFAULT_LIMITS.get(param_name.upper())
        )
        
        self.current_ewma = target_mean
        self.sample_count = 0

    def process_result(self, value: float) -> Tuple_SPC:
        if not self.truncation_filter.filter_value(value):
            return self.current_ewma, None

        self.sample_count += 1
        self.current_ewma = (self.lambda_param * value) + ((1.0 - self.lambda_param) * self.current_ewma)

        # Dynamic standard error of EWMA based on sample depth
        variance_factor = (self.lambda_param / (2.0 - self.lambda_param)) * (
            1.0 - (1.0 - self.lambda_param) ** (2 * self.sample_count)
        )
        sigma_ewma = self.target_sd * np.sqrt(variance_factor)
        ucl = self.target_mean + (self.control_limit_sigma * sigma_ewma)
        lcl = self.target_mean - (self.control_limit_sigma * sigma_ewma)

        alarm = None
        if self.current_ewma > ucl:
            alarm = SPCAlarm(self.sample_count, self.param_name, "EWMA", self.current_ewma, ucl, "HIGH")
        elif self.current_ewma < lcl:
            alarm = SPCAlarm(self.sample_count, self.param_name, "EWMA", self.current_ewma, lcl, "LOW")

        return self.current_ewma, alarm


class CUSUMStreamGuard:
    """
    Cumulative Sum (CUSUM) Control Engine for detecting persistent small shifts
    (e.g., 0.5 - 1.5 SD) in electrolyte electrodes and photometry.
    """

    def __init__(
        self,
        param_name: str,
        target_mean: float,
        target_sd: float,
        allowance_k: float = 0.5,
        decision_limit_h: float = 4.5,
        truncation_limits: Optional[TruncationLimits] = None,
    ):
        self.param_name = param_name
        self.target_mean = target_mean
        self.target_sd = target_sd
        self.k = allowance_k
        self.h = decision_limit_h
        self.truncation_filter = TruncationFilter(
            truncation_limits or TruncationFilter.DEFAULT_LIMITS.get(param_name.upper())
        )

        self.s_high = 0.0
        self.s_low = 0.0
        self.sample_count = 0

    def process_result(self, value: float) -> Tuple_CUSUM:
        if not self.truncation_filter.filter_value(value):
            return (self.s_high, self.s_low), None

        self.sample_count += 1
        z = (value - self.target_mean) / self.target_sd

        # Tabular CUSUM updates
        self.s_high = max(0.0, self.s_high + z - self.k)
        self.s_low = max(0.0, self.s_low - z - self.k)

        alarm = None
        if self.s_high > self.h:
            alarm = SPCAlarm(self.sample_count, self.param_name, "CUSUM", self.s_high, self.h, "HIGH")
        elif self.s_low > self.h:
            alarm = SPCAlarm(self.sample_count, self.param_name, "CUSUM", self.s_low, self.h, "LOW")

        return (self.s_high, self.s_low), alarm


# Type aliases for clean type-hinting
Tuple_SPC = tuple[float, Optional[SPCAlarm]]
Tuple_CUSUM = tuple[tuple[float, float], Optional[SPCAlarm]]
