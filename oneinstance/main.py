import psutil
import time
import requests
import argparse


def monitor_cpu(interval=1, duration=60, action=""):
    counter = 0
    end_time = time.time() + duration
    last_time = time.time()
    while time.time() < end_time:
        cpu_usage = psutil.cpu_percent(interval=interval)
        print(f"CPU Usage: {cpu_usage}%", end="\r")
        if cpu_usage < 50 and last_time + 2 < time.time():
            requests.get("http://localhost:5000/" + action)
            counter += 1
            last_time = time.time()
        time.sleep(interval)
    report(counter, duration)

def report(num_invocations, duration):
    print(f"Elapsed time: {duration} seconds")
    print(f"# invocations: {num_invocations}")
    print(f"Invocations/sec: {num_invocations/float(duration)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--program', type=str, help='The program to execute', required=True)
    parser.add_argument('--duration', type=int, help='The duration of the test', default=600)
    args = parser.parse_args()
    action = args.program
    assert action in ["compilation", "encoding"]

    monitor_cpu(interval=0.2, duration=args.duration, action=action)
