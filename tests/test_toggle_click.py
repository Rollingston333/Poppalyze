#!/usr/bin/env python3

import requests
import re

def test_toggle_click_simulation():
    """Simulate clicking the toggle and verify URL changes"""
    
    base_url = "http://localhost:5001"
    
    print("🔍 Testing Toggle Click Simulation")
    print("=" * 50)
    
    # Get the initial page
    print("\n1️⃣ Initial State:")
    response = requests.get(base_url)
    if response.status_code == 200:
        print("✅ Page loaded successfully")
        
        # Check initial state
        if "Filtered" in response.text:
            print("✅ Initial state: Filtered")
            initial_mode = "filtered"
        elif "Independent" in response.text:
            print("✅ Initial state: Independent")
            initial_mode = "independent"
        else:
            print("❌ Could not determine initial state")
            return
    else:
        print(f"❌ Failed to load page: {response.status_code}")
        return
    
    # Simulate clicking the toggle (switch to opposite mode)
    print(f"\n2️⃣ Simulating Toggle Click (switching from {initial_mode}):")
    
    if initial_mode == "filtered":
        # Switch to independent
        test_url = f"{base_url}?top_gappers_independent=true"
        expected_text = "Independent"
    else:
        # Switch to filtered
        test_url = f"{base_url}?top_gappers_independent=false"
        expected_text = "Filtered"
    
    response = requests.get(test_url)
    if response.status_code == 200:
        print(f"✅ Toggle simulation successful")
        
        # Check if the text changed
        if expected_text in response.text:
            print(f"✅ Toggle shows '{expected_text}' as expected")
        else:
            print(f"❌ Toggle did not show '{expected_text}'")
            
        # Check if the toggle circle has the right class
        if expected_text == "Independent" and "toggle-circle active" in response.text:
            print("✅ Toggle circle has 'active' class")
        elif expected_text == "Filtered" and "toggle-circle" in response.text and "toggle-circle active" not in response.text:
            print("✅ Toggle circle does not have 'active' class")
        else:
            print("❌ Toggle circle class mismatch")
            
    else:
        print(f"❌ Failed to simulate toggle: {response.status_code}")
    
    # Test the actual toggle logic
    print(f"\n3️⃣ Testing Toggle Logic:")
    
    # Test from filtered to independent
    print("   Testing: Filtered → Independent")
    response = requests.get(f"{base_url}?top_gappers_independent=false")
    if response.status_code == 200 and "Independent" in response.text:
        print("   ✅ Filtered → Independent works")
    else:
        print("   ❌ Filtered → Independent failed")
    
    # Test from independent to filtered
    print("   Testing: Independent → Filtered")
    response = requests.get(f"{base_url}?top_gappers_independent=true")
    if response.status_code == 200 and "Filtered" in response.text:
        print("   ✅ Independent → Filtered works")
    else:
        print("   ❌ Independent → Filtered failed")

if __name__ == "__main__":
    test_toggle_click_simulation() 