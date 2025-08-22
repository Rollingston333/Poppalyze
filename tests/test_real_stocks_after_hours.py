#!/usr/bin/env python3
"""
Test the enhanced scanner with real stocks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from background_scanner import fetch_stock_data

def test_real_stocks():
    """Test the enhanced scanner with real stocks"""
    
    print("🔍 Testing Enhanced Scanner with Real Stocks")
    print("=" * 60)
    
    # Test with some real stocks that should have after-hours data
    test_symbols = ['AAPL', 'TSLA', 'NVDA', 'SPY']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        print("-" * 40)
        
        try:
            # Use the enhanced fetch_stock_data function
            stock_data = fetch_stock_data(symbol)
            
            if stock_data:
                print(f"✅ Data fetched successfully!")
                print(f"Symbol: {stock_data['symbol']}")
                print(f"Price: ${stock_data['price']:.2f}")
                print(f"Gap: {stock_data['gap_pct']:.2f}%")
                print(f"Market State: {stock_data['market_state']}")
                
                # Check for after-hours data
                if stock_data.get('post_market_price'):
                    print(f"🔔 AFTER-HOURS: ${stock_data['post_market_price']:.2f}")
                    if stock_data.get('post_market_change_pct'):
                        print(f"   Change: {stock_data['post_market_change_pct']:+.2f}%")
                
                if stock_data.get('pre_market_price'):
                    print(f"🌅 PRE-MARKET: ${stock_data['pre_market_price']:.2f}")
                    if stock_data.get('pre_market_change_pct'):
                        print(f"   Change: {stock_data['pre_market_change_pct']:+.2f}%")
                
                # Show data age
                if stock_data.get('data_fetch_time'):
                    print(f"Data Age: {stock_data.get('data_age_seconds', 0):.1f} seconds")
                
            else:
                print(f"❌ Failed to fetch data for {symbol}")
                
        except Exception as e:
            print(f"❌ Error testing {symbol}: {e}")
    
    print("\n" + "="*60)
    print("✅ Enhanced scanner test completed!")

if __name__ == "__main__":
    test_real_stocks() 