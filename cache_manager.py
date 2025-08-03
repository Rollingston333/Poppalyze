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
    def __init__(self, cache_file="stock_cache.json"):
        self.cache_file = cache_file
    
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
        """Save cache data to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            logger.info("✅ Cache saved successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving cache: {e}")
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