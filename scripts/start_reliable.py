#!/usr/bin/env python3
"""
Reliable Startup Script for Gap Screener
Ensures smooth startup without background scanner conflicts
"""

import os
import sys
import subprocess
import time
import json
import signal

def cleanup_processes():
    """Clean up any existing processes"""
    print("🧹 Cleaning up existing processes...")
    
    try:
        # Kill any existing app processes
        subprocess.run(['pkill', '-f', 'python.*app.py'], 
                      capture_output=True, text=True)
        
        # Kill any existing background scanner processes
        subprocess.run(['pkill', '-f', 'python.*background_scanner.py'], 
                      capture_output=True, text=True)
        
        # Remove PID files
        for pid_file in ['background_scanner.pid']:
            if os.path.exists(pid_file):
                os.remove(pid_file)
                print(f"🧹 Removed {pid_file}")
        
        time.sleep(2)  # Wait for processes to clean up
        print("✅ Cleanup complete")
        
    except Exception as e:
        print(f"⚠️  Warning during cleanup: {e}")

def ensure_cache_exists():
    """Ensure cache exists before starting app"""
    cache_file = "stock_cache.json"
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            if data.get('stocks') and len(data['stocks']) > 0:
                stock_count = len(data['stocks'])
                print(f"✅ Cache found with {stock_count} stocks")
                return True
        except Exception as e:
            print(f"⚠️  Cache file corrupted: {e}")
    
    print("📁 Creating fresh cache...")
    
    try:
        result = subprocess.run([sys.executable, 'create_mixed_price_cache.py'], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Cache created successfully")
            return True
        else:
            print(f"❌ Failed to create cache: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating cache: {e}")
        return False

def start_app_only():
    """Start the Flask app without background scanner"""
    print("🚀 Starting Flask app (without background scanner)...")
    
    try:
        # Set environment variable to disable auto-scanner
        env = os.environ.copy()
        env['DISABLE_AUTO_SCANNER'] = '1'
        
        # Start the app
        process = subprocess.Popen([sys.executable, 'app.py'], env=env)
        
        # Wait for startup
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Flask app started successfully")
            return process
        else:
            print("❌ Flask app failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        return None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down...")
    cleanup_processes()
    sys.exit(0)

def main():
    """Main startup function"""
    print("🎯 Gap Screener - Reliable Startup")
    print("=" * 40)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Clean up existing processes
    cleanup_processes()
    
    # Ensure cache exists
    if not ensure_cache_exists():
        print("❌ Failed to ensure cache exists. Exiting.")
        sys.exit(1)
    
    # Start the app without background scanner
    app_process = start_app_only()
    
    if app_process:
        print("\n✅ Reliable startup complete!")
        print("📊 Your Gap Screener is ready at http://localhost:5001")
        print("💡 To start background scanner manually, run: python3 background_scanner.py")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            app_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            app_process.terminate()
            app_process.wait()
            cleanup_processes()
            print("✅ Shutdown complete")
    else:
        print("❌ Failed to start application")
        sys.exit(1)

if __name__ == "__main__":
    main() 