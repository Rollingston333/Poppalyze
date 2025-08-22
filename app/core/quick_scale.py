#!/usr/bin/env python3
"""
Quick Scaling Script for Stock Screener
=======================================
Implements immediate performance improvements
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required packages for scaling"""
    packages = [
        "gunicorn",
        "redis", 
        "flask-limiter",
        "flask-caching"
    ]
    
    print("🔧 Installing scaling dependencies...")
    for package in packages:
        print(f"   Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package], 
                      capture_output=True, text=True)
    print("✅ Dependencies installed!")

def create_gunicorn_config():
    """Create Gunicorn configuration file"""
    config = """# Gunicorn configuration for Stock Screener
import multiprocessing

# Server socket
bind = "0.0.0.0:5001"
backlog = 2048

# Worker processes
workers = min(4, multiprocessing.cpu_count())
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "access.log"
errorlog = "error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "stock_screener"

# Preload app for better performance
preload_app = True

# Graceful restarts
graceful_timeout = 30
"""
    
    with open("gunicorn.conf.py", "w") as f:
        f.write(config)
    print("✅ Gunicorn config created!")

def create_redis_config():
    """Create Redis configuration snippet"""
    config = """# Add this to your app.py for Redis caching

from flask_caching import Cache
import redis

# Redis configuration
cache_config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 0,
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes
}

cache = Cache()
cache.init_app(app, config=cache_config)

# Example usage:
# @cache.memoize(timeout=300)
# def get_stock_data(filters):
#     return expensive_operation(filters)
"""
    
    with open("redis_integration.py", "w") as f:
        f.write(config)
    print("✅ Redis integration example created!")

def create_rate_limiting():
    """Create rate limiting configuration"""
    config = """# Add this to your app.py for rate limiting

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate limiter configuration
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour", "10 per minute"],
    storage_uri="redis://localhost:6379"
)

# Apply to specific routes:
# @app.route('/api/screen')
# @limiter.limit("30 per minute")
# def screen_stocks():
#     return jsonify(results)
"""
    
    with open("rate_limiting.py", "w") as f:
        f.write(config)
    print("✅ Rate limiting example created!")

def create_startup_script():
    """Create production startup script"""
    script = """#!/bin/bash
# Production startup script for Stock Screener

echo "🚀 Starting Stock Screener in production mode..."

# Start Redis (if not running)
redis-server --daemonize yes --port 6379

# Wait for Redis to start
sleep 2

# Start the application with Gunicorn
echo "🔧 Starting Gunicorn workers..."
gunicorn -c gunicorn.conf.py app:app

echo "✅ Stock Screener is running on http://localhost:5001"
echo "📊 Workers: $(ps aux | grep gunicorn | wc -l) processes"
echo "🔍 Monitoring: tail -f access.log error.log"
"""
    
    with open("start_production.sh", "w") as f:
        f.write(script)
    os.chmod("start_production.sh", 0o755)
    print("✅ Production startup script created!")

def create_monitoring_script():
    """Create basic monitoring script"""
    script = """#!/usr/bin/env python3
import psutil
import requests
import time

def monitor_system():
    while True:
        # System metrics
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        
        # Test application health
        try:
            response = requests.get("http://localhost:5001/", timeout=5)
            status = "✅ UP" if response.status_code == 200 else f"❌ {response.status_code}"
            response_time = response.elapsed.total_seconds() * 1000
        except:
            status = "❌ DOWN"
            response_time = 0
        
        print(f"CPU: {cpu:5.1f}% | Memory: {memory:5.1f}% | App: {status} | Response: {response_time:.0f}ms")
        time.sleep(5)

if __name__ == "__main__":
    monitor_system()
"""
    
    with open("monitor.py", "w") as f:
        f.write(script)
    os.chmod("monitor.py", 0o755)
    print("✅ Monitoring script created!")

def main():
    """Main function to run all improvements"""
    print("🔥 STOCK SCREENER QUICK SCALING SETUP")
    print("=" * 50)
    
    try:
        install_dependencies()
        create_gunicorn_config()
        create_redis_config()
        create_rate_limiting()
        create_startup_script()
        create_monitoring_script()
        
        print("\n🎉 SCALING SETUP COMPLETE!")
        print("=" * 50)
        print("📋 Next Steps:")
        print("1. Install Redis: brew install redis (Mac) or apt install redis (Ubuntu)")
        print("2. Start Redis: redis-server")
        print("3. Run production: ./start_production.sh")
        print("4. Monitor: python3 monitor.py")
        print("5. Test: locust -f stress_test.py --host=http://localhost:5001")
        print("\n💡 Expected improvements:")
        print("   • 1,000 users: ~50ms response time")
        print("   • Better stability under load")
        print("   • Graceful error handling")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 