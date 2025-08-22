#!/usr/bin/env python3
"""
Test the enhanced after-hours detection with real yfinance data
"""

import yfinance as yf
import json
from datetime import datetime
import pytz

def test_enhanced_after_hours():
    """Test the enhanced after-hours detection"""
    
    print("🔍 Testing Enhanced After-Hours Detection")
    print("=" * 60)
    
    # Test symbols that should have after-hours data
    test_symbols = ['AAPL', 'TSLA', 'NVDA', 'SPY', 'QQQ']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        print("-" * 40)
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                print("❌ No info available")
                continue
            
            # Check for after-hours data availability
            has_pre_post_data = info.get('hasPrePostMarketData', False)
            market_state = info.get('marketState', 'REGULAR')
            
            print(f"Has Pre/Post Market Data: {has_pre_post_data}")
            print(f"Market State: {market_state}")
            
            if has_pre_post_data:
                # Get regular market data
                current_price = info.get('currentPrice', info.get('regularMarketPrice'))
                regular_price = info.get('regularMarketPrice')
                previous_close = info.get('regularMarketPreviousClose')
                
                # Get after-hours data
                post_market_price = info.get('postMarketPrice')
                post_market_change = info.get('postMarketChange')
                post_market_change_pct = info.get('postMarketChangePercent')
                
                # Get pre-market data
                pre_market_price = info.get('preMarketPrice')
                pre_market_change = info.get('preMarketChange')
                pre_market_change_pct = info.get('preMarketChangePercent')
                
                print(f"Regular Market Price: ${regular_price:.2f}")
                print(f"Current Price: ${current_price:.2f}")
                
                if post_market_price and post_market_price != current_price:
                    print(f"🔔 AFTER-HOURS: ${post_market_price:.2f} (Change: {post_market_change_pct:+.2f}%)")
                    print(f"   After-hours change: ${post_market_change:+.2f}")
                else:
                    print("❌ No after-hours price difference detected")
                
                if pre_market_price and pre_market_price != current_price:
                    print(f"🌅 PRE-MARKET: ${pre_market_price:.2f} (Change: {pre_market_change_pct:+.2f}%)")
                    print(f"   Pre-market change: ${pre_market_change:+.2f}")
                else:
                    print("❌ No pre-market price difference detected")
                
                # Map market state
                if market_state == 'POST':
                    mapped_state = 'AFTER-HOURS'
                elif market_state == 'PRE':
                    mapped_state = 'PRE-MARKET'
                elif market_state == 'REGULAR':
                    mapped_state = 'REGULAR'
                elif market_state == 'CLOSED':
                    mapped_state = 'CLOSED'
                else:
                    mapped_state = market_state
                
                print(f"Mapped Market State: {mapped_state}")
                
            else:
                print("❌ No pre/post market data available")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ Enhanced after-hours detection test completed!")

if __name__ == "__main__":
    test_enhanced_after_hours() 