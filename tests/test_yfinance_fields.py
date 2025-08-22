#!/usr/bin/env python3
"""
Test all available fields in yfinance to find after-hours data
"""

import yfinance as yf
import json

def test_all_fields(symbol):
    """Test all available fields for a symbol"""
    
    print(f"\n🔍 Testing all fields for {symbol}:")
    print("-" * 50)
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info:
            print("❌ No info available")
            return
        
        print(f"Total fields available: {len(info)}")
        
        # Group fields by category
        price_fields = []
        volume_fields = []
        market_fields = []
        after_hours_fields = []
        other_fields = []
        
        for key, value in info.items():
            key_lower = key.lower()
            
            if any(term in key_lower for term in ['price', 'close', 'open', 'high', 'low', 'bid', 'ask']):
                price_fields.append((key, value))
            elif any(term in key_lower for term in ['volume', 'vol']):
                volume_fields.append((key, value))
            elif any(term in key_lower for term in ['market', 'cap', 'sector', 'industry']):
                market_fields.append((key, value))
            elif any(term in key_lower for term in ['after', 'pre', 'post', 'extended', 'hours']):
                after_hours_fields.append((key, value))
            else:
                other_fields.append((key, value))
        
        # Display after-hours related fields first
        if after_hours_fields:
            print("\n⏰ AFTER-HOURS RELATED FIELDS:")
            for key, value in after_hours_fields:
                print(f"  {key}: {value}")
        else:
            print("\n⏰ No after-hours specific fields found")
        
        # Display price fields
        if price_fields:
            print("\n💰 PRICE FIELDS:")
            for key, value in price_fields:
                if value is not None and value != '':
                    print(f"  {key}: {value}")
        
        # Display volume fields
        if volume_fields:
            print("\n📊 VOLUME FIELDS:")
            for key, value in volume_fields:
                if value is not None and value != '':
                    print(f"  {key}: {value}")
        
        # Display market fields
        if market_fields:
            print("\n🏢 MARKET FIELDS:")
            for key, value in market_fields:
                if value is not None and value != '':
                    print(f"  {key}: {value}")
        
        # Show a few other interesting fields
        print("\n🔍 OTHER INTERESTING FIELDS:")
        interesting_fields = ['regularMarketTime', 'exchange', 'quoteType', 'symbol', 'shortName', 'longName']
        for field in interesting_fields:
            if field in info:
                print(f"  {field}: {info[field]}")
        
        # Try to get more detailed info
        print("\n🔍 ATTEMPTING TO GET MORE DETAILED INFO:")
        
        # Try different methods
        try:
            if hasattr(ticker, 'fast_info'):
                fast_info = ticker.fast_info
                print(f"  Fast info available: {len(dir(fast_info))} attributes")
                
                # Check for after-hours related attributes
                for attr in dir(fast_info):
                    if any(term in attr.lower() for term in ['after', 'pre', 'post', 'extended', 'hours']):
                        try:
                            value = getattr(fast_info, attr)
                            print(f"    {attr}: {value}")
                        except:
                            pass
        except Exception as e:
            print(f"  Fast info error: {e}")
        
        # Try to get quote data
        try:
            # Some versions of yfinance have different methods
            if hasattr(ticker, 'quote'):
                quote = ticker.quote
                print(f"  Quote data available: {quote}")
            elif hasattr(ticker, 'get_quote'):
                quote = ticker.get_quote()
                print(f"  Quote data available: {quote}")
        except Exception as e:
            print(f"  Quote error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🔍 Testing yfinance Field Availability")
    print("=" * 60)
    
    # Test with a few symbols
    symbols = ['AAPL', 'TSLA', 'SPY']
    
    for symbol in symbols:
        test_all_fields(symbol)
        print("\n" + "="*60)

if __name__ == "__main__":
    main() 