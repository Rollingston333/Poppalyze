#!/usr/bin/env python3
import json

# Load cache data
with open('stock_cache.json', 'r') as f:
    data = json.load(f)

stocks = data.get('stocks', {})

print("Stocks between $1-20 with their gap percentages:")
print("=" * 50)

positive_gaps = []
negative_gaps = []

for symbol, stock in stocks.items():
    price = stock.get('price', 0)
    gap_pct = stock.get('gap_pct', 0)
    
    if 1 <= price <= 20:
        if gap_pct > 0:
            positive_gaps.append((symbol, price, gap_pct))
        else:
            negative_gaps.append((symbol, price, gap_pct))

print(f"\n📈 POSITIVE GAPS ({len(positive_gaps)} stocks):")
if positive_gaps:
    for symbol, price, gap in sorted(positive_gaps, key=lambda x: x[2], reverse=True):
        print(f"  {symbol}: ${price:.2f} (+{gap:.2f}%)")
else:
    print("  None found")

print(f"\n📉 NEGATIVE GAPS ({len(negative_gaps)} stocks):")
for symbol, price, gap in sorted(negative_gaps, key=lambda x: x[2]):
    print(f"  {symbol}: ${price:.2f} ({gap:.2f}%)")

print(f"\n📊 SUMMARY:")
print(f"  Total stocks $1-20: {len(positive_gaps) + len(negative_gaps)}")
print(f"  Positive gaps: {len(positive_gaps)}")
print(f"  Negative gaps: {len(negative_gaps)}") 