#!/usr/bin/env python3

import requests
import json

def test_toggle_functionality():
    """Test the toggle functionality for Top Gappers"""
    
    base_url = "http://localhost:5001"
    
    print("🔍 Testing Top Gappers Toggle Functionality")
    print("=" * 50)
    
    # Test 1: Default state (should be Filtered)
    print("\n1️⃣ Testing Default State (Filtered):")
    response = requests.get(base_url)
    if response.status_code == 200:
        print("✅ Default page loads successfully")
        # Check if "Filtered" text appears
        if "Filtered" in response.text and "toggle-circle" in response.text:
            print("✅ Toggle shows 'Filtered' state")
        else:
            print("❌ Toggle state not found")
    else:
        print(f"❌ Failed to load page: {response.status_code}")
    
    # Test 2: Set to Independent
    print("\n2️⃣ Testing Independent State:")
    response = requests.get(f"{base_url}?top_gappers_independent=true")
    if response.status_code == 200:
        print("✅ Independent page loads successfully")
        # Check if "Independent" text appears
        if "Independent" in response.text and "toggle-circle active" in response.text:
            print("✅ Toggle shows 'Independent' state")
        else:
            print("❌ Toggle state not found")
    else:
        print(f"❌ Failed to load page: {response.status_code}")
    
    # Test 3: Set to Filtered explicitly
    print("\n3️⃣ Testing Explicit Filtered State:")
    response = requests.get(f"{base_url}?top_gappers_independent=false")
    if response.status_code == 200:
        print("✅ Filtered page loads successfully")
        # Check if "Filtered" text appears
        if "Filtered" in response.text and "toggle-circle" in response.text and "toggle-circle active" not in response.text:
            print("✅ Toggle shows 'Filtered' state")
        else:
            print("❌ Toggle state not found")
    else:
        print(f"❌ Failed to load page: {response.status_code}")
    
    # Test 4: Check JavaScript function
    print("\n4️⃣ Testing JavaScript Function:")
    response = requests.get(base_url)
    if "toggleTopGappersMode()" in response.text:
        print("✅ JavaScript function found in page")
        
        # Check the function logic
        if "url.searchParams.get('top_gappers_independent')" in response.text:
            print("✅ Function reads URL parameter correctly")
        else:
            print("❌ Function parameter reading issue")
            
        if "url.searchParams.set('top_gappers_independent', 'false')" in response.text:
            print("✅ Function sets parameter correctly")
        else:
            print("❌ Function parameter setting issue")
    else:
        print("❌ JavaScript function not found")

if __name__ == "__main__":
    test_toggle_functionality() 