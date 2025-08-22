# notebooks/demo_synthetic_data.py
# Generates a synthetic labeled windows CSV so you can test the entire pipeline without real captures.

import numpy as np
import pandas as pd
import os, random

def generate_synthetic_windows(n=2000, out_csv='../data/windows_labeled_synthetic.csv', seed=42):
    random.seed(seed); np.random.seed(seed)
    rows = []
    for i in range(n):
        label = 1 if random.random() < 0.5 else 0
        if label == 1:
            bytes_down = int(max(10000, np.random.normal(200000, 50000)))
            pkt_count_down = int(max(10, np.random.normal(80, 20)))
            iat_mean = max(0.002, np.random.normal(0.02, 0.01))
            burst = int(np.random.poisson(7))
        else:
            bytes_down = int(max(1000, np.random.normal(40000, 20000)))
            pkt_count_down = int(max(5, np.random.normal(40, 10)))
            iat_mean = max(0.002, np.random.normal(0.08, 0.04))
            burst = int(np.random.poisson(1))

        bytes_up = int(max(0, np.random.normal(2000, 1000)))
        pkt_count_up = int(max(0, np.random.normal(6, 3)))
        avg_pkt_down = bytes_down / max(1, pkt_count_down)
        avg_pkt_up = bytes_up / max(1, pkt_count_up) if pkt_count_up>0 else 0
        bitrate_down = bytes_down / 5.0

        rows.append({
            'wstart': i*2.5,
            'bytes_down': bytes_down,
            'pkt_count_down': pkt_count_down,
            'avg_pkt_size_down': avg_pkt_down,
            'std_pkt_size_down': 0.0,
            'bytes_up': bytes_up,
            'pkt_count_up': pkt_count_up,
            'avg_pkt_size_up': avg_pkt_up,
            'std_pkt_size_up': 0.0,
            'bitrate_down': bitrate_down,
            'iat_mean_down': iat_mean,
            'iat_std_down': 0.0,
            'burst_count_down': burst,
            'ratio_down_up': bytes_down / (bytes_up + 1),
            'label': label
        })

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print("Saved:", out_csv)

if __name__ == '__main__':
    generate_synthetic_windows()
