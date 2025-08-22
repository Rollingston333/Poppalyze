#!/usr/bin/env python3
"""
Simple Cache Manager for Poppalyze
Handles loading and saving of stock cache data
"""

import json
import os
import time
import logging
from config import Config
from utils import safe_json_dump, safe_json_load, validate_cache_data, ensure_directory

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, cache_file=None):
        if cache_file is None:
            # Use centralized configuration
            Config.ensure_directories()
            self.cache_file = Config.CACHE_FILE
            print(f"📁 Cache file path: {self.cache_file}")
        else:
            self.cache_file = os.path.abspath(cache_file) if not os.path.isabs(cache_file) else cache_file
    
    def save_cache_with_path(self, stock_data, cache_path=None):
        """Save cache data to specific path with success message"""
        if cache_path is None:
            cache_path = self.cache_file
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            with open(cache_path, "w") as f:
                json.dump(stock_data, f, indent=2)
            print(f"✅ Saved {len(stock_data.get('stocks', {}))} stocks to cache at {cache_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving cache to {cache_path}: {e}")
            return False
    
    def save_to_cache(self, data):
        """Save data to cache with directory creation"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, "w") as f:
            json.dump(data, f)
        print(f"✅ Cache saved to {self.cache_file}")
    
    def load_cache(self):
        """Load cache data from file with validation"""
        try:
            if os.path.exists(self.cache_file):
                data = safe_json_load(self.cache_file)
                if data and validate_cache_data(data):
                    logger.info(f"✅ Cache loaded with {len(data.get('stocks', {}))} stocks")
                    return data
                else:
                    logger.warning("❌ Invalid cache data structure")
        except Exception as e:
            logger.error(f"❌ Error loading cache: {e}")
        return None
    
    def save_cache(self, cache_data):
        """Save cache data to file with confirmation"""
        try:
            # Ensure cache directory exists before writing
            ensure_directory(os.path.dirname(self.cache_file))
            
            # Validate data before saving
            if not validate_cache_data(cache_data):
                logger.error("❌ Invalid cache data structure")
                return False
            
            # Save using safe utility function
            if safe_json_dump(cache_data, self.cache_file, indent=2):
                # Verify the write was successful
                if self.verify_cache_write(cache_data):
                    logger.info(f"✅ Cache saved successfully to {self.cache_file}")
                    print(f"✅ Cache saved successfully to {self.cache_file}")
                    return True
                else:
                    logger.error("❌ Cache write verification failed")
                    return False
            else:
                logger.error("❌ Failed to save cache data")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error saving cache: {e}")
            print(f"❌ Error saving cache: {e}")
            return False
    
    def verify_cache_write(self, expected_data):
        """Verify that cache was written correctly"""
        try:
            if not os.path.exists(self.cache_file):
                return False
                
            with open(self.cache_file, 'r') as f:
                written_data = json.load(f)
            
            # Check if we have the expected structure
            if not isinstance(written_data, dict):
                return False
                
            if 'stocks' not in written_data:
                return False
                
            # Check if we have actual stock data
            stocks = written_data.get('stocks', {})
            if not stocks or len(stocks) == 0:
                return False
                
            print(f"✅ Cache verification: {len(stocks)} stocks written")
            return True
            
        except Exception as e:
            print(f"❌ Cache verification failed: {e}")
            return False
    
    def clear_cache(self):
        """Clear the cache file"""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                print(f"✅ Cache cleared: {self.cache_file}")
                return True
            else:
                print(f"⚠️ Cache file does not exist: {self.cache_file}")
                return False
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")
            return False
    
    def get_cache_status(self):
        """Get cache status information"""
        cache_data = self.load_cache()
        
        if not cache_data or not cache_data.get('stocks'):
            return {
                'status': 'No data',
                'stock_count': 0,
                'last_update': 0,
                'age_minutes': 0,
                'scan_type': 'none'
            }
        
        last_update = cache_data.get('last_update', 0)
        age_seconds = time.time() - last_update
        age_minutes = age_seconds / 60
        
        return {
            'status': 'Fresh' if age_minutes < 10 else 'Stale' if age_minutes < 60 else 'Very stale',
            'stock_count': len(cache_data.get('stocks', {})),
            'last_update': last_update,
            'age_minutes': age_minutes,
            'scan_type': cache_data.get('scan_type', 'unknown')
        }

# Global cache manager instance
cache_manager = CacheManager() 