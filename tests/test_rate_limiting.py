#!/usr/bin/env python3
"""
Test script to verify rate limiting works before running full scanner
"""

import time
import yfinance as yf

def test_rate_limiting():
    """Test rate limiting with a few popular stocks"""
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    print("🧪 Testing rate limiting with 5 popular stocks...")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for i, symbol in enumerate(test_symbols, 1):
        print(f"\n📊 Testing {symbol} ({i}/{len(test_symbols)})...")
        
        # Add delay between requests
        if i > 1:
            delay = 5.0
            print(f"⏳ Waiting {delay}s to respect rate limits...")
            time.sleep(delay)
        
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
            
            # Process data
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
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results:")
    print(f"✅ Successful: {successful}/{len(test_symbols)}")
    print(f"❌ Failed: {failed}/{len(test_symbols)}")
    
    if successful > 0:
        print("✅ Rate limiting test passed! Ready to run full scanner.")
        return True
    else:
        print("❌ Rate limiting test failed! Need to adjust delays.")
        return False

if __name__ == "__main__":
    test_rate_limiting() 