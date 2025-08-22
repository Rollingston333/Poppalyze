#!/usr/bin/env python3
"""
Test script to demonstrate sector/industry data capabilities in yfinance
Shows examples of how to get and categorize stock sector information
"""

import yfinance as yf
import json

def categorize_stock(sector, industry):
    """Categorize stocks into simplified groups for easier filtering"""
    if not sector or sector == '—':
        return 'Other'
    
    sector = sector.lower()
    industry = industry.lower() if industry else ''
    
    # AI & Technology
    if 'technology' in sector or 'software' in industry or 'artificial intelligence' in industry:
        if 'semiconductor' in industry or 'chip' in industry:
            return 'Semiconductors'
        elif 'software' in industry:
            return 'Software'
        else:
            return 'Technology'
    
    # Healthcare & Biotech
    elif 'healthcare' in sector or 'pharmaceutical' in industry or 'biotechnology' in industry:
        if 'biotechnology' in industry or 'biotech' in industry:
            return 'Biotech'
        else:
            return 'Healthcare'
    
    # Financial Services
    elif 'financial' in sector or 'bank' in industry:
        return 'Finance'
    
    # Energy & Utilities
    elif 'energy' in sector or 'utilities' in sector or 'oil' in industry:
        return 'Energy'
    
    # Defense & Aerospace
    elif 'aerospace' in industry or 'defense' in industry or 'military' in industry:
        return 'Defense'
    
    # Space & Satellite
    elif 'space' in industry or 'satellite' in industry:
        return 'Space'
    
    # Crypto & Blockchain
    elif 'crypto' in industry or 'blockchain' in industry or 'bitcoin' in industry:
        return 'Crypto'
    
    # Electric Vehicles & Clean Energy
    elif 'electric vehicle' in industry or 'clean energy' in industry or 'solar' in industry:
        return 'Clean Energy'
    
    # Consumer Goods
    elif 'consumer' in sector:
        return 'Consumer'
    
    # Real Estate
    elif 'real estate' in sector:
        return 'Real Estate'
    
    # Communication & Media
    elif 'communication' in sector or 'media' in industry:
        return 'Media'
    
    # Basic Materials
    elif 'materials' in sector or 'mining' in industry:
        return 'Materials'
    
    # Industrials
    elif 'industrial' in sector:
        return 'Industrial'
    
    else:
        return 'Other'

def test_sector_data():
    """Test sector data retrieval for various stocks"""
    test_symbols = [
        'NVDA',    # Semiconductors
        'MSFT',    # Software
        'TSLA',    # Electric Vehicles
        'PFE',     # Healthcare/Pharma
        'JPM',     # Finance
        'LMT',     # Defense
        'XOM',     # Energy
        'AMZN',    # Technology/Consumer
        'COIN',    # Crypto-related
        'MRNA',    # Biotech
        'DIS',     # Media/Entertainment
        'BA',      # Aerospace
        'ABVE',    # Biotech (small cap)
        'MP',      # Materials/Mining
        'SOFI'     # Fintech
    ]
    
    print("🧪 Testing Sector/Industry Data Retrieval\n")
    print(f"{'Symbol':<8} {'Price':<8} {'Sector':<20} {'Industry':<30} {'Category':<15}")
    print("=" * 95)
    
    results = []
    
    for symbol in test_symbols:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get basic data
            price = info.get('regularMarketPrice') or info.get('currentPrice', 0)
            sector = info.get('sector', '—')
            industry = info.get('industry', '—')
            
            # Get our simplified category
            category = categorize_stock(sector, industry)
            
            # Store results
            results.append({
                'symbol': symbol,
                'price': price,
                'sector': sector,
                'industry': industry,
                'category': category
            })
            
            # Display results
            print(f"{symbol:<8} ${price:<7.2f} {sector[:19]:<20} {industry[:29]:<30} {category:<15}")
            
        except Exception as e:
            print(f"{symbol:<8} Error: {e}")
    
    print("\n" + "=" * 95)
    
    # Group by category
    print("\n📊 Stocks by Category:\n")
    categories = {}
    for result in results:
        cat = result['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result['symbol'])
    
    for category, symbols in sorted(categories.items()):
        print(f"{category:<15}: {', '.join(symbols)}")
    
    print(f"\n✅ Successfully categorized {len(results)} stocks into {len(categories)} categories")
    
    # Show available yfinance sector screener
    print("\n🔍 Available Sector Screening with yfinance:")
    print("You can use the built-in screener for Technology sector:")
    print("```python")
    print("import yfinance as yf")
    print("tech_stocks = yf.screen('growth_technology_stocks')")
    print("for stock in tech_stocks['quotes']:")
    print("    print(f\"{stock['symbol']}: {stock.get('sector', 'N/A')}\")")
    print("```")
    
    return results

if __name__ == "__main__":
    results = test_sector_data()
    
    # Save results to JSON for inspection
    with open('sector_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to sector_test_results.json")
    print("\n🚀 To enable sector filtering in your screener:")
    print("1. Stop the current Flask app (Ctrl+C)")
    print("2. Stop the background scanner (Ctrl+C)")  
    print("3. Restart both: python3 background_scanner.py & python3 app.py")
    print("4. The sector dropdown will appear in the filter panel!") 