#!/usr/bin/env python3
"""
Debug script to test template rendering and Quick Movers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, get_quick_movers
import json

def test_template_debug():
    """Test template rendering with Quick Movers"""
    
    print("🔍 Testing Template Debug")
    print("=" * 50)
    
    try:
        # Load cache data
        with open('stock_cache.json', 'r') as f:
            cache_data = json.load(f)
        
        stocks = cache_data.get('stocks', {})
        print(f"Total stocks in cache: {len(stocks)}")
        
        # Test Quick Movers generation
        quick_movers = get_quick_movers(stocks)
        print(f"Quick Movers generated: {len(quick_movers)}")
        
        if quick_movers:
            print("First Quick Mover:")
            print(f"  Symbol: {quick_movers[0]['symbol']}")
            print(f"  Price: {quick_movers[0]['price']}")
            print(f"  Pct Change: {quick_movers[0]['pct_change']}")
            print(f"  Rel Vol: {quick_movers[0]['rel_vol']}")
        
        # Test with Flask app context
        with app.test_client() as client:
            print("\n📊 Testing Flask route:")
            
            # Test the main route
            response = client.get('/')
            print(f"Status code: {response.status_code}")
            
            # Check if Quick Movers are in the response
            content = response.get_data(as_text=True)
            has_quick_movers = 'Quick Movers' in content
            has_quick_movers_section = '⚡ Quick Movers' in content
            
            print(f"Contains 'Quick Movers': {has_quick_movers}")
            print(f"Contains '⚡ Quick Movers': {has_quick_movers_section}")
            
            # Look for the specific section
            if '⚡ Quick Movers' in content:
                start = content.find('⚡ Quick Movers')
                end = content.find('</div>', start) + 6
                section = content[start:end]
                print(f"\nQuick Movers section found:")
                print(section[:200] + "..." if len(section) > 200 else section)
            else:
                print("\n❌ Quick Movers section not found in response")
                
                # Look for highlight section
                if 'highlight-section' in content:
                    start = content.find('highlight-section')
                    end = content.find('</div>', start) + 6
                    highlight_section = content[start:end]
                    print(f"\nHighlight section found:")
                    print(highlight_section[:300] + "..." if len(highlight_section) > 300 else highlight_section)
                else:
                    print("\n❌ Highlight section not found either")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template_debug() 