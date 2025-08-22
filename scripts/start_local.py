#!/usr/bin/env python3
"""
Local Development Startup Script for Poppalyze
Quick start for local development and testing
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import yfinance
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def create_initial_cache():
    """Create initial cache if it doesn't exist"""
    if not os.path.exists("stock_cache.json"):
        print("📁 Creating initial cache...")
        try:
            # Import and run a quick scan
            from app_production import scan_stocks
            cache_data = scan_stocks()
            if cache_data:
                print("✅ Initial cache created successfully")
            else:
                print("⚠️ Could not create initial cache")
        except Exception as e:
            print(f"⚠️ Error creating initial cache: {e}")

def main():
    """Main startup function"""
    print("🚀 Poppalyze - Local Development Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create initial cache
    create_initial_cache()
    
    # Start the app
    print("🌐 Starting Poppalyze...")
    print("📊 App will be available at: http://localhost:5001")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Import and run the app
        from app_production import app, initialize_app
        
        # Initialize the app
        initialize_app()
        
        # Run the development server
        app.run(debug=True, host='0.0.0.0', port=5001)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        print("✅ Shutdown complete")
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 