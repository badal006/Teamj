import os
import sys
import time
import subprocess

def run_attack(ip, port, duration, threads):
    # Example command to run your attack binary
    command = f"./Moin {ip} {port} {duration} {threads}"
    process = subprocess.Popen(command, shell=True)
    time.sleep(int(duration))
    process.terminate()
    sys.exit(0)

if name == "main":
    if len(sys.argv) < 5:
        print("Usage: runner.py <ip> <port> <duration> <threads>")
        sys.exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]
    duration = sys.argv[3]
    threads = sys.argv[4]

    run_attack(ip, port, duration, threads))