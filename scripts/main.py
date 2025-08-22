#!/usr/bin/env python3
"""
Main entry point for Poppalyze Web Service
"""

import os
import sys
import logging
from app_web import app, initialize_app

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize and start the web server"""
    
    try:
        logger.info("🚀 Initializing Poppalyze Web Service...")
        
        # Initialize the app
        initialize_app()
        logger.info("✅ Web app initialization complete")
        
        # Get port from environment (Render sets PORT)
        port = int(os.environ.get('PORT', 5001))
        
        logger.info(f"🚀 Starting Poppalyze Web Service on port {port}")
        logger.info(f"🌐 App will be available at: http://localhost:{port}")
        logger.info("🛑 Press Ctrl+C to stop")
        
        # Run the app with production settings
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start web service: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 