import json
import logging
import numpy as np
from functools import wraps
import time

logger = logging.getLogger(__name__)

def json_serializer(obj):
    """Custom JSON serializer for numpy types and other non-serializable objects"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif hasattr(obj, 'isoformat'):  # datetime objects
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def safe_json_dump(data, file_path, **kwargs):
    """Safely dump data to JSON file with error handling"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, default=json_serializer, **kwargs)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {e}")
        return False

def safe_json_load(file_path):
    """Safely load data from JSON file with error handling"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return None

def safe_operation(func, *args, **kwargs):
    """Wrapper for safe operations with logging"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}")
        print(f"❌ Error in {func.__name__}: {e}")
        return None

def retry_operation(func, max_retries=3, delay=1, *args, **kwargs):
    """Retry an operation with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay * (2 ** attempt))

def ensure_directory(path):
    """Ensure directory exists, create if it doesn't"""
    import os
    os.makedirs(path, exist_ok=True)
    return path

def validate_cache_data(data):
    """Validate cache data structure"""
    if not isinstance(data, dict):
        return False
    if 'stocks' not in data:
        return False
    # Accept both list and dict for stocks (list is newer format, dict is legacy)
    if not isinstance(data['stocks'], (list, dict)):
        return False
    return True 