import sys
import os

def run_attack(ip, port, time, threads):
    print(f"[INFO] Running attack on {ip}:{port} for {time}s with {threads} threads...")
    os.system(f"./Moin {ip} {port} {time} {threads}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 runner.py <ip> <port> <time> [threads]")
        sys.exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]
    time = sys.argv[3]

    try:
        threads = int(sys.argv[4]) if len(sys.argv) > 4 else 1450
    except ValueError:
        print("[ERROR] Threads must be a number.")
        sys.exit(1)

    run_attack(ip, port, time, threads)

if name == "main":
    main()
