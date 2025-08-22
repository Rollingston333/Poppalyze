#!/usr/bin/env python3

import requests
import re

def test_slider_filter_functionality():
    """Test the new slider filter functionality"""
    
    base_url = "http://localhost:5001"
    
    print("🔍 Testing Slider Filter Functionality")
    print("=" * 50)
    
    # Test 1: Default state (sliders should be OFF by default)
    print("\n1️⃣ Testing Default State:")
    response = requests.get(base_url)
    if response.status_code == 200:
        print("✅ Default page loads successfully")
        
        # Check if sliders are present and in correct state
        if "slider-switch" in response.text:
            print("✅ Slider switches found")
            
            # Check Quick Movers slider state
            if 'id="quick_movers_filter"' in response.text and 'checked' not in response.text:
                print("✅ Quick Movers slider: OFF (Independent)")
            else:
                print("❌ Quick Movers slider state incorrect")
                
            # Check Top Gappers slider state  
            if 'id="top_gappers_filter"' in response.text and 'checked' not in response.text:
                print("✅ Top Gappers slider: OFF (Independent)")
            else:
                print("❌ Top Gappers slider state incorrect")
        else:
            print("❌ Slider switches not found")
    else:
        print(f"❌ Failed to load page: {response.status_code}")
        return
    
    # Test 2: Enable Quick Movers filter
    print("\n2️⃣ Testing Quick Movers Filter ON:")
    response = requests.get(f"{base_url}?quick_movers_independent=false")
    if response.status_code == 200:
        print("✅ Quick Movers filter page loads")
        
        # Check if slider shows as checked
        if 'id="quick_movers_filter" checked' in response.text:
            print("✅ Quick Movers slider: ON (Filtered)")
        else:
            print("❌ Quick Movers slider not checked")
            
        # Check if "Apply Filters" label is present
        if "Apply Filters" in response.text:
            print("✅ 'Apply Filters' label found")
        else:
            print("❌ 'Apply Filters' label not found")
    else:
        print(f"❌ Failed to load Quick Movers filter page: {response.status_code}")
    
    # Test 3: Enable Top Gappers filter
    print("\n3️⃣ Testing Top Gappers Filter ON:")
    response = requests.get(f"{base_url}?top_gappers_independent=false")
    if response.status_code == 200:
        print("✅ Top Gappers filter page loads")
        
        # Check if slider shows as checked
        if 'id="top_gappers_filter" checked' in response.text:
            print("✅ Top Gappers slider: ON (Filtered)")
        else:
            print("❌ Top Gappers slider not checked")
    else:
        print(f"❌ Failed to load Top Gappers filter page: {response.status_code}")
    
    # Test 4: Both filters enabled
    print("\n4️⃣ Testing Both Filters ON:")
    response = requests.get(f"{base_url}?quick_movers_independent=false&top_gappers_independent=false")
    if response.status_code == 200:
        print("✅ Both filters page loads")
        
        # Check both sliders
        if 'id="quick_movers_filter" checked' in response.text and 'id="top_gappers_filter" checked' in response.text:
            print("✅ Both sliders: ON (Filtered)")
        else:
            print("❌ Both sliders not checked")
    else:
        print(f"❌ Failed to load both filters page: {response.status_code}")
    
    # Test 5: Check JavaScript functions
    print("\n5️⃣ Testing JavaScript Functions:")
    response = requests.get(base_url)
    if "toggleQuickMoversFilter()" in response.text:
        print("✅ toggleQuickMoversFilter() function found")
    else:
        print("❌ toggleQuickMoversFilter() function not found")
        
    if "toggleTopGappersFilter()" in response.text:
        print("✅ toggleTopGappersFilter() function found")
    else:
        print("❌ toggleTopGappersFilter() function not found")
    
    # Test 6: Check CSS styles
    print("\n6️⃣ Testing CSS Styles:")
    if ".slider-switch" in response.text:
        print("✅ Slider switch CSS found")
    else:
        print("❌ Slider switch CSS not found")
        
    if ".slider" in response.text:
        print("✅ Slider CSS found")
    else:
        print("❌ Slider CSS not found")

if __name__ == "__main__":
    test_slider_filter_functionality() 