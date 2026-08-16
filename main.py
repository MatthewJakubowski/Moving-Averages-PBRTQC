import numpy as np
from pbrtqc.bull_algorithm import BullAlgorithm
from pbrtqc.spc_stream import EWMAStreamGuard, CUSUMStreamGuard


def main():
    print("=" * 80)
    print(" 🩸 Moving-Averages-PBRTQC: Real-Time Stream SPC Engine Demo")
    print("=" * 80)

    # 1. Simulate Hematology RBC Stream (Bull's Algorithm on MCV)
    print("\n--- 1. HEMATOLOGY STREAM: Bull's Algorithm (MCV target = 90.0 fL) ---")
    bull = BullAlgorithm(param_name="MCV", target_mean=90.0, batch_size=20, alarm_limit_pct=3.0)

    # Normal population batch followed by analyzer drift (+5 fL)
    stable_results = np.random.normal(90.0, 4.0, 40).tolist()
    drifted_results = np.random.normal(95.0, 4.0, 20).tolist()
    mcv_stream = stable_results + drifted_results

    for i, val in enumerate(mcv_stream, 1):
        res = bull.add_patient_result(val)
        if res:
            status = "🚨 ALARM (DRIFT DETECTED)" if res.is_alarm else "✅ STABLE"
            print(f"[Batch {res.batch_id:02d}] Samples Processed: {i:02d} | "
                  f"Bull MCV: {res.current_estimate:.2f} fL | "
                  f"Dev: {res.percent_deviation:+.2f}% | Status: {status}")

    # 2. Simulate Biochemistry Telemetry (EWMA & CUSUM on Sodium)
    print("\n--- 2. BIOCHEMISTRY STREAM: EWMA & CUSUM (Sodium target = 140.0 mmol/L) ---")
    ewma = EWMAStreamGuard(param_name="SODIUM", target_mean=140.0, target_sd=2.0, lambda_param=0.15)
    cusum = CUSUMStreamGuard(param_name="SODIUM", target_mean=140.0, target_sd=2.0)

    # Generating 50 samples with a gradual positive shift starting at sample 25
    na_stream = np.random.normal(140.0, 2.0, 25).tolist() + np.random.normal(144.5, 2.0, 25).tolist()

    for idx, reading in enumerate(na_stream, 1):
        ewma_val, ewma_alarm = ewma.process_result(reading)
        (s_h, s_l), cusum_alarm = cusum.process_result(reading)

        if ewma_alarm:
            print(f"⚠️ [Sample #{idx:02d}] EWMA ALARM: {ewma_alarm.direction} drift detected! (EWMA: {ewma_val:.2f})")
        if cusum_alarm:
            print(f"🚨 [Sample #{idx:02d}] CUSUM ALARM: Persistent shift detected! (S_high: {s_h:.2f})")


if __name__ == "__main__":
    main()
