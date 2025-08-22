#!/usr/bin/env python3
import psutil
import requests
import time

def monitor_system():
    while True:
        # System metrics
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        
        # Test application health
        try:
            response = requests.get("http://localhost:5001/", timeout=5)
            status = "✅ UP" if response.status_code == 200 else f"❌ {response.status_code}"
            response_time = response.elapsed.total_seconds() * 1000
        except:
            status = "❌ DOWN"
            response_time = 0
        
        print(f"CPU: {cpu:5.1f}% | Memory: {memory:5.1f}% | App: {status} | Response: {response_time:.0f}ms")
        time.sleep(5)

if __name__ == "__main__":
    monitor_system()
