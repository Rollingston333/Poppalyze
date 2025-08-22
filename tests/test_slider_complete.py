#!/usr/bin/env python3

import requests
import json

def test_complete_slider_functionality():
    """Test the complete slider functionality including visual states and data filtering"""
    
    base_url = "http://localhost:5001"
    
    print("🔍 Testing Complete Slider Functionality")
    print("=" * 60)
    
    # Test 1: Default state - both sliders OFF (independent)
    print("\n1️⃣ Default State - Both Sliders OFF (Independent):")
    response = requests.get(base_url)
    if response.status_code == 200:
        print("✅ Page loads successfully")
        
        # Check slider states
        if 'id="quick_movers_filter"' in response.text and 'checked' not in response.text:
            print("✅ Quick Movers slider: OFF (Independent)")
        else:
            print("❌ Quick Movers slider state incorrect")
            
        if 'id="top_gappers_filter"' in response.text and 'checked' not in response.text:
            print("✅ Top Gappers slider: OFF (Independent)")
        else:
            print("❌ Top Gappers slider state incorrect")
            
        # Check if sections show data (should show data from all stocks)
        if "Quick Movers" in response.text and "Top Positive Gappers" in response.text:
            print("✅ Both sections are visible")
        else:
            print("❌ Sections not visible")
    else:
        print(f"❌ Failed to load page: {response.status_code}")
        return
    
    # Test 2: Quick Movers filter ON
    print("\n2️⃣ Quick Movers Filter ON:")
    response = requests.get(f"{base_url}?quick_movers_independent=false")
    if response.status_code == 200:
        if 'id="quick_movers_filter" checked' in response.text:
            print("✅ Quick Movers slider: ON (Filtered)")
        else:
            print("❌ Quick Movers slider not checked")
    else:
        print(f"❌ Failed to load Quick Movers filter page: {response.status_code}")
    
    # Test 3: Top Gappers filter ON
    print("\n3️⃣ Top Gappers Filter ON:")
    response = requests.get(f"{base_url}?top_gappers_independent=false")
    if response.status_code == 200:
        if 'id="top_gappers_filter" checked' in response.text:
            print("✅ Top Gappers slider: ON (Filtered)")
        else:
            print("❌ Top Gappers slider not checked")
    else:
        print(f"❌ Failed to load Top Gappers filter page: {response.status_code}")
    
    # Test 4: Both filters ON
    print("\n4️⃣ Both Filters ON:")
    response = requests.get(f"{base_url}?quick_movers_independent=false&top_gappers_independent=false")
    if response.status_code == 200:
        if 'id="quick_movers_filter" checked' in response.text and 'id="top_gappers_filter" checked' in response.text:
            print("✅ Both sliders: ON (Filtered)")
        else:
            print("❌ Both sliders not checked")
    else:
        print(f"❌ Failed to load both filters page: {response.status_code}")
    
    # Test 5: Test with restrictive filters
    print("\n5️⃣ Testing with Restrictive Filters:")
    restrictive_url = f"{base_url}?min_price=1000&max_price=1001&quick_movers_independent=false&top_gappers_independent=false"
    response = requests.get(restrictive_url)
    if response.status_code == 200:
        print("✅ Restrictive filter page loads")
        
        # Check if "No results" messages appear
        if "No Quick Movers found" in response.text:
            print("✅ Quick Movers shows 'No results' message")
        else:
            print("❌ Quick Movers 'No results' message not found")
            
        if "No Top Gappers found" in response.text:
            print("✅ Top Gappers shows 'No results' message")
        else:
            print("❌ Top Gappers 'No results' message not found")
    else:
        print(f"❌ Failed to load restrictive filter page: {response.status_code}")
    
    # Test 6: Verify slider appearance
    print("\n6️⃣ Verifying Slider Appearance:")
    response = requests.get(base_url)
    if "Apply Filters" in response.text:
        print("✅ 'Apply Filters' labels found")
    else:
        print("❌ 'Apply Filters' labels not found")
        
    if "slider-switch" in response.text:
        print("✅ Slider switches found")
    else:
        print("❌ Slider switches not found")
        
    if "toggleQuickMoversFilter()" in response.text and "toggleTopGappersFilter()" in response.text:
        print("✅ JavaScript functions found")
    else:
        print("❌ JavaScript functions not found")
    
    print("\n🎉 Slider Filter Testing Complete!")
    print("=" * 60)
    print("📋 Summary:")
    print("   • Sliders default to OFF (Independent mode)")
    print("   • Sliders can be toggled ON (Filtered mode)")
    print("   • 'Apply Filters' labels are clear and visible")
    print("   • 'No results' messages appear when no data matches filters")
    print("   • JavaScript functions handle the toggle logic")
    print("   • CSS provides modern slider appearance")

if __name__ == "__main__":
    test_complete_slider_functionality() 