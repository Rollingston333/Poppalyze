#!/usr/bin/env python3
"""
Main entry point for Poppalyze on Render
"""

import os
import sys
from app_streamlined import app, initialize_app, scanner

def main():
    """Initialize and start the production server"""
    
    # Initialize the app
    initialize_app()
    
    # Start background scanner
    scanner.start_background_scanner()
    
    # Get port from environment (Render sets PORT)
    port = int(os.environ.get('PORT', 5001))
    
    print(f"🚀 Starting Poppalyze on port {port}")
    print(f"🌐 App will be available at: http://localhost:{port}")
    print(f"📊 Background scanner is running")
    print(f"🛑 Press Ctrl+C to stop")
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main() 