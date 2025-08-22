#!/usr/bin/env python3
"""
Create a cache with real after-hours data from yfinance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from background_scanner import fetch_stock_data
import json
from datetime import datetime

def create_real_after_hours_cache():
    """Create a cache with real after-hours data"""
    
    print("🔍 Creating Real After-Hours Cache")
    print("=" * 50)
    
    # Real stocks that should have after-hours data
    real_symbols = ['AAPL', 'TSLA', 'NVDA', 'SPY', 'QQQ', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX']
    
    stocks_data = {}
    successful_count = 0
    total_count = len(real_symbols)
    
    for symbol in real_symbols:
        print(f"\n📊 Scanning {symbol}...")
        
        try:
            stock_data = fetch_stock_data(symbol)
            
            if stock_data:
                stocks_data[symbol] = stock_data
                successful_count += 1
                
                print(f"✅ {symbol}: ${stock_data['price']:.2f} (Gap: {stock_data['gap_pct']:.2f}%)")
                
                # Show after-hours data if available
                if stock_data.get('post_market_price'):
                    print(f"   🔔 After-hours: ${stock_data['post_market_price']:.2f} ({stock_data.get('post_market_change_pct', 0):+.2f}%)")
                
                if stock_data.get('pre_market_price'):
                    print(f"   🌅 Pre-market: ${stock_data['pre_market_price']:.2f} ({stock_data.get('pre_market_change_pct', 0):+.2f}%)")
                
            else:
                print(f"❌ Failed to fetch {symbol}")
                
        except Exception as e:
            print(f"❌ Error scanning {symbol}: {e}")
    
    # Create cache structure
    cache_data = {
        'stocks': stocks_data,
        'last_update': datetime.now().isoformat(),
        'last_update_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'successful_count': successful_count,
        'total_count': total_count,
        'scan_type': 'real_after_hours',
        'market_session': 'AFTER-HOURS'
    }
    
    # Save cache
    try:
        with open('stock_cache.json', 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print(f"\n✅ Cache created successfully!")
        print(f"📊 {successful_count}/{total_count} stocks scanned")
        print(f"💾 Cache saved to stock_cache.json")
        
        # Show sample data
        if stocks_data:
            sample_symbol = list(stocks_data.keys())[0]
            sample_stock = stocks_data[sample_symbol]
            print(f"\n📋 Sample data for {sample_symbol}:")
            print(f"   Price: ${sample_stock['price']:.2f}")
            print(f"   After-hours: ${sample_stock.get('post_market_price', 'N/A')}")
            print(f"   Pre-market: ${sample_stock.get('pre_market_price', 'N/A')}")
            print(f"   Market State: {sample_stock.get('market_state', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error saving cache: {e}")

if __name__ == "__main__":
    create_real_after_hours_cache() 