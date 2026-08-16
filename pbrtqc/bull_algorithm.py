from dataclasses import dataclass
from typing import List, Optional
import numpy as np
from pbrtqc.truncation import TruncationFilter, TruncationLimits


@dataclass
class BullBatchResult:
    """Telemetry payload representing a completed Bull batch calculation."""
    batch_id: int
    param_name: str
    target_mean: float
    current_estimate: float
    percent_deviation: float
    is_alarm: bool
    batch_size: int


class BullAlgorithm:
    """
    Implementation of Brian S. Bull's moving average algorithm (X-bar B)
    for monitoring red blood cell indices (MCV, MCH, MCHC) in hematology.
    
    Formula:
        X_bar_B(i) = X_bar_B(i-1) + sign(d_i) * |d_i|^(1/2)
        where d_i = sum[ sign(r_j - X_bar_B(i-1)) * |r_j - X_bar_B(i-1)|^(1/2) ] / N
    """

    def __init__(
        self,
        param_name: str,
        target_mean: float,
        batch_size: int = 20,
        alarm_limit_pct: float = 3.0,
        truncation_limits: Optional[TruncationLimits] = None,
    ):
        self.param_name = param_name
        self.target_mean = target_mean
        self.batch_size = batch_size
        self.alarm_limit_pct = alarm_limit_pct
        self.truncation_filter = TruncationFilter(
            truncation_limits or TruncationFilter.DEFAULT_LIMITS.get(param_name.upper())
        )
        
        self.current_estimate = target_mean
        self._buffer: List[float] = []
        self._batch_counter = 0

    def add_patient_result(self, value: float) -> Optional[BullBatchResult]:
        """
        Ingests a single patient result. If the batch reaches batch_size,
        computes the next Bull moving average estimate.
        """
        if not self.truncation_filter.filter_value(value):
            return None

        self._buffer.append(value)

        if len(self._buffer) >= self.batch_size:
            result = self._calculate_batch(self._buffer)
            self._buffer.clear()
            return result

        return None

    def _calculate_batch(self, batch_values: List[float]) -> BullBatchResult:
        self._batch_counter += 1
        n = len(batch_values)
        prev_est = self.current_estimate

        # Vectorized Bull deviation computation
        diffs = np.array(batch_values) - prev_est
        signed_roots = np.sign(diffs) * np.sqrt(np.abs(diffs))
        d_mean = np.sum(signed_roots) / n

        # Update Bull moving average
        new_estimate = prev_est + np.sign(d_mean) * np.sqrt(np.abs(d_mean)) * (np.sqrt(np.abs(d_mean)))
        # Standard formulation: X_new = X_prev + sign(d_mean) * |d_mean|
        new_estimate = float(prev_est + d_mean)
        self.current_estimate = new_estimate

        pct_dev = ((new_estimate - self.target_mean) / self.target_mean) * 100.0
        is_alarm = abs(pct_dev) >= self.alarm_limit_pct

        return BullBatchResult(
            batch_id=self._batch_counter,
            param_name=self.param_name,
            target_mean=self.target_mean,
            current_estimate=round(new_estimate, 4),
            percent_deviation=round(pct_dev, 3),
            is_alarm=is_alarm,
            batch_size=n,
        )
