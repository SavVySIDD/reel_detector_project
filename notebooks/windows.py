# notebooks/windows.py
# Convert a packet CSV (ts,length,src,dst) into sliding windows of features.

import pandas as pd
import numpy as np

def load_packet_csv(path):
    df = pd.read_csv(path)
    df = df.sort_values('ts').reset_index(drop=True)
    return df

def compute_sliding_windows(df, device_ip, window_size=5.0, step=2.5):
    if df.empty:
        return pd.DataFrame()
    start_ts, end_ts = df['ts'].iloc[0], df['ts'].iloc[-1]
    windows = []
    t = start_ts
    while t <= end_ts:
        wstart, wend = t, t + window_size
        wdf = df[(df['ts'] >= wstart) & (df['ts'] < wend)]
        if len(wdf) > 0:
            down = wdf[wdf['dst'] == device_ip]['length'].values
            up = wdf[wdf['src'] == device_ip]['length'].values

            def stats(arr):
                if len(arr) == 0:
                    return 0, 0, 0.0, 0.0
                return int(arr.sum()), int(len(arr)), float(arr.mean()), float(arr.std())

            bd, nd, md, sd = stats(down)
            bu, nu, mu, su = stats(up)

            down_ts = wdf[wdf['dst'] == device_ip]['ts'].values
            if len(down_ts) > 1:
                iat = np.diff(down_ts)
                iat_mean, iat_std = float(iat.mean()), float(iat.std())
            else:
                iat_mean, iat_std = 0.0, 0.0

            burst_count_down = int((down > 1000).sum()) if len(down) > 0 else 0
            features = {
                'wstart': wstart,
                'bytes_down': bd, 'pkt_count_down': nd, 'avg_pkt_size_down': md, 'std_pkt_size_down': sd,
                'bytes_up': bu, 'pkt_count_up': nu, 'avg_pkt_size_up': mu, 'std_pkt_size_up': su,
                'bitrate_down': bd / window_size,
                'iat_mean_down': iat_mean, 'iat_std_down': iat_std,
                'burst_count_down': burst_count_down,
                'ratio_down_up': bd / (bu + 1)
            }
            windows.append(features)
        t += step
    return pd.DataFrame(windows)
