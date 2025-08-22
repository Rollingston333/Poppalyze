# Add this to your app.py for Redis caching

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
