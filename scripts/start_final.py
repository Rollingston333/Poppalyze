#!/usr/bin/env python3
"""
Final Startup Script for Gap Screener
Ensures smooth startup with proper cache management
"""

import os
import sys
import subprocess
import time
import json

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
        # Run cache creation
        result = subprocess.run([sys.executable, 'create_mixed_price_cache.py'], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Cache created successfully")
            return True
        else:
            print(f"❌ Failed to create cache: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Cache creation timed out")
        return False
    except Exception as e:
        print(f"❌ Error creating cache: {e}")
        return False

def start_app():
    """Start the Flask app"""
    print("🚀 Starting Flask app...")
    
    try:
        # Start the app
        process = subprocess.Popen([sys.executable, 'app.py'])
        
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

def main():
    """Main startup function"""
    print("🎯 Gap Screener - Final Startup")
    print("=" * 40)
    
    # Ensure cache exists
    if not ensure_cache_exists():
        print("❌ Failed to ensure cache exists. Exiting.")
        sys.exit(1)
    
    # Start the app
    app_process = start_app()
    
    if app_process:
        print("\n✅ Startup complete!")
        print("📊 Your Gap Screener is ready at http://localhost:5001")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            app_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            app_process.terminate()
            app_process.wait()
            print("✅ Shutdown complete")
    else:
        print("❌ Failed to start application")
        sys.exit(1)

if __name__ == "__main__":
    main() 