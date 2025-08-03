#!/usr/bin/env python3
"""
Simple Cache Manager for Poppalyze
Handles loading and saving of stock cache data
"""

import json
import os
import time
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, cache_file=None):
        if cache_file is None:
            # Use absolute path to avoid confusion between Render and local
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            cache_dir = os.path.join(BASE_DIR, "data")
            os.makedirs(cache_dir, exist_ok=True)  # Create cache directory if it doesn't exist
            self.cache_file = os.path.abspath(os.path.join(cache_dir, "stock_cache.json"))
            print(f"📁 Cache file path: {self.cache_file}")
        else:
            self.cache_file = os.path.abspath(cache_file) if not os.path.isabs(cache_file) else cache_file
    
    def load_cache(self):
        """Load cache data from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                logger.info(f"✅ Cache loaded with {len(data.get('stocks', {}))} stocks")
                return data
        except Exception as e:
            logger.error(f"❌ Error loading cache: {e}")
        return None
    
    def save_cache(self, cache_data):
        """Save cache data to file with confirmation"""
        try:
            # Ensure cache directory exists before writing
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = self.cache_file + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            # Atomic rename to ensure file is complete
            os.replace(temp_file, self.cache_file)
            
            # Verify the write was successful
            if self.verify_cache_write(cache_data):
                logger.info(f"✅ Cache saved successfully to {self.cache_file}")
                print(f"✅ Cache saved successfully to {self.cache_file}")
                return True
            else:
                logger.error("❌ Cache write verification failed")
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