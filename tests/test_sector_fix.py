#!/usr/bin/env python3
"""
Quick test to verify and fix sector/industry data for INKT and other stocks
"""

import json
import time
from background_scanner import fetch_stock_data

def test_and_update_sectors():
    """Test sector data fetching and update cache"""
    
    # Test a few stocks
    test_symbols = ['INKT', 'ABVE', 'VEON', 'NEGG']
    
    print("🧪 Testing Sector/Industry Data Fetching\n")
    
    # Load current cache
    try:
        with open('stock_cache.json', 'r') as f:
            cache = json.load(f)
    except:
        cache = {'stocks': {}}
    
    updated_stocks = {}
    
    for symbol in test_symbols:
        print(f"📊 Testing {symbol}...")
        
        try:
            stock_data = fetch_stock_data(symbol)
            
            if stock_data:
                print(f"  ✅ Price: ${stock_data['price']}")
                print(f"  📋 Sector: {stock_data['sector']}")
                print(f"  🏭 Industry: {stock_data['industry']}")
                print(f"  🏷️  Category: {stock_data['category']}")
                print(f"  📈 Gap: {stock_data['gap_pct']}%\n")
                
                # Update cache
                updated_stocks[symbol] = stock_data
                
            else:
                print(f"  ❌ Failed to fetch data\n")
                
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    # Update cache with corrected data
    if updated_stocks:
        cache['stocks'].update(updated_stocks)
        cache['last_update'] = time.time()
        cache['last_update_str'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        with open('stock_cache.json', 'w') as f:
            json.dump(cache, f, indent=2)
        
        print(f"💾 Updated cache with {len(updated_stocks)} stocks with correct sector data")
    
    print("🎯 Test complete! Check your web interface - sector data should now appear correctly.")

if __name__ == "__main__":
    test_and_update_sectors() 