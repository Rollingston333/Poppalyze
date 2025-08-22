#!/usr/bin/env python3
"""
Test script to check yfinance after-market data capabilities
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

def test_after_market_data():
    """Test various methods to get after-market data from yfinance"""
    
    # Test with a few active stocks
    test_symbols = ['AAPL', 'TSLA', 'NVDA', 'SPY']
    
    print("🔍 Testing yfinance After-Market Data Access")
    print("=" * 50)
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        print("-" * 30)
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Method 1: Get basic info
            print("1. Basic Info:")
            info = ticker.info
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            regular_price = info.get('regularMarketPrice', 'N/A')
            print(f"   Current Price: ${current_price}")
            print(f"   Regular Market Price: ${regular_price}")
            
            # Method 2: Get detailed price info
            print("\n2. Detailed Price Info:")
            if hasattr(ticker, 'fast_info'):
                fast_info = ticker.fast_info
                print(f"   Fast Info - Current Price: ${getattr(fast_info, 'last_price', 'N/A')}")
                print(f"   Fast Info - Regular Price: ${getattr(fast_info, 'regular_market_price', 'N/A')}")
            
            # Method 3: Get historical data with different intervals
            print("\n3. Historical Data (1d interval):")
            hist_1d = ticker.history(period="2d", interval="1d")
            if not hist_1d.empty:
                print(f"   Latest Close: ${hist_1d['Close'].iloc[-1]:.2f}")
                print(f"   Previous Close: ${hist_1d['Close'].iloc[-2]:.2f}" if len(hist_1d) > 1 else "   Previous Close: N/A")
            
            # Method 4: Get intraday data (might show after-hours)
            print("\n4. Intraday Data (1m interval, last 5 days):")
            try:
                hist_intraday = ticker.history(period="5d", interval="1m")
                if not hist_intraday.empty:
                    latest_time = hist_intraday.index[-1]
                    latest_price = hist_intraday['Close'].iloc[-1]
                    print(f"   Latest Time: {latest_time}")
                    print(f"   Latest Price: ${latest_price:.2f}")
                    
                    # Check if this is after hours
                    et_tz = pytz.timezone('US/Eastern')
                    if hasattr(latest_time, 'tz_localize'):
                        latest_time_et = latest_time.tz_localize('UTC').tz_convert(et_tz)
                    else:
                        latest_time_et = latest_time.tz_convert(et_tz)
                    
                    hour = latest_time_et.hour
                    minute = latest_time_et.minute
                    time_decimal = hour + minute / 60.0
                    
                    if 16.0 <= time_decimal < 20.0:
                        print(f"   ⏰ AFTER-HOURS: {latest_time_et.strftime('%H:%M:%S ET')}")
                    elif 4.0 <= time_decimal < 9.5:
                        print(f"   🌅 PRE-MARKET: {latest_time_et.strftime('%H:%M:%S ET')}")
                    else:
                        print(f"   📈 Regular Hours: {latest_time_et.strftime('%H:%M:%S ET')}")
                        
            except Exception as e:
                print(f"   ❌ Intraday data error: {e}")
            
            # Method 5: Check for after-hours data in info
            print("\n5. After-Hours Info:")
            after_hours_price = info.get('afterHoursPrice', 'N/A')
            after_hours_change = info.get('afterHoursChange', 'N/A')
            after_hours_change_pct = info.get('afterHoursChangePercent', 'N/A')
            
            print(f"   After Hours Price: ${after_hours_price}")
            print(f"   After Hours Change: ${after_hours_change}")
            print(f"   After Hours Change %: {after_hours_change_pct}%")
            
            # Method 6: Get real-time quote
            print("\n6. Real-time Quote:")
            try:
                quote = ticker.quote
                if quote:
                    print(f"   Quote - Current: ${quote.get('currentPrice', 'N/A')}")
                    print(f"   Quote - Regular: ${quote.get('regularMarketPrice', 'N/A')}")
                    print(f"   Quote - After Hours: ${quote.get('afterHoursPrice', 'N/A')}")
            except Exception as e:
                print(f"   ❌ Quote error: {e}")
            
        except Exception as e:
            print(f"   ❌ Error fetching data for {symbol}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ After-market data test completed!")

def test_market_hours():
    """Test current market hours detection"""
    print("\n🕐 Current Market Hours Check:")
    print("-" * 30)
    
    et_tz = pytz.timezone('US/Eastern')
    current_time_et = datetime.now(et_tz)
    
    print(f"Current ET Time: {current_time_et.strftime('%Y-%m-%d %H:%M:%S ET')}")
    
    hour = current_time_et.hour
    minute = current_time_et.minute
    time_decimal = hour + minute / 60.0
    is_weekday = current_time_et.weekday() < 5
    
    if not is_weekday:
        print("📅 WEEKEND - Markets Closed")
    elif 4.0 <= time_decimal < 9.5:
        print("🌅 PRE-MARKET (4:00 AM - 9:30 AM ET)")
    elif 9.5 <= time_decimal < 16.0:
        print("📈 REGULAR MARKET HOURS (9:30 AM - 4:00 PM ET)")
    elif 16.0 <= time_decimal < 20.0:
        print("🌙 AFTER-HOURS (4:00 PM - 8:00 PM ET)")
    else:
        print("🌃 MARKETS CLOSED (8:00 PM - 4:00 AM ET)")

if __name__ == "__main__":
    test_market_hours()
    test_after_market_data() 