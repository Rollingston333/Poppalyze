#!/usr/bin/env python3
"""
Test script to verify conservative rate limiting works
"""

import time
import yfinance as yf

def test_conservative_rate_limiting():
    """Test conservative rate limiting with just 3 popular stocks"""
    test_symbols = ['AAPL', 'MSFT', 'TSLA']
    
    print("🧪 Testing conservative rate limiting with 3 stocks...")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for i, symbol in enumerate(test_symbols, 1):
        print(f"\n📊 Testing {symbol} ({i}/{len(test_symbols)})...")
        
        # Add delay between requests
        if i > 1:
            delay = 10.0  # 10 second delay
            print(f"⏳ Waiting {delay}s to respect rate limits...")
            time.sleep(delay)
        
        # Add extra delay every 2 requests
        if i % 2 == 0:
            extra_delay = 30
            print(f"⏸️  Taking a {extra_delay}s break...")
            time.sleep(extra_delay)
        
        try:
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Get basic info
            info = ticker.info
            if not info or 'symbol' not in info:
                raise ValueError(f"No data available for {symbol}")
            
            # Get historical data
            hist = ticker.history(period="2d", interval="1d")
            if hist.empty or len(hist) < 2:
                raise ValueError(f"Insufficient historical data for {symbol}")
            
            # Get price data
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            previous_close = hist['Close'].iloc[-2] if len(hist) >= 2 else None
            
            if current_price and previous_close:
                gap_pct = ((current_price - previous_close) / previous_close) * 100
                print(f"✅ {symbol}: ${current_price:.2f} ({gap_pct:+.2f}% gap)")
                successful += 1
            else:
                print(f"❌ {symbol}: Missing price data")
                failed += 1
                
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")
            failed += 1
    
    print(f"\n🎉 Test completed!")
    print(f"✅ Successful: {successful}/{len(test_symbols)}")
    print(f"❌ Failed: {failed}/{len(test_symbols)}")
    
    if successful == len(test_symbols):
        print("🎯 All tests passed! Rate limiting is working.")
    else:
        print("⚠️  Some tests failed. Rate limiting may need adjustment.")

if __name__ == "__main__":
    test_conservative_rate_limiting() 