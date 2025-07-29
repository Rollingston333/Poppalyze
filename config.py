"""
Production Configuration for Gap Screener
Centralized configuration management
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Cache settings
    CACHE_FILE = 'stock_cache.json'
    CACHE_FRESHNESS_MINUTES = 30
    CACHE_MAX_AGE_HOURS = 24
    
    # Scanner settings
    SCAN_INTERVAL_SECONDS = 600  # 10 minutes
    MAX_STOCKS = 50
    RATE_LIMIT_DELAY = 10  # seconds between API calls
    
    # Web interface settings
    DEFAULT_MIN_PRICE = 1.0
    DEFAULT_MAX_PRICE = 2000.0
    DEFAULT_MIN_GAP_PCT = -100.0
    DEFAULT_MIN_REL_VOL = 0.0
    
    # Quick Movers settings
    QUICK_MOVERS_MIN_GAP_PCT = 0.5
    QUICK_MOVERS_MIN_REL_VOL = 0.5
    QUICK_MOVERS_MIN_PRICE = 1.0
    QUICK_MOVERS_LIMIT = 5
    
    # Top Gappers settings
    TOP_GAPPERS_LIMIT = 5
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'production.log'
    
    # Health check
    HEALTH_CHECK_TIMEOUT = 10
    
    # Process management
    PROCESS_CLEANUP_TIMEOUT = 10
    STARTUP_TIMEOUT = 180

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