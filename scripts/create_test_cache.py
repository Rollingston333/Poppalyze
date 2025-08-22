#!/usr/bin/env python3
"""
Create a test cache with sample stock data
"""

import json
import time
from datetime import datetime
from cache_manager import cache_manager

def create_test_cache():
    """Create a test cache with sample stock data"""
    print("🧪 Creating test cache with sample data...")
    
    # Test data with realistic stock information
    test_data = {
        'stocks': {
            'AAPL': {
                'symbol': 'AAPL',
                'price': 213.88,
                'gap_pct': 0.06,
                'volume': 1000000,
                'market_cap': 3000000000000,
                'sector': 'Technology',
                'category': 'Mega Cap Tech',
                'relative_volume': 1.2,
                'float': 15000000000,
                'pe_ratio': 25.5,
                'data_fetch_time': datetime.now().isoformat()
            },
            'MSFT': {
                'symbol': 'MSFT',
                'price': 513.71,
                'gap_pct': 0.55,
                'volume': 2000000,
                'market_cap': 4000000000000,
                'sector': 'Technology',
                'category': 'Mega Cap Tech',
                'relative_volume': 1.8,
                'float': 8000000000,
                'pe_ratio': 30.2,
                'data_fetch_time': datetime.now().isoformat()
            },
            'TSLA': {
                'symbol': 'TSLA',
                'price': 316.06,
                'gap_pct': 3.52,
                'volume': 5000000,
                'market_cap': 1000000000000,
                'sector': 'Automotive',
                'category': 'Large Cap',
                'relative_volume': 2.5,
                'float': 3000000000,
                'pe_ratio': 45.8,
                'data_fetch_time': datetime.now().isoformat()
            },
            'NVDA': {
                'symbol': 'NVDA',
                'price': 173.50,
                'gap_pct': -0.14,
                'volume': 3000000,
                'market_cap': 2000000000000,
                'sector': 'Technology',
                'category': 'Large Cap',
                'relative_volume': 1.5,
                'float': 2500000000,
                'pe_ratio': 35.1,
                'data_fetch_time': datetime.now().isoformat()
            },
            'GME': {
                'symbol': 'GME',
                'price': 23.33,
                'gap_pct': -0.85,
                'volume': 8000000,
                'market_cap': 7000000000,
                'sector': 'Consumer Cyclical',
                'category': 'Small Cap',
                'relative_volume': 3.2,
                'float': 300000000,
                'pe_ratio': None,
                'data_fetch_time': datetime.now().isoformat()
            }
        },
        'last_update': time.time(),
        'last_update_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'successful_count': 5,
        'total_count': 5,
        'scan_type': 'biggest_gappers',
        'market_session': {
            'session': 'CLOSED (Weekend)',
            'current_time_et': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'market_open': '9:30 ET',
            'market_close': '16:00 ET',
            'is_trading_day': False
        }
    }
    
    # Save the test cache
    success = cache_manager.save_cache(test_data)
    
    if success:
        print(f"✅ Test cache created with {len(test_data['stocks'])} stocks")
        
        # Verify the cache
        loaded_data = cache_manager.load_cache()
        if loaded_data and 'stocks' in loaded_data:
            print(f"📊 Cache verified: {len(loaded_data['stocks'])} stocks loaded")
            for symbol in loaded_data['stocks']:
                stock = loaded_data['stocks'][symbol]
                print(f"  - {symbol}: ${stock['price']:.2f} ({stock['gap_pct']:+.2f}%)")
        
        # Check cache status
        status = cache_manager.get_cache_status()
        print(f"📈 Cache status: {status['status']} ({status['age_minutes']:.1f} minutes old)")
    else:
        print("❌ Failed to create test cache")

if __name__ == "__main__":
    create_test_cache() 