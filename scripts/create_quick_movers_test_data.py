#!/usr/bin/env python3
"""
Create test data with pct_change field to make Quick Movers section appear
"""

import json
import time
from datetime import datetime
from cache_manager import cache_manager

def create_quick_movers_test_data():
    """Create test data with pct_change field to trigger Quick Movers section"""
    print("⚡ Creating test data with Quick Movers...")
    
    # Test data with pct_change field to trigger Quick Movers
    test_data = {
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
                'relative_volume': 3.2,  # High relative volume
                'float': 50000000,
                'pe_ratio': None,
                'data_fetch_time': datetime.now().isoformat()
            },
            'COUR': {
                'symbol': 'COUR',
                'price': 12.37,
                'gap_pct': 36.23,
                'pct_change': 8.7,  # This will trigger Quick Movers
                'volume': 3000000,
                'market_cap': 2000000000,
                'sector': 'Technology',
                'category': 'Mid Cap',
                'relative_volume': 2.8,  # High relative volume
                'float': 80000000,
                'pe_ratio': 45.2,
                'data_fetch_time': datetime.now().isoformat()
            },
            'SCHL': {
                'symbol': 'SCHL',
                'price': 26.70,
                'gap_pct': 23.90,
                'pct_change': 12.3,  # This will trigger Quick Movers
                'volume': 2000000,
                'market_cap': 1500000000,
                'sector': 'Consumer Cyclical',
                'category': 'Mid Cap',
                'relative_volume': 2.1,  # High relative volume
                'float': 60000000,
                'pe_ratio': 25.8,
                'data_fetch_time': datetime.now().isoformat()
            },
            'ABVE': {
                'symbol': 'ABVE',
                'price': 1.94,
                'gap_pct': 11.49,
                'pct_change': 6.2,  # This will trigger Quick Movers
                'volume': 8000000,
                'market_cap': 300000000,
                'sector': 'Healthcare',
                'category': 'Small Cap',
                'relative_volume': 4.5,  # Very high relative volume
                'float': 20000000,
                'pe_ratio': None,
                'data_fetch_time': datetime.now().isoformat()
            },
            'GNTX': {
                'symbol': 'GNTX',
                'price': 27.42,
                'gap_pct': 16.19,
                'pct_change': 9.8,  # This will trigger Quick Movers
                'volume': 1500000,
                'market_cap': 800000000,
                'sector': 'Technology',
                'category': 'Mid Cap',
                'relative_volume': 2.3,  # High relative volume
                'float': 40000000,
                'pe_ratio': 35.1,
                'data_fetch_time': datetime.now().isoformat()
            },
            'AAPL': {
                'symbol': 'AAPL',
                'price': 213.88,
                'gap_pct': 0.06,
                'pct_change': 0.5,  # Too low for Quick Movers
                'volume': 1000000,
                'market_cap': 3000000000000,
                'sector': 'Technology',
                'category': 'Mega Cap Tech',
                'relative_volume': 1.2,  # Too low for Quick Movers
                'float': 15000000000,
                'pe_ratio': 25.5,
                'data_fetch_time': datetime.now().isoformat()
            },
            'MSFT': {
                'symbol': 'MSFT',
                'price': 513.71,
                'gap_pct': 0.55,
                'pct_change': 0.8,  # Too low for Quick Movers
                'volume': 2000000,
                'market_cap': 4000000000000,
                'sector': 'Technology',
                'category': 'Mega Cap Tech',
                'relative_volume': 1.8,  # High enough but pct_change too low
                'float': 8000000000,
                'pe_ratio': 30.2,
                'data_fetch_time': datetime.now().isoformat()
            }
        },
        'last_update': time.time(),
        'last_update_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'successful_count': 7,
        'total_count': 7,
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
        print("📊 Quick Movers should now appear with 5 stocks:")
        print("   - MCVT: 15.5% change, 3.2x volume")
        print("   - COUR: 8.7% change, 2.8x volume") 
        print("   - SCHL: 12.3% change, 2.1x volume")
        print("   - ABVE: 6.2% change, 4.5x volume")
        print("   - GNTX: 9.8% change, 2.3x volume")
        
        # Verify the cache
        loaded_data = cache_manager.load_cache()
        if loaded_data and 'stocks' in loaded_data:
            print(f"📊 Cache verified: {len(loaded_data['stocks'])} stocks loaded")
        
        # Check cache status
        status = cache_manager.get_cache_status()
        print(f"📈 Cache status: {status['status']} ({status['age_minutes']:.1f} minutes old)")
        
        print("\n🌐 Now check the web interface at http://localhost:5001")
        print("   Look for the '⚡ Quick Movers' section!")
    else:
        print("❌ Failed to create test cache")

if __name__ == "__main__":
    create_quick_movers_test_data() 