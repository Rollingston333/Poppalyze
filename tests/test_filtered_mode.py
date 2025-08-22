#!/usr/bin/env python3
"""
Test the filtered mode behavior for Quick Movers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, get_quick_movers, filter_cached_stocks
import json

def test_filtered_mode():
    """Test Quick Movers in filtered mode"""
    
    print("🔍 Testing Filtered Mode Behavior")
    print("=" * 50)
    
    try:
        # Load cache data
        with open('stock_cache.json', 'r') as f:
            cache_data = json.load(f)
        
        stocks = cache_data.get('stocks', {})
        print(f"Total stocks in cache: {len(stocks)}")
        
        # Test 1: Normal filters (should show Quick Movers)
        print("\n📊 Test 1: Normal filters (max_price=2000)")
        filtered_stocks = filter_cached_stocks(
            stocks,
            min_price=1.0,
            max_price=2000.0,
            min_gap_pct=0.0,
            min_rel_vol=0.0
        )
        print(f"Filtered stocks: {len(filtered_stocks)}")
        
        if filtered_stocks:
            quick_movers = get_quick_movers(filtered_stocks)
            print(f"Quick Movers: {len(quick_movers)}")
            for qm in quick_movers[:3]:
                print(f"  {qm['symbol']}: ${qm['price']:.2f}, {qm['pct_change']:.2f}%")
        else:
            print("No filtered stocks")
        
        # Test 2: Restrictive filters (should hide Quick Movers)
        print("\n📊 Test 2: Restrictive filters (max_price=20)")
        filtered_stocks_restrictive = filter_cached_stocks(
            stocks,
            min_price=1.0,
            max_price=20.0,  # Very restrictive
            min_gap_pct=0.0,
            min_rel_vol=0.0
        )
        print(f"Filtered stocks: {len(filtered_stocks_restrictive)}")
        
        if filtered_stocks_restrictive:
            quick_movers = get_quick_movers(filtered_stocks_restrictive)
            print(f"Quick Movers: {len(quick_movers)}")
        else:
            print("No filtered stocks - Quick Movers should be empty")
            quick_movers = []
            print(f"Quick Movers: {len(quick_movers)}")
        
        # Test 3: Flask route with restrictive filters
        print("\n📊 Test 3: Flask route with restrictive filters")
        with app.test_client() as client:
            response = client.get('/?quick_movers_independent=false&max_price=20')
            content = response.get_data(as_text=True)
            
            has_quick_movers = '⚡ Quick Movers' in content
            print(f"Quick Movers in response: {has_quick_movers}")
            
            if has_quick_movers:
                print("❌ Quick Movers should NOT appear with restrictive filters")
            else:
                print("✅ Quick Movers correctly hidden with restrictive filters")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_filtered_mode() 