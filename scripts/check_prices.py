#!/usr/bin/env python3

import json

def check_stock_prices():
    """Check the prices of stocks in the cache"""
    
    try:
        with open('stock_cache.json', 'r') as f:
            data = json.load(f)
        
        print("📊 Stock Prices in Cache:")
        print("=" * 40)
        
        prices = []
        for symbol, stock in data['stocks'].items():
            price = stock.get('price', 0)
            prices.append(price)
            print(f"{symbol}: ${price:.2f}")
        
        print("\n📈 Price Summary:")
        print(f"Total stocks: {len(prices)}")
        print(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        
        # Check how many stocks are in $1-$20 range
        in_range = [p for p in prices if 1 <= p <= 20]
        print(f"Stocks in $1-$20 range: {len(in_range)}")
        
        if len(in_range) == 0:
            print("❌ No stocks in $1-$20 range!")
            print("💡 Try adjusting the price filter to include higher-priced stocks")
        
    except FileNotFoundError:
        print("❌ stock_cache.json not found")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_stock_prices() 