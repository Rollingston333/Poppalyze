#!/usr/bin/env python3
"""
Simplified Startup Script for Poppalyze
Clean, simple startup with proper error handling
"""

import os
import sys
import signal
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def cleanup_processes():
    """Clean up any existing processes"""
    try:
        # Kill any existing Python processes on port 5001
        result = subprocess.run(['lsof', '-ti:5001'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid])
                    logger.info(f"Killed process {pid}")
    except Exception as e:
        logger.warning(f"Cleanup warning: {e}")

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import flask
        import yfinance
        import dotenv
        logger.info("✅ All dependencies available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.info("Install with: pip install flask yfinance python-dotenv")
        return False

def create_initial_cache():
    """Create initial cache if it doesn't exist"""
    cache_file = "stock_cache.json"
    if not os.path.exists(cache_file):
        logger.info("Creating initial cache...")
        try:
            # Import and run a quick scan
            from app_simplified import scanner
            scanner.scan_stocks()
            logger.info("✅ Initial cache created")
        except Exception as e:
            logger.warning(f"Could not create initial cache: {e}")

def main():
    """Main startup function"""
    logger.info("🚀 Starting Poppalyze - Simplified Version")
    logger.info("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Cleanup existing processes
    cleanup_processes()
    
    # Create initial cache
    create_initial_cache()
    
    # Start the app
    logger.info("🌐 Starting Flask app...")
    logger.info("📊 App will be available at: http://localhost:5001")
    logger.info("🔄 Background scanner will run every 5 minutes")
    logger.info("🛑 Press Ctrl+C to stop")
    
    try:
        # Import and run the app
        from app_simplified import app, initialize_app
        
        # Initialize the app
        initialize_app()
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5001, debug=False)
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown signal received...")
    except Exception as e:
        logger.error(f"❌ Error starting app: {e}")
        sys.exit(1)
    finally:
        logger.info("✅ Cleanup complete")

if __name__ == "__main__":
    main() 