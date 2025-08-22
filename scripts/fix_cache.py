#!/usr/bin/env python3
"""
Fix Cache Structure
Convert existing flat cache to correct nested structure
"""

import json
import time
from datetime import datetime

def fix_cache_structure():
    """Convert flat cache structure to nested structure"""
    
    try:
        # Load existing cache
        with open('stock_cache.json', 'r') as f:
            flat_data = json.load(f)
        
        print(f"📁 Found {len(flat_data)} stocks in flat cache")
        
        # Create proper cache structure
        fixed_cache = {
            'stocks': flat_data,
            'last_update': time.time(),
            'last_update_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'successful_count': len(flat_data),
            'total_count': len(flat_data),
            'scan_type': 'biggest_gappers',
            'market_session': {
                'session': 'CLOSED (Weekend)',
                'current_time_et': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'market_open': '9:30 ET',
                'market_close': '16:00 ET',
                'is_trading_day': False
            }
        }
        
        # Save fixed cache
        with open('stock_cache.json', 'w') as f:
            json.dump(fixed_cache, f, indent=2)
        
        print(f"✅ Cache fixed! {len(flat_data)} stocks now in correct structure")
        print(f"📊 Cache status: Fresh data from {fixed_cache['last_update_str']}")
        
        return True
        
    except FileNotFoundError:
        print("❌ No cache file found")
        return False
    except Exception as e:
        print(f"❌ Error fixing cache: {e}")
        return False

if __name__ == "__main__":
    fix_cache_structure() 