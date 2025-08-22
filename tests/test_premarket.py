#!/usr/bin/env python3
"""
Test script to verify pre-market data fetching
"""

import yfinance as yf
import json
from datetime import datetime

def test_premarket_data():
    """Test pre-market data fetching for various stocks"""
    
    # Test stocks that might have pre-market activity
    test_symbols = ['AAPL', 'TSLA', 'NVDA', 'AMD', 'META', 'NFLX', 'AMZN', 'GOOGL']
    
    print("🔍 Testing Pre-Market Data Fetching")
    print("=" * 50)
    
    for symbol in test_symbols:
        try:
            print(f"\n📊 Testing {symbol}...")
            
            # Get stock info
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract pre-market data
            pre_market_price = info.get('preMarketPrice')
            pre_market_source = info.get('preMarketSource')
            regular_market_price = info.get('regularMarketPrice')
            regular_market_previous_close = info.get('regularMarketPreviousClose')
            
            print(f"  Regular Market Price: ${regular_market_price}")
            print(f"  Previous Close: ${regular_market_previous_close}")
            print(f"  Pre-Market Price: ${pre_market_price if pre_market_price else 'None'}")
            print(f"  Pre-Market Source: {pre_market_source if pre_market_source else 'None'}")
            
            # Calculate pre-market change if available
            if pre_market_price and regular_market_previous_close:
                change_pct = ((pre_market_price - regular_market_previous_close) / regular_market_previous_close) * 100
                print(f"  Pre-Market Change: {change_pct:.2f}%")
            else:
                print(f"  Pre-Market Change: N/A (no pre-market data)")
                
        except Exception as e:
            print(f"  ❌ Error testing {symbol}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Pre-market data test completed")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Note: Pre-market data is only available:")
    print("   - Before regular market hours (9:30 AM ET)")
    print("   - For stocks with significant pre-market trading")
    print("   - When there's actual pre-market activity")

if __name__ == "__main__":
    test_premarket_data() 