import pytest
import numpy as np
from pbrtqc.truncation import TruncationFilter, TruncationLimits
from pbrtqc.bull_algorithm import BullAlgorithm
from pbrtqc.spc_stream import EWMAStreamGuard, CUSUMStreamGuard


def test_truncation_filter():
    limits = TruncationLimits("POTASSIUM", lower_limit=2.5, upper_limit=7.0)
    t_filter = TruncationFilter(limits)

    # Valid values
    assert t_filter.filter_value(4.2) is True
    assert t_filter.filter_value(2.5) is True
    assert t_filter.filter_value(7.0) is True

    # Out-of-boundary outliers
    assert t_filter.filter_value(1.8) is False
    assert t_filter.filter_value(9.5) is False
    assert t_filter.filter_value(np.nan) is False

    # Batch filtering
    batch = [4.0, 1.2, 5.1, 8.9, 4.8]
    filtered = t_filter.filter_batch(batch)
    assert filtered == [4.0, 5.1, 4.8]


def test_bull_algorithm_stable_series():
    # Target MCV = 90.0 fL, batch size = 20
    bull = BullAlgorithm(param_name="MCV", target_mean=90.0, batch_size=20, alarm_limit_pct=3.0)

    # Ingest 19 stable values -> no batch completed yet
    for _ in range(19):
        res = bull.add_patient_result(90.0)
        assert res is None

    # 20th value completes the batch
    res = bull.add_patient_result(90.0)
    assert res is not None
    assert res.batch_id == 1
    assert res.param_name == "MCV"
    assert res.current_estimate == pytest.approx(90.0, abs=0.1)
    assert res.percent_deviation == pytest.approx(0.0, abs=0.1)
    assert res.is_alarm is False


def test_bull_algorithm_drift_alarm():
    # Target MCV = 90.0 fL
    bull = BullAlgorithm(param_name="MCV", target_mean=90.0, batch_size=20, alarm_limit_pct=3.0)

    # Ingest shifted batch (mean around 95.0 fL -> > 3% deviation)
    res = None
    for _ in range(20):
        res = bull.add_patient_result(95.0)

    assert res is not None
    assert res.is_alarm is True
    assert res.percent_deviation > 3.0


def test_ewma_stream_guard():
    # Sodium baseline: mean = 140.0, SD = 2.0
    ewma = EWMAStreamGuard(param_name="SODIUM", target_mean=140.0, target_sd=2.0, lambda_param=0.2)

    # Ingest stable results
    for _ in range(15):
        val, alarm = ewma.process_result(140.0)
        assert alarm is None

    # Ingest severe positive drift (148.0 mmol/L)
    alarm_triggered = False
    for _ in range(20):
        _, alarm = ewma.process_result(148.0)
        if alarm is not None:
            alarm_triggered = True
            assert alarm.algorithm == "EWMA"
            assert alarm.direction == "HIGH"
            break

    assert alarm_triggered is True


def test_cusum_stream_guard():
    # Potassium baseline: mean = 4.50, SD = 0.20
    cusum = CUSUMStreamGuard(param_name="POTASSIUM", target_mean=4.50, target_sd=0.20)

    # Ingest normal stable readings
    for _ in range(10):
        (s_h, s_l), alarm = cusum.process_result(4.50)
        assert alarm is None
        assert s_h == 0.0
        assert s_l == 0.0

    # Ingest systematic shift (+1.5 SD -> 4.80 mmol/L)
    alarm_triggered = False
    for _ in range(15):
        _, alarm = cusum.process_result(4.80)
        if alarm is not None:
            alarm_triggered = True
            assert alarm.algorithm == "CUSUM"
            assert alarm.direction == "HIGH"
            break

    assert alarm_triggered is True
