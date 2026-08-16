<div align="center">
  <img src="https://raw.githubusercontent.com/MatthewJakubowski/Universal-Lab-Converter/main/going_dark_cover.jpg" width="100%" alt="System Status: Going Dark. Deep Work Protocol.">

# 🩸 Moving-Averages-PBRTQC

### Patient-Based Real-Time Quality Control (PBRTQC) Engine: Bull's Algorithm for Hematology & Stream SPC (EWMA/CUSUM)

[![CI - Pytest Suite](https://github.com/MatthewJakubowski/Moving-Averages-PBRTQC/actions/workflows/ci.yml/badge.svg)](https://github.com/MatthewJakubowski/Moving-Averages-PBRTQC/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3b82f6?logo=python&logoColor=white)](https://github.com/MatthewJakubowski/Moving-Averages-PBRTQC)
[![Metrology Standard](https://img.shields.io/badge/Standard-ISO%2015189%20Metrology-8b5cf6)](https://github.com/MatthewJakubowski/Moving-Averages-PBRTQC)
[![Research & PoC](https://img.shields.io/badge/Status-Educational%20%2F%20PoC-f59e0b)](https://github.com/MatthewJakubowski/Moving-Averages-PBRTQC)
[![License: MIT](https://img.shields.io/badge/License-MIT-06b6d4.svg)](https://opensource.org/licenses/MIT)

> **Continuous Statistical Process Control for Clinical Diagnostic Analyzers**  
> A zero-black-box implementation of patient-based real-time statistical process control (PBRTQC), incorporating Bull's Algorithm ($X_B$) for red blood cell indices, Exponentially Weighted Moving Averages (EWMA), and Cumulative Sum (CUSUM) drift detection.

---

### 🌐 Ecosystem & Professional Profiles

[🌐 Portfolio Hub](https://mateusz-jakubowski.ai.studio/) • [🚀 Project Showroom](https://from-pipette-to-python.ai.studio/) • [💼 LinkedIn](https://www.linkedin.com/in/mateuszjakubowski) • [🐙 GitHub](https://github.com/MatthewJakubowski)  
[🏆 Kaggle](https://www.kaggle.com/matthewjakubowski) • [🤗 Hugging Face](https://huggingface.co/matthewjakubowski) • [𝕏 Twitter / X](https://x.com/M_S_Jakubowski) • [🍷 Vivino](http://www.vivino.com/users/mateusz.jakubowski/)

</div>

---

## 🤖 AI & Learning Transparency

This project documents my technical transition from Medical Diagnostic Analysis to Software Engineering and Explainable AI (**#FromPipetteToPython**).

While the core domain knowledge (clinical hematology constants, electrolyte metrology, preanalytical truncation boundaries, ISO 15189 compliance) stems from my 15 years of experience in clinical diagnostic laboratories, the modular stream algorithms, vectorized variance estimators, and automated testing matrices were engineered with the technical co-pilot assistance of **Google Gemini**.

The entire codebase is developed and tested in a mobile-only engineering environment (**Samsung DeX + Pydroid 3 / Termux**).

---

## 📊 Overview

Traditional internal quality control (IQC) tests commercial control material at fixed intervals (e.g., once every 8 hours), leaving thousands of patient samples vulnerable to undetected analytical shifts between runs.

**Patient-Based Real-Time Quality Control (PBRTQC)** continuously audits the stability of the analytical system using incoming anonymized patient telemetry in real-time.

┌─────────────────────────────────────────────────────────────────────────┐
│                     Continuous Patient Stream                           │
│        (Hematology Analyzers, Biochemistry ISE & Photometers)           │
└────────────────────────────────────┬────────────────────────────────────┘
│ Raw Telemetry Stream
▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 Truncation & Sanitization Filter Layer                  │
│  • Discard extreme pathological values & preanalytical outliers         │
│  • Preserve analytical sensitivity without clinical skew                │
└────────────────────────────────────┬────────────────────────────────────┘
│ Filtered Observations
▼
┌─────────────────────────────────────────────────────────────────────────┐
│               Real-Time Statistical Process Control (SPC)               │
│                                                                         │
│   ├── [Hematology] Bull's Algorithm (X_B)                             │
│   │   • Batch size N=20 for RBC indices (MCV, MCH, MCHC)              │
│   │   • d_j = r_j - X_{B(i-1)}, s_j = \text{sign}(d_j)\sqrt{|d_j|}   │
│   │   • X_{B(i)} = X_{B(i-1)} + \text{sign}(\bar{d})\cdot(\bar{d})^2  │
│   │                                                                     │
│   ├── [Biochemistry] EWMA Stream Guard                                  │
│   │   • Dynamic variance bounds: z_t = \lambda x_t + (1-\lambda)z_{t-1}│
│   │                                                                     │
│   └── [Electrolytes] Tabular CUSUM Guard                                │
│       • High/Low persistent accumulation: S_H, S_L vs threshold h   │
└────────────────────────────────────┬────────────────────────────────────┘
│ Real-time Telemetry & Alarms
▼
┌─────────────────────────────────────────────────────────────────────────┐
│               Automated Analyzer Alerting & Quality Gates               │
│  • Early warning before commercial QC runs                              │
│  • Zero Black-Box | ISO 15189 Metrology Aligned                         │
└─────────────────────────────────────────────────────────────────────────┘


---

## ⚡ Quick Start

```python
from pbrtqc.bull_algorithm import BullAlgorithm
from pbrtqc.spc_stream import EWMAStreamGuard

# 1. Initialize Bull's Algorithm for MCV monitoring (Target = 90.0 fL)
bull = BullAlgorithm(param_name="MCV", target_mean=90.0, batch_size=20, alarm_limit_pct=3.0)

# Feed patient telemetry
for mcv_val in [89.2, 91.0, 90.4, 88.9]:  # stream feeds in real-time
    batch_result = bull.add_patient_result(mcv_val)
    if batch_result:
        print(f"Batch {batch_result.batch_id} Estimate: {batch_result.current_estimate} fL")

# 2. Initialize EWMA for Sodium monitoring
ewma = EWMAStreamGuard(param_name="SODIUM", target_mean=140.0, target_sd=2.0, lambda_param=0.15)

current_val, alarm = ewma.process_result(147.5)
if alarm:
    print(f"Triggered {alarm.algorithm} Alarm ({alarm.direction}) at sample #{alarm.sample_index}")
```

## 🧪 Unit Testing
​Run the automated test suite verifying Bull's algorithm mathematical stability, truncation thresholds, and SPC alarm triggers:
```bash
pytest tests/ -v
```
## 👨‍💻 About the Author
​Matthew (Mateusz) Jakubowski
Senior Laboratory Technologist & Healthcare Data Engineer
Creator of the #FromPipetteToPython initiative.
​With over 15 years of hands-on experience in high-throughput clinical diagnostic laboratories, I bridge the gap between laboratory medicine and modern data science. My engineering focus centers on Explainable AI (XAI), Statistical Quality Control (ISO 15189), and deterministic hardware interoperability—building robust, transparent tools that eliminate "black-box" risks in healthcare analytics.
​Domain Expertise: Clinical Laboratory Diagnostics, Hematology & Biochemistry Automation, LIS/HIS Interoperability, Statistical Metrology (6\sigma, Westgard Multirule).
​Engineering Stack: Python, Pandas, Scikit-Learn, Pytest, FastAPI, Docker, Google Colab.
​Development Environment: 100% Mobile-First Engineering on Samsung DeX (Galaxy S24 Ultra & Tab S11 Ultra) via Termux, Pydroid 3, and Google AI Studio.
## ​⚖️ Legal & Medical Device Disclaimer
​IMPORTANT NOTICE / NON-MEDICAL SOFTWARE DISCLAIMER:
​Educational & Research Proof of Concept (PoC): This repository is developed solely for educational, technical demonstrative, and scientific research purposes under the #FromPipetteToPython initiative.
​Not a Certified Medical Device: This software is NOT a certified Medical Device (neither CE-IVD, IVDR 2017/746, nor FDA 510(k)/SaMD certified). It is not intended, designed, or approved for clinical decision-making, direct patient diagnosis, treatment monitoring, or live medical diagnostic execution without human verification.
​No Clinical Liability: All data processed in examples or unit tests are synthetic or anonymized mock datasets. The author disclaims any express or implied liability for errors, analytical discrepancies, or data integrity issues resulting from the direct or indirect use of this code in clinical or commercial production environments.
​Provided "AS IS": The software is provided under the terms of the MIT License, without warranty of any kind.
## ​🛡️ License
​Distributed under the MIT License.
