#!/usr/bin/env python3
"""
Check the most recent data points from yfinance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

def check_latest_data(symbol):
    """Check the most recent data for a symbol"""
    
    print(f"\n📊 Checking {symbol}:")
    print("-" * 40)
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get 1-minute data for the last 2 days
        hist = ticker.history(period="2d", interval="1m")
        
        if not hist.empty:
            print(f"Total data points: {len(hist)}")
            
            # Show the last 5 data points
            print("\nLast 5 data points:")
            for i in range(min(5, len(hist))):
                idx = hist.index[-(i+1)]
                price = hist['Close'].iloc[-(i+1)]
                volume = hist['Volume'].iloc[-(i+1)]
                
                # Convert to ET
                if idx.tz is None:
                    time_et = idx.tz_localize('UTC').tz_convert('US/Eastern')
                else:
                    time_et = idx.tz_convert('US/Eastern')
                
                print(f"  {time_et.strftime('%Y-%m-%d %H:%M:%S ET')} - ${price:.2f} (Vol: {volume:,.0f})")
            
            # Check for any data after 4 PM ET
            print("\nData after 4 PM ET:")
            after_4pm_data = []
            
            for idx, row in hist.iterrows():
                if idx.tz is None:
                    time_et = idx.tz_localize('UTC').tz_convert('US/Eastern')
                else:
                    time_et = idx.tz_convert('US/Eastern')
                
                if time_et.hour >= 16:  # After 4 PM
                    after_4pm_data.append({
                        'time': time_et,
                        'price': row['Close'],
                        'volume': row['Volume']
                    })
            
            if after_4pm_data:
                for data in after_4pm_data[-3:]:  # Show last 3
                    print(f"  {data['time'].strftime('%H:%M:%S ET')} - ${data['price']:.2f} (Vol: {data['volume']:,.0f})")
            else:
                print("  No data after 4 PM ET found")
        
        else:
            print("No data available")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    print("🔍 Checking Latest yfinance Data")
    print("=" * 50)
    
    # Check current time
    et_tz = pytz.timezone('US/Eastern')
    current_time_et = datetime.now(et_tz)
    print(f"Current ET Time: {current_time_et.strftime('%Y-%m-%d %H:%M:%S ET')}")
    
    # Test symbols
    symbols = ['AAPL', 'TSLA', 'NVDA', 'SPY']
    
    for symbol in symbols:
        check_latest_data(symbol)

if __name__ == "__main__":
    main() 