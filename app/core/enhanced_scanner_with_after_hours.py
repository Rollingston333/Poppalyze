#!/usr/bin/env python3
"""
Enhanced Stock Scanner with After-Hours Detection
"""

import yfinance as yf
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import pytz
import os

def get_market_session():
    """Determine current market session"""
    et_tz = pytz.timezone('US/Eastern')
    current_time_et = datetime.now(et_tz)
    
    hour = current_time_et.hour
    minute = current_time_et.minute
    time_decimal = hour + minute / 60.0
    is_weekday = current_time_et.weekday() < 5
    
    if not is_weekday:
        return "WEEKEND"
    elif 4.0 <= time_decimal < 9.5:
        return "PRE_MARKET"
    elif 9.5 <= time_decimal < 16.0:
        return "REGULAR_MARKET"
    elif 16.0 <= time_decimal < 20.0:
        return "AFTER_HOURS"
    else:
        return "CLOSED"

def fetch_stock_with_after_hours(symbol):
    """Fetch stock data with enhanced after-hours detection"""
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get basic info
        info = ticker.info
        if not info or 'symbol' not in info:
            return None
        
        # Get historical data for gap calculation
        hist = ticker.history(period="2d", interval="1d")
        if hist.empty or len(hist) < 2:
            return None
        
        # Get intraday data for after-hours detection
        intraday = ticker.history(period="1d", interval="1m")
        
        # Basic price data
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        regular_market_price = info.get('regularMarketPrice', current_price)
        previous_close = hist['Close'].iloc[-2]
        
        # Calculate gap percentage
        gap_pct = ((current_price - previous_close) / previous_close) * 100
        
        # After-hours detection
        after_hours_price = None
        after_hours_change = None
        after_hours_change_pct = None
        market_close_price = None
        
        if not intraday.empty:
            # Get the latest intraday data
            latest_time = intraday.index[-1]
            latest_price = intraday['Close'].iloc[-1]
            
            # Convert to ET
            if latest_time.tz is None:
                latest_time_et = latest_time.tz_localize('UTC').tz_convert('US/Eastern')
            else:
                latest_time_et = latest_time.tz_convert('US/Eastern')
            
            # Check if we're in after-hours
            current_session = get_market_session()
            
            if current_session == "AFTER_HOURS":
                # Look for market close price (around 4 PM)
                for idx in intraday.index:
                    idx_et = idx.tz_convert('US/Eastern')
                    if idx_et.hour >= 16:
                        market_close_price = intraday.loc[idx, 'Close']
                        break
                
                if market_close_price:
                    after_hours_price = latest_price
                    after_hours_change = latest_price - market_close_price
                    after_hours_change_pct = (after_hours_change / market_close_price) * 100
        
        # Volume data
        current_volume = info.get('volume', info.get('regularMarketVolume', 0))
        avg_volume = info.get('averageVolume', info.get('averageVolume10days', 1))
        relative_volume = (current_volume / avg_volume) if avg_volume > 0 else 0
        
        # Other metrics
        market_cap = info.get('marketCap', 0)
        sector = info.get('sector', 'Unknown')
        industry = info.get('industry', 'Unknown')
        
        # Market session info
        current_session = get_market_session()
        
        return {
            'symbol': symbol,
            'price': current_price,
            'regular_market_price': regular_market_price,
            'previous_close': previous_close,
            'gap_pct': round(gap_pct, 2),
            'volume': current_volume,
            'avg_volume': avg_volume,
            'relative_volume': round(relative_volume, 2),
            'market_cap': market_cap,
            'sector': sector,
            'industry': industry,
            'market_session': current_session,
            'after_hours_price': after_hours_price,
            'after_hours_change': after_hours_change,
            'after_hours_change_pct': round(after_hours_change_pct, 2) if after_hours_change_pct else None,
            'market_close_price': market_close_price,
            'data_fetch_time': datetime.now().isoformat(),
            'has_after_hours_data': after_hours_price is not None
        }
        
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None

def scan_after_hours_stocks():
    """Scan for stocks with after-hours activity"""
    
    # Test symbols that often have after-hours activity
    test_symbols = [
        'AAPL', 'TSLA', 'NVDA', 'AMD', 'META', 'NFLX', 'AMZN', 'GOOGL', 
        'MSFT', 'SPY', 'QQQ', 'IWM', 'VTI', 'VOO'
    ]
    
    print("🔍 Scanning for After-Hours Activity")
    print("=" * 50)
    
    results = []
    current_session = get_market_session()
    
    print(f"📅 Current Market Session: {current_session}")
    print(f"🕐 Current Time: {datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S ET')}")
    print()
    
    for symbol in test_symbols:
        print(f"📊 Scanning {symbol}...", end=" ")
        
        data = fetch_stock_with_after_hours(symbol)
        
        if data:
            results.append(data)
            
            if data['has_after_hours_data']:
                print(f"✅ AFTER-HOURS DETECTED!")
                print(f"   Market Close: ${data['market_close_price']:.2f}")
                print(f"   After-Hours: ${data['after_hours_price']:.2f}")
                print(f"   Change: ${data['after_hours_change']:.2f} ({data['after_hours_change_pct']:+.2f}%)")
            else:
                print(f"📈 Regular market data")
                print(f"   Price: ${data['price']:.2f}")
                print(f"   Gap: {data['gap_pct']:+.2f}%")
        else:
            print("❌ Failed to fetch data")
        
        # Rate limiting
        time.sleep(0.5)
    
    return results

def save_after_hours_cache(data):
    """Save after-hours data to cache"""
    
    cache_data = {
        'stocks': {},
        'last_update': time.time(),
        'last_update_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'market_session': get_market_session(),
        'total_count': len(data),
        'after_hours_count': len([s for s in data if s['has_after_hours_data']]),
        'scan_type': 'after_hours_enhanced'
    }
    
    # Convert list to dict format
    for stock in data:
        cache_data['stocks'][stock['symbol']] = stock
    
    # Save to file
    with open('after_hours_cache.json', 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    print(f"\n💾 After-hours cache saved: {len(data)} stocks")
    print(f"⏰ After-hours activity detected: {cache_data['after_hours_count']} stocks")

def main():
    """Main function"""
    print("🚀 Enhanced After-Hours Stock Scanner")
    print("=" * 50)
    
    # Scan for after-hours activity
    results = scan_after_hours_stocks()
    
    if results:
        # Save results
        save_after_hours_cache(results)
        
        # Show summary
        print("\n📊 Summary:")
        print("-" * 30)
        
        after_hours_stocks = [s for s in results if s['has_after_hours_data']]
        
        if after_hours_stocks:
            print(f"⏰ Stocks with After-Hours Activity: {len(after_hours_stocks)}")
            for stock in after_hours_stocks:
                print(f"   {stock['symbol']}: ${stock['after_hours_change']:.2f} ({stock['after_hours_change_pct']:+.2f}%)")
        else:
            print("📈 No after-hours activity detected")
            print("   (This is normal if markets are closed or no significant after-hours movement)")
        
        print(f"\n🌐 Check the web interface for full results")
        print(f"📄 Cache file: after_hours_cache.json")
    
    else:
        print("❌ No data retrieved")

if __name__ == "__main__":
    main() 