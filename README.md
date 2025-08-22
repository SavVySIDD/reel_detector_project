# Reel vs Non-Reel Traffic Detector (Prototype)

This repository contains an end-to-end prototype to detect **Reel (short-form video)** vs **Non-Reel** traffic using **network metadata** (no payload inspection) and a lightweight on-device model.

## Structure

```
reel_detector_project/
├─ android/               # Android app skeleton (Kotlin)
│  ├─ app/
│     ├─ src/main/java/com/example/reeldetector/
│     ├─ src/main/res/layout/
│     └─ src/main/assets/
├─ notebooks/             # Python scripts for data, features, training, conversion
├─ data/                  # raw captures (.pcap or collector CSV) and generated windows (not included)
├─ models/                # saved model.h5, model_quant.tflite, scaler.json (generated locally)
├─ scripts/               # helper scripts
├─ docs/                  # documentation, demo plan
└─ demo/                  # demo recording & slides
```

## Quickstart (use Python virtualenv)

1. Create venv and install:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install numpy pandas scikit-learn matplotlib seaborn tensorflow pyshark tqdm
```

2. Generate synthetic data to test pipeline:
```bash
python notebooks/demo_synthetic_data.py
```

3. Train and convert to TFLite:
```bash
python notebooks/train_and_convert.py ../data/windows_labeled_synthetic.csv
```

4. Evaluate TFLite locally:
```bash
python notebooks/eval_tflite.py
```

5. Copy `models/model_quant.tflite` and `models/scaler.json` into `android/app/src/main/assets/` to test Android integration.

## Datasets (recommended to download and use for improved models)
- CICIDS2017 / CIC-IDS: realistic network traffic datasets (pcap + flows).
- UNSW-NB15: network traffic with attacks and normal flows.
- Custom captures from Android `VpnService` (recommended): capture labeled REEL vs NON-REEL sessions.

> This repo does NOT include datasets or pre-trained models for privacy and size reasons. Use the provided scripts to generate and train locally.

## Contact / Notes
Follow the instructions in `notebooks/` for full pipeline. The Android skeleton is minimal; you will need to integrate model and scaler and test on a real device.

