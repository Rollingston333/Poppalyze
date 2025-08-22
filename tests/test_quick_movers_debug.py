#!/usr/bin/env python3
"""
Debug script to test Quick Movers functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_quick_movers, get_top_positive_gappers
import json

def test_quick_movers():
    """Test Quick Movers functionality"""
    
    print("🔍 Testing Quick Movers Debug")
    print("=" * 50)
    
    try:
        # Load cache data
        with open('stock_cache.json', 'r') as f:
            cache_data = json.load(f)
        
        stocks = cache_data.get('stocks', {})
        print(f"Total stocks in cache: {len(stocks)}")
        
        # Test Quick Movers with dictionary format
        print("\n📊 Testing Quick Movers (dictionary format):")
        quick_movers = get_quick_movers(stocks)
        print(f"Quick Movers found: {len(quick_movers)}")
        
        for i, qm in enumerate(quick_movers[:3]):
            print(f"  {i+1}. {qm['symbol']}: {qm['pct_change']:.2f}%, {qm['rel_vol']:.1f}x vol, score: {qm['movement_score']:.2f}")
        
        # Test Top Positive Gappers
        print("\n📊 Testing Top Positive Gappers (dictionary format):")
        top_gappers = get_top_positive_gappers(stocks)
        print(f"Top Gappers found: {len(top_gappers)}")
        
        for i, tg in enumerate(top_gappers[:3]):
            print(f"  {i+1}. {tg['symbol']}: {tg['gap_pct']:.2f}% gap")
        
        # Test with list format (simulate filtered stocks)
        print("\n📊 Testing with list format (simulated filtered stocks):")
        stocks_list = []
        for symbol, stock_data in stocks.items():
            stocks_list.append({
                'symbol': symbol,
                'price': stock_data.get('price', 0),
                'pct_change': stock_data.get('pct_change', 0),
                'gap_pct': stock_data.get('gap_pct', 0),
                'relative_volume': stock_data.get('relative_volume', 0),
                'volume': stock_data.get('volume', 0),
                'market_cap_display': stock_data.get('market_cap_display', '—'),
                'pe_display': stock_data.get('pe_display', '—'),
                'float': stock_data.get('float', '—'),
                'has_news': stock_data.get('has_news', False),
                'source': stock_data.get('source', 'cache'),
                'timestamp': stock_data.get('timestamp', 0)
            })
        
        quick_movers_list = get_quick_movers(stocks_list)
        print(f"Quick Movers (list format): {len(quick_movers_list)}")
        
        for i, qm in enumerate(quick_movers_list[:3]):
            print(f"  {i+1}. {qm['symbol']}: {qm['pct_change']:.2f}%, {qm['rel_vol']:.1f}x vol")
        
        # Check if any stocks meet the criteria
        print("\n📊 Checking individual stock criteria:")
        for symbol, stock_data in list(stocks.items())[:5]:
            pct_change = abs(stock_data.get('pct_change', 0))
            rel_vol = stock_data.get('relative_volume', 0)
            price = stock_data.get('price', 0)
            
            meets_criteria = pct_change >= 0.5 and rel_vol >= 0.5 and price >= 1
            print(f"  {symbol}: pct_change={pct_change:.2f} (>=0.5: {pct_change >= 0.5}), rel_vol={rel_vol:.2f} (>=0.5: {rel_vol >= 0.5}), price={price:.2f} (>=1: {price >= 1}) -> {'✅' if meets_criteria else '❌'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quick_movers() 