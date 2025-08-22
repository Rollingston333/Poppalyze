#!/usr/bin/env python3
"""
Stock Scanner Worker for Render
Handles background stock scanning independently from the web app
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main worker function for background stock scanning"""
    
    try:
        logger.info("🚀 Starting Render worker for stock scanning")
        
        # Import scanner after path setup
        from app_streamlined import StockScanner
        
        # Initialize scanner
        scanner = StockScanner()
        
        # Get scan interval from environment (default 5 minutes)
        interval = int(os.environ.get('SCAN_INTERVAL', 300))
        logger.info(f"📊 Scan interval set to {interval} seconds")
        
        while True:
            try:
                logger.info("🔍 Starting stock scan...")
                scanner.scan_stocks()
                logger.info("✅ Scan completed successfully")
                
                logger.info(f"⏱ Sleeping for {interval} seconds before next scan")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Worker stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in worker: {e}")
                logger.info("⏳ Waiting 60 seconds before retry...")
                time.sleep(60)
                
    except Exception as e:
        logger.error(f"❌ Failed to start worker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 