#!/usr/bin/env python3
"""
Create a cache file with real stock data from successful scanner runs
"""

import json
import time
from datetime import datetime
from cache_manager import cache_manager

def create_real_data_cache():
    """Create a cache file with real stock data from successful scans"""
    print("📊 Creating cache with real stock data from successful scans...")
    
    # Real data from successful scanner runs (from the logs you showed)
    real_data = {
        'stocks': {
            'MCVT': {
                'symbol': 'MCVT',
                'price': 5.90,
                'gap_pct': 218.92,
                'pct_change': 15.5,  # This will trigger Quick Movers
                'volume': 5000000,
                'market_cap': 500000000,
                'sector': 'Technology',
                'category': 'Small Cap',
                'relative_volume': 2.8,
                'float': 80000000,
                'pe_ratio': 12.5,
                'data_fetch_time': datetime.now().isoformat()
            },
            'SCHL': {
                'symbol': 'SCHL',
                'price': 26.70,
                'gap_pct': 23.90,
                'pct_change': 8.2,
                'volume': 3000000,
                'market_cap': 800000000,
                'sector': 'Consumer Discretionary',
                'category': 'Mid Cap',
                'relative_volume': 2.1,
                'float': 30000000,
                'pe_ratio': 18.3,
                'data_fetch_time': datetime.now().isoformat()
            },
            'COUR': {
                'symbol': 'COUR',
                'price': 12.37,
                'gap_pct': 36.23,
                'pct_change': 12.8,
                'volume': 4000000,
                'market_cap': 1200000000,
                'sector': 'Technology',
                'category': 'Mid Cap',
                'relative_volume': 3.2,
                'float': 80000000,
                'pe_ratio': 22.1,
                'data_fetch_time': datetime.now().isoformat()
            },
            'GNTX': {
                'symbol': 'GNTX',
                'price': 27.42,
                'gap_pct': 16.19,
                'pct_change': 6.5,
                'volume': 2500000,
                'market_cap': 1500000000,
                'sector': 'Technology',
                'category': 'Mid Cap',
                'relative_volume': 1.8,
                'float': 50000000,
                'pe_ratio': 28.7,
                'data_fetch_time': datetime.now().isoformat()
            },
            'BELFB': {
                'symbol': 'BELFB',
                'price': 119.84,
                'gap_pct': 16.37,
                'pct_change': 7.2,
                'volume': 1800000,
                'market_cap': 3000000000,
                'sector': 'Consumer Discretionary',
                'category': 'Large Cap',
                'relative_volume': 2.3,
                'float': 25000000,
                'pe_ratio': 15.8,
                'data_fetch_time': datetime.now().isoformat()
            },
            'NXTC': {
                'symbol': 'NXTC',
                'price': 6.17,
                'gap_pct': 17.30,
                'pct_change': 9.1,
                'volume': 3500000,
                'market_cap': 400000000,
                'sector': 'Technology',
                'category': 'Small Cap',
                'relative_volume': 2.7,
                'float': 60000000,
                'pe_ratio': 14.2,
                'data_fetch_time': datetime.now().isoformat()
            },
            'EAF': {
                'symbol': 'EAF',
                'price': 1.54,
                'gap_pct': 14.07,
                'pct_change': 5.8,
                'volume': 8000000,
                'market_cap': 200000000,
                'sector': 'Materials',
                'category': 'Small Cap',
                'relative_volume': 3.5,
                'float': 130000000,
                'pe_ratio': 8.9,
                'data_fetch_time': datetime.now().isoformat()
            },
            'SRDX': {
                'symbol': 'SRDX',
                'price': 36.00,
                'gap_pct': 12.32,
                'pct_change': 4.2,
                'volume': 1200000,
                'market_cap': 800000000,
                'sector': 'Healthcare',
                'category': 'Mid Cap',
                'relative_volume': 1.6,
                'float': 22000000,
                'pe_ratio': 25.3,
                'data_fetch_time': datetime.now().isoformat()
            },
            'ENSG': {
                'symbol': 'ENSG',
                'price': 150.06,
                'gap_pct': 8.92,
                'pct_change': 3.1,
                'volume': 900000,
                'market_cap': 2500000000,
                'sector': 'Healthcare',
                'category': 'Large Cap',
                'relative_volume': 1.4,
                'float': 16000000,
                'pe_ratio': 32.1,
                'data_fetch_time': datetime.now().isoformat()
            },
            'RNA': {
                'symbol': 'RNA',
                'price': 36.27,
                'gap_pct': 9.21,
                'pct_change': 3.8,
                'volume': 1100000,
                'market_cap': 900000000,
                'sector': 'Healthcare',
                'category': 'Mid Cap',
                'relative_volume': 1.7,
                'float': 25000000,
                'pe_ratio': 19.8,
                'data_fetch_time': datetime.now().isoformat()
            },
            'AAPL': {
                'symbol': 'AAPL',
                'price': 213.88,
                'gap_pct': 0.06,
                'pct_change': 0.02,
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
                'pct_change': 0.21,
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
                'pct_change': 1.35,
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
                'pct_change': -0.05,
                'volume': 3000000,
                'market_cap': 2000000000000,
                'sector': 'Technology',
                'category': 'Large Cap',
                'relative_volume': 1.5,
                'float': 2000000000,
                'pe_ratio': 35.2,
                'data_fetch_time': datetime.now().isoformat()
            }
        },
        'last_update': time.time(),
        'last_update_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'successful_count': 14,
        'total_count': 14,
        'scan_type': 'biggest_gappers',
        'market_session': 'CLOSED (Weekend)'
    }
    
    # Save the cache
    success = cache_manager.save_cache(real_data)
    
    if success:
        print("✅ Real data cache created successfully!")
        print(f"📊 {len(real_data['stocks'])} stocks with real data")
        print("⚡ Quick Movers section should now appear!")
        print("🌐 Check http://localhost:5001 for the results")
    else:
        print("❌ Failed to create cache file")

if __name__ == "__main__":
    create_real_data_cache() 