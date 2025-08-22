# scripts/pcap_to_csv.py
# Lightweight helper to call pyshark conversion script from scripts folder
import os, sys, subprocess
if len(sys.argv) < 3:
    print("Usage: python scripts/pcap_to_csv.py input.pcap output.csv")
    sys.exit(1)
pcap = sys.argv[1]; out = sys.argv[2]
# call the notebook script (assumes pyshark installed)
subprocess.check_call(['python', os.path.join('..','notebooks','pcap_to_csv.py'), pcap, out])
