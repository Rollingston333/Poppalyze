#!/usr/bin/env python3
"""
Test script to verify cache saving works
"""

import json
import os
from cache_manager import cache_manager

def test_cache_save():
    """Test cache saving functionality"""
    print("🧪 Testing cache save functionality...")
    print("=" * 50)
    
    # Test data
    test_data = {
        'stocks': {
            'AAPL': {
                'symbol': 'AAPL',
                'price': 213.88,
                'gap_pct': 0.06,
                'volume': 1000000,
                'market_cap': 3000000000000,
                'sector': 'Technology',
                'category': 'Mega Cap Tech'
            },
            'MSFT': {
                'symbol': 'MSFT',
                'price': 513.71,
                'gap_pct': 0.55,
                'volume': 2000000,
                'market_cap': 4000000000000,
                'sector': 'Technology',
                'category': 'Mega Cap Tech'
            }
        },
        'last_update': 1732608000,  # Current timestamp
        'last_update_str': '2025-07-27 01:00:00',
        'successful_count': 2,
        'total_count': 2,
        'scan_type': 'biggest_gappers',
        'market_session': {
            'session': 'CLOSED (Weekend)',
            'current_time_et': '2025-07-27 01:00:00',
            'market_open': '9:30 ET',
            'market_close': '16:00 ET',
            'is_trading_day': False
        }
    }
    
    # Check if cache file exists before
    print(f"📁 Cache file exists before: {os.path.exists('stock_cache.json')}")
    
    # Try to save cache
    print("💾 Attempting to save cache...")
    success = cache_manager.save_cache(test_data)
    
    print(f"✅ Save successful: {success}")
    
    # Check if cache file exists after
    print(f"📁 Cache file exists after: {os.path.exists('stock_cache.json')}")
    
    if os.path.exists('stock_cache.json'):
        print("📄 Cache file size:", os.path.getsize('stock_cache.json'), "bytes")
        
        # Try to read the cache
        print("📖 Attempting to read cache...")
        loaded_data = cache_manager.load_cache()
        
        if loaded_data and 'stocks' in loaded_data:
            print(f"✅ Cache loaded successfully with {len(loaded_data['stocks'])} stocks")
            for symbol in loaded_data['stocks']:
                stock = loaded_data['stocks'][symbol]
                print(f"  - {symbol}: ${stock['price']:.2f} ({stock['gap_pct']:+.2f}%)")
        else:
            print("❌ Failed to load cache data")
    else:
        print("❌ Cache file was not created")
    
    # Check cache status
    print("\n📊 Cache status:")
    status = cache_manager.get_cache_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_cache_save() 