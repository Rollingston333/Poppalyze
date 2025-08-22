#!/usr/bin/env python3
"""
Update cache timestamp to current time
"""

import json
import time
from datetime import datetime
from cache_manager import cache_manager

def update_cache_timestamp():
    """Update the cache timestamp to current time"""
    print("🕐 Updating cache timestamp...")
    
    # Load current cache
    cache_data = cache_manager.load_cache()
    
    if not cache_data or 'stocks' not in cache_data:
        print("❌ No cache data found")
        return
    
    # Update timestamp
    current_time = time.time()
    current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cache_data['last_update'] = current_time
    cache_data['last_update_str'] = current_time_str
    
    # Save updated cache
    success = cache_manager.save_cache(cache_data)
    
    if success:
        print(f"✅ Cache timestamp updated to: {current_time_str}")
        
        # Verify the update
        status = cache_manager.get_cache_status()
        print(f"📊 Cache status: {status['status']} ({status['age_minutes']:.1f} minutes old)")
    else:
        print("❌ Failed to update cache timestamp")

if __name__ == "__main__":
    update_cache_timestamp() 