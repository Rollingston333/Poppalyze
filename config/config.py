"""
Production Configuration for Gap Screener
Centralized configuration management
"""

import os
from datetime import timedelta

class Config:
    """Centralized configuration for the application"""
    
    # Base directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Cache configuration
    CACHE_FILE = os.path.join(BASE_DIR, "data", "stock_cache.json")
    CACHE_DIR = os.path.join(BASE_DIR, "data")
    
    # Scanner configuration
    SCAN_INTERVAL = int(os.environ.get('SCAN_INTERVAL', 60))  # 1 minute
    MAX_STOCKS = int(os.environ.get('MAX_STOCKS', 15))
    RATE_LIMIT_DELAY = float(os.environ.get('RATE_LIMIT_DELAY', 0.1))
    
    # Flask configuration
    PORT = int(os.environ.get('PORT', 5001))
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    # PID files
    SCANNER_PID_FILE = "background_scanner_fast.pid"
    
    # Database
    TRAFFIC_DB = "traffic_analytics.db"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        os.makedirs(cls.CACHE_DIR, exist_ok=True)
        print(f"📁 Cache directory: {cls.CACHE_DIR}")
    
    @classmethod
    def get_absolute_path(cls, relative_path):
        """Get absolute path from relative path"""
        return os.path.abspath(os.path.join(cls.BASE_DIR, relative_path))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # Faster scanning for development
    SCAN_INTERVAL_SECONDS = 300  # 5 minutes
    CACHE_FRESHNESS_MINUTES = 5

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # More conservative settings for production
    SCAN_INTERVAL_SECONDS = 900  # 15 minutes
    CACHE_FRESHNESS_MINUTES = 60
    RATE_LIMIT_DELAY = 15  # More conservative rate limiting

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    CACHE_FILE = 'test_cache.json'
    SCAN_INTERVAL_SECONDS = 60  # 1 minute for testing

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default']) 