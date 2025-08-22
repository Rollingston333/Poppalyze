#!/usr/bin/env python3
"""
Smooth Startup Script for Gap Screener
Ensures cache exists and provides clean startup
"""

import os
import sys
import subprocess
import time
import json

def check_cache():
    """Check if cache exists and is valid"""
    cache_file = "stock_cache.json"
    
    if not os.path.exists(cache_file):
        print("📁 No cache file found")
        return False
    
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        if not data.get('stocks'):
            print("📁 Cache file exists but has no stock data")
            return False
        
        stock_count = len(data['stocks'])
        print(f"📁 Cache found with {stock_count} stocks")
        return True
        
    except Exception as e:
        print(f"❌ Error reading cache: {e}")
        return False

def create_cache():
    """Create initial cache if needed"""
    print("🔄 Creating initial cache...")
    
    try:
        # Run the cache creation script
        result = subprocess.run([sys.executable, 'create_mixed_price_cache.py'], 
                              capture_output=True, text=True, timeout=60)
        
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
        # Start the app in the background
        process = subprocess.Popen([sys.executable, 'app.py'])
        
        # Wait a moment for startup
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Flask app started successfully")
            print("🌐 Open your browser to: http://localhost:5001")
            return process
        else:
            print("❌ Flask app failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        return None

def main():
    """Main startup function"""
    print("🎯 Gap Screener - Smooth Startup")
    print("=" * 40)
    
    # Check if cache exists
    if not check_cache():
        print("\n📁 Creating initial cache...")
        if not create_cache():
            print("❌ Failed to create cache. Exiting.")
            sys.exit(1)
    
    # Start the app
    print("\n🚀 Starting application...")
    app_process = start_app()
    
    if app_process:
        print("\n✅ Startup complete!")
        print("📊 Your Gap Screener is ready at http://localhost:5001")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            # Keep the script running
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