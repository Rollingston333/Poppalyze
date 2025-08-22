#!/usr/bin/env python3

import json

def check_quick_movers_data():
    """Check why Quick Movers aren't showing up"""
    
    try:
        with open('stock_cache.json', 'r') as f:
            data = json.load(f)
        
        print("🔍 Checking Quick Movers Data")
        print("=" * 50)
        
        # Check criteria
        print("📋 Quick Movers Criteria:")
        print("   • gap_pct >= 0.5%")
        print("   • relative_volume >= 0.5x")
        print("   • price >= $1")
        print()
        
        # Check each stock
        qualifying_stocks = []
        
        for symbol, stock in data['stocks'].items():
            gap_pct = abs(stock.get('gap_pct', 0))
            rel_vol = stock.get('relative_volume', 0)
            price = stock.get('price', 0)
            
            print(f"{symbol}: gap_pct={gap_pct:.2f}%, rel_vol={rel_vol:.2f}x, price=${price:.2f}")
            
            # Check if qualifies
            if gap_pct >= 0.5 and rel_vol >= 0.5 and price >= 1:
                qualifying_stocks.append(symbol)
                print(f"   ✅ QUALIFIES")
            else:
                reasons = []
                if gap_pct < 0.5:
                    reasons.append(f"gap_pct too low ({gap_pct:.2f}% < 0.5%)")
                if rel_vol < 0.5:
                    reasons.append(f"rel_vol too low ({rel_vol:.2f}x < 0.5x)")
                if price < 1:
                    reasons.append(f"price too low (${price:.2f} < $1)")
                print(f"   ❌ Does not qualify: {', '.join(reasons)}")
            print()
        
        print(f"📊 Summary:")
        print(f"   Total stocks: {len(data['stocks'])}")
        print(f"   Qualifying stocks: {len(qualifying_stocks)}")
        
        if qualifying_stocks:
            print(f"   ✅ Qualifying stocks: {', '.join(qualifying_stocks)}")
        else:
            print(f"   ❌ No stocks qualify for Quick Movers")
            print(f"   💡 Consider lowering the criteria")
        
    except FileNotFoundError:
        print("❌ stock_cache.json not found")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_quick_movers_data() 