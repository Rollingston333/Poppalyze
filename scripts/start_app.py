#!/usr/bin/env python3
"""
Simple startup script for the Gap Screener Dashboard
This script demonstrates the new automatic background scanner functionality.
"""

import subprocess
import sys
import time

def main():
    print("🚀 Starting Gap Screener Dashboard with Auto Background Scanner")
    print("=" * 60)
    
    try:
        # Start the Flask app (which will automatically start the background scanner)
        print("📱 Starting Flask app...")
        process = subprocess.Popen([sys.executable, 'app.py'])
        
        # Wait a moment for startup
        time.sleep(3)
        
        print("\n✅ Gap Screener Dashboard is running!")
        print("🌐 Web Interface: http://localhost:5001")
        print("📊 Health Check: http://localhost:5001/health")
        print("🔍 Scanner Status: http://localhost:5001/api/scanner/status")
        print("\n🎯 Features:")
        print("   • Automatic background scanner startup")
        print("   • Real-time stock data collection")
        print("   • Web-based filtering and analysis")
        print("   • Manual scanner control via API")
        print("\n🛑 Press Ctrl+C to stop")
        
        # Keep the script running
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if process:
            process.terminate()
        print("✅ Cleanup complete")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 