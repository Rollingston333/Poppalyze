#!/usr/bin/env python3
"""
Cleanup script to stop all background scanner processes and remove PID files
"""

import os
import subprocess
import signal
import time

def cleanup_all_scanners():
    """Clean up all background scanner processes and PID files"""
    print("🧹 Cleaning up all background scanner processes...")
    
    # Kill all background scanner processes
    try:
        result = subprocess.run(['pkill', '-f', 'background_scanner.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Killed background scanner processes")
        else:
            print("ℹ️  No background scanner processes found")
    except Exception as e:
        print(f"⚠️  Error killing processes: {e}")
    
    # Remove PID file
    pid_file = "background_scanner.pid"
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)
            print(f"✅ Removed PID file: {pid_file}")
        except Exception as e:
            print(f"⚠️  Error removing PID file: {e}")
    else:
        print(f"ℹ️  No PID file found: {pid_file}")
    
    # Wait a moment for processes to fully terminate
    time.sleep(2)
    
    # Check if any processes are still running
    try:
        result = subprocess.run(['pgrep', '-f', 'background_scanner.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("⚠️  Some processes may still be running")
            print("   You may need to force kill them manually")
        else:
            print("✅ All background scanner processes stopped")
    except Exception as e:
        print(f"⚠️  Error checking remaining processes: {e}")

if __name__ == "__main__":
    cleanup_all_scanners() 