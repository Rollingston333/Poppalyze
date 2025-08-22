#!/usr/bin/env python3
"""
Test script to verify after-market data fetching
"""

import yfinance as yf
import json
from datetime import datetime

def test_aftermarket_data():
    """Test after-market data fetching for various stocks"""
    
    # Test stocks that might have after-market activity
    test_symbols = ['AAPL', 'TSLA', 'NVDA', 'AMD', 'META', 'NFLX', 'AMZN', 'GOOGL']
    
    print("🔍 Testing After-Market Data Fetching")
    print("=" * 50)
    
    for symbol in test_symbols:
        try:
            print(f"\n📊 Testing {symbol}...")
            
            # Get stock info
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract after-market data
            post_market_price = info.get('postMarketPrice')
            post_market_source = info.get('postMarketSource')
            regular_market_price = info.get('regularMarketPrice')
            regular_market_previous_close = info.get('regularMarketPreviousClose')
            
            print(f"  Regular Market Price: ${regular_market_price}")
            print(f"  Previous Close: ${regular_market_previous_close}")
            print(f"  After-Market Price: ${post_market_price if post_market_price else 'None'}")
            print(f"  After-Market Source: {post_market_source if post_market_source else 'None'}")
            
            # Calculate after-market change if available
            if post_market_price and regular_market_previous_close:
                change_pct = ((post_market_price - regular_market_previous_close) / regular_market_previous_close) * 100
                print(f"  After-Market Change: {change_pct:.2f}%")
            else:
                print(f"  After-Market Change: N/A (no after-market data)")
                
        except Exception as e:
            print(f"  ❌ Error testing {symbol}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ After-market data test completed")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Note: After-market data is only available:")
    print("   - After regular market hours (4:00 PM ET)")
    print("   - For stocks with significant after-hours trading")
    print("   - When there's actual after-market activity")

if __name__ == "__main__":
    test_aftermarket_data() 