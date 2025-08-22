#!/usr/bin/env python3

import json
import yfinance as yf
import time
from datetime import datetime

def create_mixed_price_cache():
    """Create cache with mix of low and high-priced stocks"""
    
    # Mix of low and high-priced stocks
    symbols = [
        # Low-priced stocks ($1-$20)
        'SNDL', 'PLUG', 'NIO', 'XPEV', 'LI', 'NKLA', 'WKHS', 'IDEX', 'CIDM', 'ZOM',
        # Mid-priced stocks ($20-$100)
        'AMD', 'INTC', 'UBER', 'LYFT', 'SNAP', 'PINS', 'SQ', 'ROKU', 'ZM', 'CRWD',
        # High-priced stocks ($100+)
        'AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'SPY', 'QQQ'
    ]
    
    print("🔍 Creating Mixed Price Cache")
    print("=" * 50)
    
    stocks_data = {}
    successful_count = 0
    
    for symbol in symbols:
        try:
            print(f"📊 Scanning {symbol}...")
            
            # Get stock data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            current_price = info.get('currentPrice', 0)
            if not current_price:
                current_price = info.get('regularMarketPrice', 0)
            
            # Get previous close
            previous_close = info.get('previousClose', current_price)
            
            # Calculate gap percentage
            if previous_close and previous_close > 0:
                gap_pct = ((current_price - previous_close) / previous_close) * 100
            else:
                gap_pct = 0
            
            # Get after-hours data
            post_market_price = info.get('postMarketPrice', current_price)
            post_market_change = info.get('postMarketChange', 0)
            post_market_change_pct = info.get('postMarketChangePercent', 0)
            
            # Get pre-market data
            pre_market_price = info.get('preMarketPrice', current_price)
            pre_market_change = info.get('preMarketChange', 0)
            pre_market_change_pct = info.get('preMarketChangePercent', 0)
            
            # Get volume data
            volume = info.get('volume', 0)
            avg_volume = info.get('averageVolume', volume)
            relative_volume = volume / avg_volume if avg_volume > 0 else 0
            
            # Get market cap
            market_cap = info.get('marketCap', 0)
            
            # Get PE ratio
            pe_ratio = info.get('trailingPE', 0)
            
            # Get float
            shares_outstanding = info.get('sharesOutstanding', 0)
            float_shares = info.get('floatShares', shares_outstanding)
            
            # Get sector
            sector = info.get('sector', 'Unknown')
            
            # Market state
            market_state = info.get('marketState', 'UNKNOWN')
            
            # Create stock data
            stock_data = {
                'symbol': symbol,
                'price': current_price,
                'previous_close': previous_close,
                'gap_pct': gap_pct,
                'volume': volume,
                'relative_volume': relative_volume,
                'market_cap': market_cap,
                'pe_ratio': pe_ratio,
                'float_shares': float_shares,
                'sector': sector,
                'post_market_price': post_market_price,
                'post_market_change': post_market_change,
                'post_market_change_pct': post_market_change_pct,
                'pre_market_price': pre_market_price,
                'pre_market_change': pre_market_change,
                'pre_market_change_pct': pre_market_change_pct,
                'market_state': market_state,
                'data_fetch_time': datetime.now().isoformat()
            }
            
            stocks_data[symbol] = stock_data
            successful_count += 1
            
            # Show price category
            if current_price < 20:
                price_category = "💰 Low-priced"
            elif current_price < 100:
                price_category = "💎 Mid-priced"
            else:
                price_category = "🏆 High-priced"
            
            print(f"✅ {symbol}: ${current_price:.2f} (Gap: {gap_pct:.2f}%) {price_category}")
            
            # Rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}")
            continue
    
    # Create cache data
    cache_data = {
        'stocks': stocks_data,
        'successful_count': successful_count,
        'total_count': len(symbols),
        'last_update': time.time(),
        'last_update_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'scan_duration_seconds': 0,
        'scan_type': 'mixed_price_cache'
    }
    
    # Save to file
    with open('stock_cache.json', 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    print(f"\n✅ Cache created successfully!")
    print(f"📊 {successful_count}/{len(symbols)} stocks scanned")
    print(f"💾 Cache saved to stock_cache.json")
    
    # Show price distribution
    prices = [stock['price'] for stock in stocks_data.values()]
    low_price = len([p for p in prices if p < 20])
    mid_price = len([p for p in prices if 20 <= p < 100])
    high_price = len([p for p in prices if p >= 100])
    
    print(f"\n📈 Price Distribution:")
    print(f"   💰 Low-priced (<$20): {low_price} stocks")
    print(f"   💎 Mid-priced ($20-$100): {mid_price} stocks")
    print(f"   🏆 High-priced (>$100): {high_price} stocks")

if __name__ == "__main__":
    create_mixed_price_cache() 