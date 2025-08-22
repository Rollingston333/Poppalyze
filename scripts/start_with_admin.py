#!/usr/bin/env python3
"""
Startup Script with Admin Dashboard
Runs both the main Gap Screener app and admin dashboard
"""

import os
import sys
import subprocess
import time
import signal
import threading
from datetime import datetime

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
        
        # Kill any existing admin dashboard processes
        subprocess.run(['pkill', '-f', 'python.*admin_dashboard.py'], 
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
            import json
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

def start_main_app():
    """Start the main Flask app"""
    print("🚀 Starting main application...")
    
    try:
        # Set environment variable to disable auto-scanner
        env = os.environ.copy()
        env['DISABLE_AUTO_SCANNER'] = '1'
        
        # Start the app
        process = subprocess.Popen([sys.executable, 'app.py'], env=env)
        
        # Wait for startup
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Main application started successfully")
            return process
        else:
            print("❌ Main application failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting main application: {e}")
        return None

def start_admin_dashboard():
    """Start the admin dashboard"""
    print("🔧 Starting admin dashboard...")
    
    try:
        # Start the admin dashboard
        process = subprocess.Popen([sys.executable, 'admin_dashboard.py'])
        
        # Wait for startup
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Admin dashboard started successfully")
            return process
        else:
            print("❌ Admin dashboard failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting admin dashboard: {e}")
        return None

def start_background_scanner():
    """Start background scanner"""
    print("🔍 Starting background scanner...")
    
    try:
        process = subprocess.Popen([sys.executable, 'background_scanner.py'])
        
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Background scanner started successfully")
            return process
        else:
            print("❌ Background scanner failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting background scanner: {e}")
        return None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down...")
    cleanup_processes()
    sys.exit(0)

def monitor_processes(main_app_process, admin_process, scanner_process):
    """Monitor processes and restart if needed"""
    while True:
        try:
            # Check main app
            if main_app_process and main_app_process.poll() is not None:
                print("⚠️  Main application has stopped - restarting...")
                main_app_process = start_main_app()
            
            # Check admin dashboard
            if admin_process and admin_process.poll() is not None:
                print("⚠️  Admin dashboard has stopped - restarting...")
                admin_process = start_admin_dashboard()
            
            # Check background scanner
            if scanner_process and scanner_process.poll() is not None:
                print("⚠️  Background scanner has stopped - restarting...")
                scanner_process = start_background_scanner()
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚠️  Error in process monitoring: {e}")
            time.sleep(30)

def main():
    """Main startup function"""
    print("🎯 Gap Screener with Admin Dashboard")
    print("=" * 50)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Clean up existing processes
        cleanup_processes()
        
        # Ensure cache exists
        if not ensure_cache_exists():
            print("❌ Failed to ensure cache exists. Exiting.")
            sys.exit(1)
        
        # Start main application
        main_app_process = start_main_app()
        if not main_app_process:
            print("❌ Failed to start main application")
            sys.exit(1)
        
        # Start admin dashboard
        admin_process = start_admin_dashboard()
        if not admin_process:
            print("❌ Failed to start admin dashboard")
            sys.exit(1)
        
        # Start background scanner
        scanner_process = start_background_scanner()
        if not scanner_process:
            print("⚠️  Failed to start background scanner")
        
        print("\n✅ All services started successfully!")
        print("📊 Main Application: http://localhost:5001")
        print("🔧 Admin Dashboard: http://localhost:5002/admin")
        print("🔑 Admin credentials: admin / admin123")
        print("🛑 Press Ctrl+C to stop all services")
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(
            target=monitor_processes, 
            args=(main_app_process, admin_process, scanner_process),
            daemon=True
        )
        monitor_thread.start()
        
        # Wait for main processes
        try:
            main_app_process.wait()
        except KeyboardInterrupt:
            pass
        
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        signal_handler(None, None)

if __name__ == "__main__":
    main() 