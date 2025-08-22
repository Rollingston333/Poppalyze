#!/usr/bin/env python3
"""
Utility to manually add missing stocks to the cache
Usage: python3 add_missing_stock.py SYMBOL
"""

import sys
import json
import time
from background_scanner import fetch_stock_data

def add_stock_to_cache(symbol):
    """Add a specific stock to the cache"""
    print(f"Adding {symbol} to cache...")
    
    # Fetch stock data
    stock_data = fetch_stock_data(symbol)
    
    if not stock_data:
        print(f"❌ Failed to fetch data for {symbol}")
        return False
    
    # Load existing cache
    try:
        with open('stock_cache.json', 'r') as f:
            cache_data = json.load(f)
    except FileNotFoundError:
        cache_data = {'stocks': {}, 'last_update': time.time()}
    
    # Add stock to cache
    cache_data['stocks'][symbol] = stock_data
    cache_data['last_update'] = time.time()
    
    # Save updated cache
    with open('stock_cache.json', 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    print(f"✅ {symbol} added to cache!")
    print(f"   Price: ${stock_data['price']}")
    print(f"   Gap: {stock_data['gap_pct']}%")
    print(f"   Volume: {stock_data['volume']}")
    print(f"   Market Cap: {stock_data['market_cap_display']}")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 add_missing_stock.py SYMBOL")
        print("Example: python3 add_missing_stock.py IXHL")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    success = add_stock_to_cache(symbol)
    
    if success:
        print(f"\n🎉 {symbol} is now available in the web interface!")
    else:
        print(f"\n❌ Failed to add {symbol}")
        sys.exit(1)

if __name__ == "__main__":
    main() 