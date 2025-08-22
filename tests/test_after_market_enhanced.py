#!/usr/bin/env python3
"""
Enhanced test script to check yfinance after-market data capabilities
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

def test_enhanced_after_market_data():
    """Test enhanced methods to get after-market data from yfinance"""
    
    # Test with a few active stocks
    test_symbols = ['AAPL', 'TSLA', 'NVDA', 'SPY']
    
    print("🔍 Enhanced yfinance After-Market Data Test")
    print("=" * 60)
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        print("-" * 40)
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Method 1: Get basic info with all available fields
            print("1. Basic Info Analysis:")
            info = ticker.info
            
            # Check all price-related fields
            price_fields = [
                'currentPrice', 'regularMarketPrice', 'afterHoursPrice', 
                'preMarketPrice', 'regularMarketOpen', 'regularMarketPreviousClose',
                'bid', 'ask', 'dayLow', 'dayHigh'
            ]
            
            for field in price_fields:
                value = info.get(field, 'N/A')
                if value != 'N/A' and value is not None:
                    print(f"   {field}: ${value}")
            
            # Method 2: Get intraday data with proper timezone handling
            print("\n2. Intraday Data Analysis:")
            try:
                # Get 1-minute data for the last 2 days
                hist_intraday = ticker.history(period="2d", interval="1m")
                
                if not hist_intraday.empty:
                    # Get the latest data point
                    latest_time = hist_intraday.index[-1]
                    latest_price = hist_intraday['Close'].iloc[-1]
                    
                    # Proper timezone conversion
                    if latest_time.tz is None:
                        latest_time_et = latest_time.tz_localize('UTC').tz_convert('US/Eastern')
                    else:
                        latest_time_et = latest_time.tz_convert('US/Eastern')
                    
                    print(f"   Latest Time: {latest_time_et.strftime('%Y-%m-%d %H:%M:%S ET')}")
                    print(f"   Latest Price: ${latest_price:.2f}")
                    
                    # Check if this is after hours
                    hour = latest_time_et.hour
                    minute = latest_time_et.minute
                    time_decimal = hour + minute / 60.0
                    
                    if 16.0 <= time_decimal < 20.0:
                        print(f"   ⏰ AFTER-HOURS DETECTED")
                        
                        # Look for after-hours price changes
                        if len(hist_intraday) > 1:
                            # Get the last regular market close (around 4 PM)
                            market_close_time = latest_time_et.replace(hour=16, minute=0, second=0, microsecond=0)
                            
                            # Find the closest data point to market close
                            market_close_idx = None
                            for i, idx in enumerate(hist_intraday.index):
                                idx_et = idx.tz_convert('US/Eastern')
                                if idx_et.hour >= 16:
                                    market_close_idx = i
                                    break
                            
                            if market_close_idx is not None:
                                market_close_price = hist_intraday['Close'].iloc[market_close_idx]
                                after_hours_change = latest_price - market_close_price
                                after_hours_change_pct = (after_hours_change / market_close_price) * 100
                                
                                print(f"   Market Close Price: ${market_close_price:.2f}")
                                print(f"   After-Hours Change: ${after_hours_change:.2f} ({after_hours_change_pct:+.2f}%)")
                    
                    elif 4.0 <= time_decimal < 9.5:
                        print(f"   🌅 PRE-MARKET DETECTED")
                    else:
                        print(f"   📈 Regular Hours")
                        
            except Exception as e:
                print(f"   ❌ Intraday data error: {e}")
            
            # Method 3: Try to get real-time data
            print("\n3. Real-time Data Attempt:")
            try:
                # Get the most recent data possible
                recent_data = ticker.history(period="1d", interval="1m")
                if not recent_data.empty:
                    latest = recent_data.iloc[-1]
                    print(f"   Latest OHLC: O=${latest['Open']:.2f} H=${latest['High']:.2f} L=${latest['Low']:.2f} C=${latest['Close']:.2f}")
                    print(f"   Volume: {latest['Volume']:,}")
            except Exception as e:
                print(f"   ❌ Real-time data error: {e}")
            
            # Method 4: Check for any after-hours indicators
            print("\n4. After-Hours Indicators:")
            
            # Check if current price differs from regular market price
            current_price = info.get('currentPrice')
            regular_price = info.get('regularMarketPrice')
            
            if current_price and regular_price and current_price != regular_price:
                change = current_price - regular_price
                change_pct = (change / regular_price) * 100
                print(f"   ⚠️  Price difference detected!")
                print(f"   Regular: ${regular_price:.2f}")
                print(f"   Current: ${current_price:.2f}")
                print(f"   Change: ${change:.2f} ({change_pct:+.2f}%)")
            else:
                print(f"   No price difference detected")
            
            # Method 5: Check market state
            print("\n5. Market State Analysis:")
            et_tz = pytz.timezone('US/Eastern')
            current_time_et = datetime.now(et_tz)
            
            hour = current_time_et.hour
            minute = current_time_et.minute
            time_decimal = hour + minute / 60.0
            is_weekday = current_time_et.weekday() < 5
            
            if not is_weekday:
                print(f"   📅 WEEKEND - Markets Closed")
            elif 4.0 <= time_decimal < 9.5:
                print(f"   🌅 PRE-MARKET (4:00 AM - 9:30 AM ET)")
            elif 9.5 <= time_decimal < 16.0:
                print(f"   📈 REGULAR MARKET HOURS (9:30 AM - 4:00 PM ET)")
            elif 16.0 <= time_decimal < 20.0:
                print(f"   🌙 AFTER-HOURS (4:00 PM - 8:00 PM ET)")
                print(f"   Current Time: {current_time_et.strftime('%H:%M:%S ET')}")
            else:
                print(f"   🌃 MARKETS CLOSED (8:00 PM - 4:00 AM ET)")
            
        except Exception as e:
            print(f"   ❌ Error fetching data for {symbol}: {e}")
        
        # Add a small delay to avoid rate limiting
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ Enhanced after-market data test completed!")

def test_specific_after_hours_stocks():
    """Test stocks that are likely to have after-hours activity"""
    
    print("\n🔍 Testing Stocks with Likely After-Hours Activity:")
    print("=" * 60)
    
    # Stocks that often have after-hours activity
    after_hours_stocks = ['TSLA', 'NVDA', 'AMD', 'META', 'NFLX']
    
    for symbol in after_hours_stocks:
        print(f"\n📊 {symbol} After-Hours Check:")
        print("-" * 30)
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Get the most recent intraday data
            hist = ticker.history(period="1d", interval="1m")
            
            if not hist.empty:
                latest_time = hist.index[-1]
                latest_price = hist['Close'].iloc[-1]
                
                # Convert to ET
                if latest_time.tz is None:
                    latest_time_et = latest_time.tz_localize('UTC').tz_convert('US/Eastern')
                else:
                    latest_time_et = latest_time.tz_convert('US/Eastern')
                
                print(f"   Latest: {latest_time_et.strftime('%H:%M:%S ET')} - ${latest_price:.2f}")
                
                # Check if this is after hours
                hour = latest_time_et.hour
                if 16 <= hour < 20:
                    print(f"   ⏰ AFTER-HOURS ACTIVITY DETECTED")
                    
                    # Find market close price (around 4 PM)
                    market_close_price = None
                    for idx in hist.index:
                        idx_et = idx.tz_convert('US/Eastern')
                        if idx_et.hour >= 16:
                            market_close_price = hist.loc[idx, 'Close']
                            break
                    
                    if market_close_price:
                        change = latest_price - market_close_price
                        change_pct = (change / market_close_price) * 100
                        print(f"   Market Close: ${market_close_price:.2f}")
                        print(f"   After-Hours: ${latest_price:.2f}")
                        print(f"   Change: ${change:.2f} ({change_pct:+.2f}%)")
                else:
                    print(f"   📈 Regular market hours")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    test_enhanced_after_market_data()
    test_specific_after_hours_stocks() 