#!/usr/bin/env python3
"""
Debug script to test filtering and see why Quick Movers aren't showing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import filter_cached_stocks, get_quick_movers
import json

def test_filtering():
    """Test filtering to see what's happening"""
    
    print("🔍 Testing Filtering Debug")
    print("=" * 50)
    
    try:
        # Load cache data
        with open('stock_cache.json', 'r') as f:
            cache_data = json.load(f)
        
        stocks = cache_data.get('stocks', {})
        print(f"Total stocks in cache: {len(stocks)}")
        
        # Test with default filters (what the web app uses)
        print("\n📊 Testing with default filters:")
        print("Default filters: min_price=1.0, max_price=100.0, min_gap_pct=0.0, min_rel_vol=0.0")
        
        filtered_stocks = filter_cached_stocks(
            stocks,
            min_price=1.0,
            max_price=100.0,
            min_gap_pct=0.0,
            min_rel_vol=0.0
        )
        
        print(f"Filtered stocks: {len(filtered_stocks)}")
        
        # Show first few filtered stocks
        for i, stock in enumerate(filtered_stocks[:3]):
            print(f"  {i+1}. {stock['symbol']}: ${stock['price']:.2f}, {stock['gap_pct']:.2f}% gap, {stock['relative_volume']:.1f}x vol")
        
        # Test Quick Movers with filtered stocks
        print("\n📊 Testing Quick Movers with filtered stocks:")
        quick_movers = get_quick_movers(filtered_stocks)
        print(f"Quick Movers from filtered stocks: {len(quick_movers)}")
        
        for i, qm in enumerate(quick_movers[:3]):
            print(f"  {i+1}. {qm['symbol']}: {qm['pct_change']:.2f}%, {qm['rel_vol']:.1f}x vol")
        
        # Test with more restrictive filters
        print("\n📊 Testing with more restrictive filters:")
        print("Filters: min_price=1.0, max_price=1000.0, min_gap_pct=0.0, min_rel_vol=0.0")
        
        filtered_stocks_wide = filter_cached_stocks(
            stocks,
            min_price=1.0,
            max_price=1000.0,  # Wider price range
            min_gap_pct=0.0,
            min_rel_vol=0.0
        )
        
        print(f"Filtered stocks (wide): {len(filtered_stocks_wide)}")
        
        # Test Quick Movers with wide filtered stocks
        quick_movers_wide = get_quick_movers(filtered_stocks_wide)
        print(f"Quick Movers (wide filters): {len(quick_movers_wide)}")
        
        # Check if any stocks are being filtered out by price
        print("\n📊 Checking price filtering:")
        for symbol, stock_data in list(stocks.items())[:5]:
            price = stock_data.get('price', 0)
            in_range = 1.0 <= price <= 100.0
            print(f"  {symbol}: ${price:.2f} (1.0-100.0: {'✅' if in_range else '❌'})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_filtering() 