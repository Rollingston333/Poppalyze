#!/usr/bin/env python3
"""
Quick Cache Refresh Script
=========================
Manually refresh cache with sample data to test template components
"""

import json
import time
from datetime import datetime
from cache_manager import cache_manager

def create_sample_data():
    """Create sample stock data for testing"""
    sample_stocks = {
        'AAPL': {
            'symbol': 'AAPL',
            'price': 185.50,
            'pct_change': 2.5,
            'gap_pct': 1.8,
            'volume': 50000000,
            'rel_vol': 1.2,
            'float': '15.7B',
            'market_cap': '2.9T',
            'pe': 28.5,
            'category': 'Technology',
            'has_news': True,
            'source': 'test',
            'timestamp': time.time(),
            'data_fetch_time': datetime.now().isoformat()
        },
        'TSLA': {
            'symbol': 'TSLA',
            'price': 245.75,
            'pct_change': 5.2,
            'gap_pct': 4.1,
            'volume': 75000000,
            'rel_vol': 2.1,
            'float': '3.2B',
            'market_cap': '780B',
            'pe': 65.2,
            'category': 'Technology',
            'has_news': True,
            'source': 'test',
            'timestamp': time.time(),
            'data_fetch_time': datetime.now().isoformat()
        },
        'NVDA': {
            'symbol': 'NVDA',
            'price': 425.30,
            'pct_change': 8.7,
            'gap_pct': 6.9,
            'volume': 45000000,
            'rel_vol': 3.5,
            'float': '2.5B',
            'market_cap': '1.1T',
            'pe': 71.8,
            'category': 'Technology',
            'has_news': True,
            'source': 'test',
            'timestamp': time.time(),
            'data_fetch_time': datetime.now().isoformat()
        },
        'META': {
            'symbol': 'META',
            'price': 310.45,
            'pct_change': 3.2,
            'gap_pct': 2.8,
            'volume': 25000000,
            'rel_vol': 1.8,
            'float': '2.7B',
            'market_cap': '785B',
            'pe': 22.4,
            'category': 'Technology',
            'has_news': False,
            'source': 'test',
            'timestamp': time.time(),
            'data_fetch_time': datetime.now().isoformat()
        },
        'AMZN': {
            'symbol': 'AMZN',
            'price': 145.80,
            'pct_change': 4.1,
            'gap_pct': 3.5,
            'volume': 35000000,
            'rel_vol': 1.6,
            'float': '10.8B',
            'market_cap': '1.5T',
            'pe': 45.2,
            'category': 'Consumer Discretionary',
            'has_news': True,
            'source': 'test',
            'timestamp': time.time(),
            'data_fetch_time': datetime.now().isoformat()
        }
    }
    
    return sample_stocks

def refresh_cache():
    """Refresh cache with fresh sample data"""
    print("🔄 Refreshing cache with sample data...")
    
    stocks_data = create_sample_data()
    
    cache_data = {
        'stocks': stocks_data,
        'last_update': time.time(),
        'last_update_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'successful_count': len(stocks_data),
        'total_count': len(stocks_data),
        'scan_type': 'test_data',
        'scan_duration_seconds': 2.5,
        'market_session': {
            'current_time_et': datetime.now().strftime('%Y-%m-%d %H:%M:%S EDT'),
            'session': 'TEST',
            'market_open': '9:30 ET',
            'market_close': '16:00 ET',
            'is_trading_day': True
        },
        'scan_summary': {
            'started_at': datetime.now().strftime('%H:%M:%S'),
            'completed_at': datetime.now().strftime('%H:%M:%S'),
            'duration_seconds': 2.5,
            'stocks_per_second': len(stocks_data) / 2.5
        }
    }
    
    success = cache_manager.save_cache(cache_data)
    
    if success:
        print(f"✅ Cache refreshed successfully!")
        print(f"📊 Added {len(stocks_data)} test stocks")
        print(f"🎯 Quick gappers and positive gappers should now display")
        print(f"🌐 Restart your Flask app and check: http://localhost:5001")
    else:
        print(f"❌ Failed to refresh cache")

if __name__ == "__main__":
    refresh_cache() 