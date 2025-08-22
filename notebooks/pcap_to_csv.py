# notebooks/pcap_to_csv.py
# Optional: convert pcap files to CSV (requires pyshark and tshark installed).
import pyshark
import csv
import sys

def pcap_to_csv(pcap_path, out_csv):
    cap = pyshark.FileCapture(pcap_path, keep_packets=False)
    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ts','length','src','dst'])
        for pkt in cap:
            try:
                ts = float(pkt.sniff_timestamp)
                length = int(pkt.length)
                src = pkt.ip.src if hasattr(pkt, 'ip') else ''
                dst = pkt.ip.dst if hasattr(pkt, 'ip') else ''
                writer.writerow([ts, length, src, dst])
            except Exception:
                continue
    cap.close()
    print('Saved to', out_csv)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python pcap_to_csv.py input.pcap output.csv')
    else:
        pcap_to_csv(sys.argv[1], sys.argv[2])
